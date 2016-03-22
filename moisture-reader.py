#!/usr/bin/python2

import binascii
import smbus
import time
import string
import errno

bus = smbus.SMBus(1)

#arduino i2c slave address
slave_address = 0x08

def writeNumber(value):
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
	#print("loop...")
	try:
		#master write causes the arduino to send it's last reading
		writeNumber(1)
		time.sleep(1)
		results = readNumber()
		print(results)
	except KeyboardInterrupt:
		break
	except Exception as e:
		if e.errno == errno.ENXIO:
			print("Cannot find sensor hub, check connection contacts.")
			time.sleep(1)
			continue
		print(e)
		continue