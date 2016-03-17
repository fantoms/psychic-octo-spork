#!/usr/bin/python3
from kafka import KafkaProducer
import systemconfig
k = KafkaProducer(bootstrap_servers=[systemconfig.kafka_connection])
import time
from datetime import datetime

kMessage = "Alive!"
counter = 0

while True:
	#k.send("heartbeat-monitor",kMessage.encode("UTF-8"))
	dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	k.send("heartbeat-monitor",str(str(counter) + " " + dt).encode("UTF-8"))
	time.sleep(0.2)
	counter = counter + 1
