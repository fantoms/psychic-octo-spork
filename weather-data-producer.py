#!/usr/bin/python3
import asyncio
import concurrent
import time
import os
from datetime import datetime

print("Starting...")

#import kafka
from kafka import KafkaProducer
from serial import Serial

import systemconfig
#import chipenable

global data_log_buffer, current_log_date, current_log_filename, current_log
global p

#set the values of the current serial port that is connected to the uart line
current_port = "/dev/ttyS0"
#local file name label
data_log_label = "weather_data-"
#timestamp format for the file name
data_log_format = "%Y-%m-%d_%H-%M"
#buffer list object to temporarily log uart messages
data_log_buffer = []
#current date for the file name
current_log_date = datetime.now().date()
#set the local file name
current_log_filename = data_log_label + datetime.now().strftime(data_log_format)
#current_log = open(systemconfig.local_data_dir + current_log_filename, "a+")
current_log = systemconfig.local_data_dir + current_log_filename

#setup kafka
p = KafkaProducer(bootstrap_servers=[systemconfig.kafka_connection])
#serial object to read uart data off of the uart 1 bus 
s = Serial(current_port,'9600',bytesize=8,parity='N',xonxoff=0,rtscts=0,timeout=1)
#pid file path and name
pidFile = '/tmp/'+data_log_label+'.pid'
#indicate current log to screen
print("data log changed: " + current_log)
print("current_log_date: " + str(current_log_date) + "current_log_filename: " + current_log_filename + "current_log: " + current_log + "data_log_buffer: " + str(data_log_buffer))
#writePidFile - function to write the process id to a file
def writePidFile():
	#get the process id from the os and convert it to a string
	pid = str(os.getpid())
	#open pid file
	f = open(pidFile, 'w')
	#write pid string to file
	f.write(pid)
	#close file
	f.close()
#deletePidFile - function to delete the pid file when finished or on error
def deletePidFile():
	if os.path.exists(pidFile):
		os.remove(pidFile)
#buffer_to_file - function to save buffer to loca log file 
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
#rotate_log - function to change the log when the date changes
def rotate_log():
	global data_log_buffer, current_log_date, current_log_filename, current_log
	#check date
	if current_log_date != datetime.now().date():
		buffer_to_file(data_log_buffer, current_log, True)
		print("current_log_date: " + str(current_log_date) + "current_log_filename: " + current_log_filename + "current_log: " + current_log + "data_log_buffer: " + str(data_log_buffer))
		current_log_date = datetime.now().date()
		current_log_filename = data_log_label + datetime.now().strftime(data_log_format)
		current_log = systemconfig.local_data_dir + current_log_filename
		print("data log changed: " + current_log)
		print("current_log_date: " + str(current_log_date) + "current_log_filename: " + current_log_filename + "current_log: " + current_log + "data_log_buffer: " + str(data_log_buffer))
	else:
		buffer_to_file(data_log_buffer, current_log)
#SerialReader - function to read data off of the uart bus
#requires permissions set on the user to access the bus
def SerialReader():
	global p
	#check the serial line is available for reading
	if s.readable():
		#capture a string terminated by a new line
		serialData = s.readline()
		#grab the current time
		ts = time.time()
		#discard the message if the length is less than 2
		if len(serialData) > 2:
			#data is good, lets output
			#creat a timestamp for the current message and prepend to the message
			stamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
			message = stamp + ' $'  + serialData.decode('UTF-8').rstrip('\r\n') + '#'
			#debug: print(message)
			print(message)
			#save message to the buffer
			data_log_buffer.append(message)
			#send the message to the producer
			p.send("weather-test",message.encode('UTF-8'))
		#attempt to rotate the log if needed
		rotate_log()
#create an async loop object that drives the entire app
loop = asyncio.get_event_loop()
#add the serial function to the event handler
loop.add_reader(s.fileno(), SerialReader)
#call the function to write the process id to file
writePidFile()
#begin the main loop
try:
	loop.run_forever()
#on ctrl+c key press grab the exception
except KeyboardInterrupt:
	#close the serial line
	s.close()
	#save the current buffer to local file
	buffer_to_file(data_log_buffer, current_log, True)
	#delete the pid file
	deletePidFile()
	#end the main loop
	loop.close()
#capture any errors and attempt to send them to the kafka topic
except Exception as e:
	buffer_to_file(data_log_buffer, current_log, True)
	print(str(datetime.now()) + str(e))
	if not p._closed:
		message = systemconfig.system_id + ': ' + str(datetime.now()) + " " + str(e)
		p.send('weather-error',message.encode('UTF-8'))
finally:
	#delete the pid file
	deletePidFile()
	#end the main loop
	loop.close()
