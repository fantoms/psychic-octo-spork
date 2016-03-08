#!/usr/bin/python3
from kafka import KafkaConsumer
import ustconfig
from datetime import datetime
import time

c = KafkaConsumer("heartbeat-monitor",bootstrap_servers=[ustconfig.kafka_connection])

last_heartbeat = datetime.now()
current_time = datetime.now()

while True:
	current_time = datetime.now()
	print(current_time - last_heartbeat)
	for message in c:
		# message value and key are raw bytes -- decode if necessary!
		# e.g., for unicode: `message.value.decode('utf-8')`
		if len(message.value) > 0:
			last_heartbeat = datetime.now()	
			print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
			print (last_heartbeat)
		else:
			print("Empty message")
