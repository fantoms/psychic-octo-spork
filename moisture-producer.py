#!/usr/bin/python2

import binascii
import smbus
import time
import string
import errno
import subprocess

from datetime import datetime

from kafka import KafkaProducer

import systemconfig

bus = smbus.SMBus(1)
moisture_topic = "moisture-data"
battery_topic = "moisture-battery"
battery_command = "battery2.sh"

try:
	p = KafkaProducer(bootstrap_servers=[systemconfig.kafka_connection])
except Exception as e:
	print(e)
	exit()

#arduino i2c slave address
slave_address = 0x08

def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

def writeNumber(value):
	#print("Writing...")
	for character in str(value):
		bus.write_byte(slave_address, int(character))
	return -1

def readNumber():
	#print("Reading...")
	byte_list = bus.read_i2c_block_data(slave_address, 1)	
	if len(byte_list) > 0:
		while 255 in byte_list:
			byte_list.remove(255)
		while 0 in byte_list:
			byte_list.remove(0)
		number = "".join([chr(byte) for byte in byte_list])
	return number

while True:
	#print("Looping...")
	try:
		#master write causes the arduino to send it's last reading
		writeNumber(1)
		time.sleep(1)
		results = readNumber()
		ts = time.time()
		stamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		message = stamp + ' '  + results + ''
		print(message)
		p.send(moisture_topic,message.encode('UTF-8'))
		#reset results
		battery_info = ''
		for line in run_command(battery_command):
			line.rstrip('\r\n')
			if "Charging" in line:
				battery_info += line.rstrip('\r\n')
			if "Fuel" in line:
				battery_info += line.rstrip('\r\n')
			if "current" in line:
				battery_info += line.rstrip('\r\n')
		message = stamp + ' '  + battery_info + ''
		print(message)
		p.send(battery_topic,message.encode('UTF-8'))
	except KeyboardInterrupt:
		break
	except Exception as e:
		print(e)
		if not p._closed:
			p.send('moisture-error',str(e).encode('UTF-8'))
		if e.errno == errno.ENXIO:
			print("Cannot find sensor hub, check connection contacts.")
			if not p._closed:
				p.send('reconnect-i2c', str(datetime.now()).encode('UTF-8'))
			time.sleep(1)
			continue
		continue
