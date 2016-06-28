#!/usr/bin/python
from kafka import KafkaConsumer
import systemconfig

#the latency on the moisture data and battery may be a bit too high
c = KafkaConsumer("moisture-data",bootstrap_servers=[systemconfig.kafka_connection])
c2 = KafkaConsumer("moisture-battery",bootstrap_servers=[systemconfig.kafka_connection])
c3 = KafkaConsumer("weather-test",bootstrap_servers=[systemconfig.kafka_connection])
c4 = KafkaConsumer("reconnect-i2c",bootstrap_servers=[systemconfig.kafka_connection])
c5 = KafkaConsumer("moisture-error",bootstrap_servers=[systemconfig.kafka_connection])

while True:
	for message in c:
		# message value and key are raw bytes -- decode if necessary!
		# e.g., for unicode: `message.value.decode('utf-8')`
		print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
		break
	for message in c2:
		# message value and key are raw bytes -- decode if necessary!
		# e.g., for unicode: `message.value.decode('utf-8')`
		print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
		break
	for message in c3:
		# message value and key are raw bytes -- decode if necessary!
		# e.g., for unicode: `message.value.decode('utf-8')`
		print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
		break
	for message in c4:
		# message value and key are raw bytes -- decode if necessary!
		# e.g., for unicode: `message.value.decode('utf-8')`
		print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
		break
	for message in c5:
		# message value and key are raw bytes -- decode if necessary!
		# e.g., for unicode: `message.value.decode('utf-8')`
		print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
		break

