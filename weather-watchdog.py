#!/usr/bin/python3
import sys
import os
import errno

def RunSensorScript():
	import subprocess
#	sensorScript = '/home/chip/psychic-octo-spork/weather-data-producer.py'
	sensorScript = '/home/chip/launch-tmux-weather.sh'
#	subprocess.Popen([sys.executable, sensorScript], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	subprocess.Popen([sensorScript], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

data_log_label = "weather_data-"

pidFile = '/tmp/' + data_log_label + '.pid'

if os.path.exists(pidFile):
	f = open(pidFile)
	processId = int(f.read())
else:
	print("Not running")
	RunSensorScript()
	exit()

try:
	os.kill(processId, 0)
except OSError as err:
	if err.errno == errno.ESRCH:
		print("Not running")
		RunSensorScript()
	elif err.errno == errno.EPERM:
		print("No permission to signal this process!")
	else:
		print("Unknown error")
#else:
#    print "Running"
#
# this is not needed unless you need to debug
