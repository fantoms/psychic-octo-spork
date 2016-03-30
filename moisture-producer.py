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
timestamp_format = "%Y-%m-%d %H:%M:%S.%f"

try:
	p = KafkaProducer(bootstrap_servers=[systemconfig.kafka_connection])
except Exception as e:
	print(e)
	exit()

#arduino i2c slave address
slave_address = 0x08

data_log_label = "moisture_data-"
data_log_format = "%Y-%m-%d-%H_%M"
data_log_buffer = []


#string current_log_date_str = datetime.now().strftime(data_log_format)
current_log_date = datetime.now().date()
current_log_filename = data_log_label + datetime.now().strftime(data_log_format)
#current_log = open(systemconfig.local_data_dir + current_log_filename, "a+")
current_log = systemconfig.local_data_dir + current_log_filename


def rotate_log(current_log_date, current_log_filename, current_log, data_log_buffer):
	#check date
	if current_log_date != datetime.now().date():
		buffer_to_file(data_log_buffer, current_log, True)
		print("current_log_date: "+ current_log_date + "current_log_filename: " +current_log_filename +"current_log: " +current_log + "data_log_buffer: " + data_log_buffer)
		current_log_date = datetime.now().date()
		current_log_filename = data_log_label + datetime.now().strftime(data_log_format)
		current_log = systemconfig.local_data_dir + current_log_filename
		print("data log changed: " + current_log)
		print("current_log_date: "+ current_log_date + "current_log_filename: " +current_log_filename +"current_log: " +current_log + "data_log_buffer: " + data_log_buffer)
	else:
		buffer_to_file(data_log_buffer, current_log)

def buffer_to_file(buffer, data_log, save_now = False):
	#if buffer element count is greater then buffer limit
	if len(buffer) > 31 or save_now:
		#write each element to current local data log
		current_log = open(data_log, "a+")
		for message in buffer:
			current_log.write(message + '\n')
		current_log.close()
		#flush buffer
		buffer[:] = []

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

print("The application has begun processing messages...")

while True:
	#print("Looping...")
	if p._closed:
		print("Waiting for kafka...")
	try:
		#master write causes the arduino to send it's last reading
		writeNumber(1)
		time.sleep(.2)
		results = readNumber()
		ts = time.time()
		stamp = datetime.fromtimestamp(ts).strftime(timestamp_format)
		message = stamp + ' '  + results + ''
		#print(message)
		p.send(moisture_topic,message.encode('UTF-8'))
		data_log_buffer.append(message)
		#current_log.write(message + '\n')
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
			if "voltage" in line:
				battery_info += line.rstrip('\r\n')
			if "temp" in line:
				battery_info += line.rstrip('\r\n')
		message = systemconfig.system_id + ': ' + stamp + ' '  + battery_info + ''
		#data_log_buffer.append(message)
		#print(message)
		p.send(battery_topic,message.encode('UTF-8'))
		#add timeout logic here:
		rotate_log(current_log_date, current_log_filename, current_log, data_log_buffer)
	except KeyboardInterrupt:
		buffer_to_file(data_log_buffer, current_log, True)
		break
	except Exception as e:
		buffer_to_file(data_log_buffer, current_log, True)
		print(str(datetime.now()) + str(e))
		if not p._closed:
			message = systemconfig.system_id + ': ' + str(datetime.now()) + " " + str(e)
			p.send('moisture-error',message.encode('UTF-8'))
		if hasattr(e, 'errno'):
			if e.errno == errno.ENXIO:
				print("Cannot find sensor hub, check connection contacts.")
				if not p._closed:
					message = '$' + systemconfig.system_id + ': ' + str(datetime.now()) + '#'
					p.send('reconnect-i2c', message.encode('UTF-8'))
				time.sleep(1)
				continue
		continue
