#!/usr/bin/env python

import serial
from TX2i import TX2i
from time import sleep

payloadStatus = True

payload = TX2i.TX2i("/dev/ttyO1")
statResponse = payload.init()

if not statResponse:
	sleep(5)
	statResponse = payload.init()

if "0" in statResponse or (not statResponse):
	payloadStatus = False

print("Status: " + str(payloadStatus))


sleep(10)

#Start
stat = payload.start()
print("Start " + str(stat))

sleep(30)

stat = payload.stop()
print("Stop " + str(stat))
