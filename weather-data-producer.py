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

current_port = "/dev/ttyS0"
data_log_label = "weather_data-"
data_log_format = "%Y-%m-%d_%H-%M"
data_log_buffer = []

#string current_log_date_str = datetime.now().strftime(data_log_format)
current_log_date = datetime.now().date()
current_log_filename = data_log_label + datetime.now().strftime(data_log_format)
#current_log = open(systemconfig.local_data_dir + current_log_filename, "a+")
current_log = systemconfig.local_data_dir + current_log_filename

#setup kafka
p = KafkaProducer(bootstrap_servers=[systemconfig.kafka_connection])
s = Serial(current_port,'9600',bytesize=8,parity='N',xonxoff=0,rtscts=0,timeout=1)

print("data log changed: " + current_log)
print("current_log_date: " + str(current_log_date) + "current_log_filename: " + current_log_filename + "current_log: " + current_log + "data_log_buffer: " + str(data_log_buffer))

def writePidFile():
	pid = str(os.getpid())
	f = open('/tmp/'+data_log_label+'pid', 'w')
	f.write(pid)
	f.close()

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

def SerialReader():
	global p
	if s.readable():
		serialData = s.readline()
		#s.write(buffer)
		ts = time.time()
		if len(serialData) > 2:
			#data is good, lets output
			stamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
			message = stamp + ' $'  + serialData.decode('UTF-8').rstrip('\r\n') + '#'
			#debug: print(message)
			print(message)
			data_log_buffer.append(message)
			p.send("weather-test",message.encode('UTF-8'))
		rotate_log()

loop = asyncio.get_event_loop()
loop.add_reader(s.fileno(), SerialReader)
writePidFile()

try:
	loop.run_forever()
except KeyboardInterrupt:
	s.close()
	buffer_to_file(data_log_buffer, current_log, True)
	loop.close()
except Exception as e:
	buffer_to_file(data_log_buffer, current_log, True)
	print(str(datetime.now()) + str(e))
	if not p._closed:
		message = systemconfig.system_id + ': ' + str(datetime.now()) + " " + str(e)
		p.send('weather-error',message.encode('UTF-8'))
finally:
#	chipenable.gpio.output("XIO-P0", chipenable.GPIO.HIGH)
#	chipenable.gpio.cleanup()
	loop.close()
