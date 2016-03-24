# psychic-octo-spork
A Python Kafka toolkit intended for transfering serial data from an arduino.

# Weather-Data Requirements:
```
Python 3
Python Kafka : https://kafka-python.readthedocs.org/en/master/install.html
Python Serial
Python asyncio
Python concurrent
```

# Moisture-Data Requirements:
```
Python 2
Python SMBus
Python Kafka : https://kafka-python.readthedocs.org/en/master/install.html
```

# How to configure "systemconfig":
```
kafka_hostname = 'ip or host address'
kafka_port = 'port number'
kafka_connection = kafka_hostname + ":" + kafka_port
system_id = 'any string id like: 0001'

Please note that: developers of this project must add a line with *systemconfig.py*, to the .git/info/exclude file.
```
