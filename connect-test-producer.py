#!/usr/bin/python3
from kafka import KafkaProducer
import ustconfig
k = KafkaProducer(bootstrap_servers=[ustconfig.kafka_connection])

kMessage = "Testing"

k.send("connect-test",kMessage.encode("UTF-8"))
