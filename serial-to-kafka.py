#!/usr/bin/python3
import asyncio
import concurrent
import time, datetime
#import kafka
from kafka import KafkaProducer
from serial import Serial

import ustconfig

print("Starting...")

current_port = "/dev/ttyS0"
global p
#setup kafka
p = KafkaProducer(bootstrap_servers=[ustconfig.kafka_connection])

s = Serial(current_port,'9600',bytesize=8,parity='N',xonxoff=0,rtscts=0,timeout=1)
#to add a serial write function, you can use a buffer or rewrite the callback
#buffer = ""

def SerialReader():
	global p
	if s.readable():
		serialData = s.readline()
		#s.write(buffer)
		ts = time.time()
		if len(serialData) > 2:
			#data is good, lets output
			print(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') + ' $'  + serialData.decode('UTF-8').rstrip('\r\n') + '#')
			p.send("weather-test",serialData)


loop = asyncio.get_event_loop()
loop.add_reader(s.fileno(), SerialReader)

try:
	loop.run_forever()
except KeyboardInterrupt:
	s.close()
	loop.close()
finally:
	loop.close()
