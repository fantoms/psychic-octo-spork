#!/usr/bin/python3
from kafka import KafkaProducer
import ustconfig
k = KafkaProducer(bootstrap_servers=[ustconfig.kafka_connection])
import time

kMessage = "Alive!"

while True:
	k.send("heartbeat-monitor",kMessage.encode("UTF-8"))
	time.sleep(0.2)
