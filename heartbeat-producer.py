#!/usr/bin/python3
from kafka import KafkaProducer
import ustconfig
k = KafkaProducer(bootstrap_servers=[ustconfig.kafka_connection])
import time

kMessage = "Alive!"
counter = 0

while True:
	#k.send("heartbeat-monitor",kMessage.encode("UTF-8"))
	k.send("heartbeat-monitor",str(counter).encode("UTF-8"))
	time.sleep(0.2)
	counter = counter + 1
