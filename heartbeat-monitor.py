#!/usr/bin/python3
from kafka import KafkaConsumer
import systemconfig
from datetime import datetime
import time

c = KafkaConsumer("heartbeat-monitor",bootstrap_servers=[systemconfig.kafka_connection])

last_heartbeat = datetime.now()
current_time = datetime.now()

while True:
	for message in c:
		dir(c)
		# message value and key are raw bytes -- decode if necessary!
		# e.g., for unicode: `message.value.decode('utf-8')`
		current_time = datetime.now()
		print(current_time - last_heartbeat)
		if len(message.value) > 0:
			last_heartbeat = datetime.now()	
			print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
			print (last_heartbeat)
		else:
			print("Empty message")
	print("done")
