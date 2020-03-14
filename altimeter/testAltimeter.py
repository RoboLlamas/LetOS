#!/usr/bin/env python

from letsatAltimeter import letsatAltimeter
from time import sleep
from random import seed
from random import randint

POP_ALTITUDE = 1500
CAPTURE_ALTITUDE = 1000

seed(1)
def pollData(altitude, falling):
	data = []
	if not falling:
		altitude = altitude + 30
	else:
		altitude = altitude - 30
	data.append(22)
	data.append(103006)
	data.append(altitude)
	data.append(102506)
	return data

def randomStatus():
	x = randint(0,1)
	if x == 1:
		return True
	elif x == 0:
		return False

#response = raw_input("Altimeter working? y/n\n")
#if response == 'y':
#	altStatus = True
#elif response == 'n':
#	altStatus = False
#else:
#	print("Error")
#	exit()
altStatus = randomStatus()
payloadPower = False
falling = False

#altimeter = None
#try:
#	altimeter = letsatAltimeter(2, 500, 102506)
#	if (not altimeter.verify)
#		print("Could not verify altimeter")
#		altStatus = False
#except Exception as e:
#	print("Altimeter init " + str(e))
#	alStatus = False

print("Altimeter Status: " + str(altStatus))
print("Payload Power: " + str(payloadPower))
print("Falling: " + str(falling))

currentAlt = 500
altitude = 0
timeout = 0
while(True):
	try:
		counter = 0
		messagePoll = ""
		sensorData = None
		altStatus = randomStatus()
		while(counter < 5):
			counter += 1
			messagePoll = ""
			#altStatus = randomStatus()
			sensorData = pollData(currentAlt, falling)
			for m in sensorData:
				messagePoll = messagePoll + str(m) + ","
			messagePoll = messagePoll[:-1]
			print(messagePoll)
			#print(str(altStatus))
			currentAlt = sensorData[2]
			if altStatus:
				altitude = currentAlt
			else:
				altitude = 0

			sleep(.25)


		print(str(altStatus))
		timeout = timeout + 1
		#if altimeter is not working... timeout
		if ((not payloadPower) and (not falling) and (timeout >= 5)):
			print("Timeout Start payload")
			payloadPower = True
			print("Payload Power: " + str(payloadPower))
			print("Falling: " + str(falling))
			#reset timeout
			timeout = 0

		if(payloadPower and (timeout >= 3)):
			print("Timeout Stop payload")
			payloadPower = False
			falling = True
			print("Payload Power: " + str(payloadPower))
			print("Falling: " + str(falling))
			#reset timeout
			timeout = 0
		if((not payloadPower) and falling and (timeout >= 8)):
			print("Timeout landed")
			exit()


		#if altimeter is working
		if ((not payloadPower) and (altitude >= CAPTURE_ALTITUDE) and (not falling)):
			print("Start payload")
			payloadPower = True
			print("Payload Power: " + str(payloadPower))
			print("Falling: " + str(falling))
			timeout = 0

		if (payloadPower and (altitude >= POP_ALTITUDE)):
			print("Stop payload")
			payloadPower = False
			falling = True
			print("Payload Power: " + str(payloadPower))
			print("Falling: " + str(falling))
			timeout = 0

		if (altStatus and (not payloadPower) and (altitude <= 500) and falling):
			print("Landed")
			exit()

		print("Transmit message")
		counter = 0

	except Exception as e:
		print(str(e))
		exit()
