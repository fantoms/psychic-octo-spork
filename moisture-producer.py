#!/usr/bin/python2
#import base library
import binascii
import smbus
import time
import string
import errno
import subprocess
#import the datetime object
from datetime import datetime
#import kafka producer object
from kafka import KafkaProducer
#import systemconfig
import systemconfig
#create the i2c bus object
bus = smbus.SMBus(1)
#kafka moisture topic to send messages to
moisture_topic = "moisture-data"
#kafka battery topic to send messages to
battery_topic = "moisture-battery"
#external command to view battery info
battery_command = "battery2.sh"
#timestamp formatting for date
timestamp_format = "%Y-%m-%d %H:%M:%S.%f"

#create the kafka producer object and capture errors
try:
	p = KafkaProducer(bootstrap_servers=[systemconfig.kafka_connection])
except Exception as e:
	print(e)
	exit()

#arduino i2c slave address
slave_address = 0x08
#global assignments for python functions
global data_log_buffer, current_log_date, current_log_filename, current_log
#data label for file local name
data_log_label = "moisture_data-"
#timestamp format for local log file
data_log_format = "%Y-%m-%d_%H-%M"
#list object to buffer data temporarily
data_log_buffer = []
#current date for local file name
current_log_date = datetime.now().date()
#local filename based on the label + date
current_log_filename = data_log_label + datetime.now().strftime(data_log_format)
#file path and file name in a single string
current_log = systemconfig.local_data_dir + current_log_filename

#rotate_log - function to change logs when the dates day changes
def rotate_log():
	global data_log_buffer, current_log_date, current_log_filename, current_log
	#check if the current date is not the same as the previous date
	if current_log_date != datetime.now().date():
		#save the last line to the current local file and save the current buffer
		buffer_to_file(data_log_buffer, current_log, True)
		#print yesterdays local file to screen. helps to indicate progress
		print("current_log_date: " + str(current_log_date) + "current_log_filename: " + current_log_filename + "current_log: " + current_log + "data_log_buffer: " + str(data_log_buffer))
		#change the log to the new date and print new log
		current_log_date = datetime.now().date()
		current_log_filename = data_log_label + datetime.now().strftime(data_log_format)
		current_log = systemconfig.local_data_dir + current_log_filename
		print("data log changed: " + current_log)
		print("current_log_date: " + str(current_log_date) + "current_log_filename: " + current_log_filename + "current_log: " + current_log + "data_log_buffer: " + str(data_log_buffer))
	else:
		#buffer message to save on disk writes?
		buffer_to_file(data_log_buffer, current_log)

#buffer_to_file - function to store local messages temporarily
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

#run_command - function to run external programs like battery2.sh
def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')
#writeNumer - function to write a value over the i2c bus
def writeNumber(value):
	#print("Writing...")
	for character in str(value):
		bus.write_byte(slave_address, int(character))
	return -1
#readNumber - function to read a block off of the i2c bus
def readNumber():
	#print("Reading...")
	byte_list = bus.read_i2c_block_data(slave_address, 1)	
	if len(byte_list) > 0:
		#strip 255 and 0
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
		#wait for bus to send and collect the string
		time.sleep(.2)
		results = readNumber()
		#create a timestamp for the message and prepend
		ts = time.time()
		stamp = datetime.fromtimestamp(ts).strftime(timestamp_format)
		message = stamp + ' '  + results + ''
		#print(message)
		#send the message to the kafka topic over the producer object
		p.send(moisture_topic,message.encode('UTF-8'))
		#buffer message
		data_log_buffer.append(message)
		#reset results and collect battery info from ecternal battery2.sh
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
		#create a message to send to the kafka battery topic
		message = systemconfig.system_id + ': ' + stamp + ' '  + battery_info + ''
		#data_log_buffer.append(message)
		#print(message)
		p.send(battery_topic,message.encode('UTF-8'))
		#rotate the log if needed
		rotate_log()
	#catch exceptions
	#if ctrl+c is pressed
	except KeyboardInterrupt:
		#save current buffer to local file and end
		buffer_to_file(data_log_buffer, current_log, True)
		break
	#all other errors
	except Exception as e:
		#save current buffer to local file
		buffer_to_file(data_log_buffer, current_log, True)
		#print the error to the screen
		print(str(datetime.now()) + str(e))
		#check if the producer is closed and send the error to the error topic
		if not p._closed:
			message = systemconfig.system_id + ': ' + str(datetime.now()) + " " + str(e)
			p.send('moisture-error',message.encode('UTF-8'))
		if hasattr(e, 'errno'):
			#if there is a connection error with the i2c bus warn
			if e.errno == errno.ENXIO:
				print("Cannot find sensor hub, check connection contacts.")
				if not p._closed:
					message = '$' + systemconfig.system_id + ': ' + str(datetime.now()) + '#'
					p.send('reconnect-i2c', message.encode('UTF-8'))
				time.sleep(1)
				continue
		continue
