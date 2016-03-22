#!/usr/bin/python3
from kafka import KafkaConsumer
import systemconfig

c = KafkaConsumer("weather-test",bootstrap_servers=[systemconfig.kafka_connection])

while True:
	for message in c:
		# message value and key are raw bytes -- decode if necessary!
		# e.g., for unicode: `message.value.decode('utf-8')`
		print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))

