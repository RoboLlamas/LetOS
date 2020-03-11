#!/usr/bin/env python

"""
Main script for LetOS flight software
"""
#<><><><> write script to install all necessary dependencies
#<><><><> change the imports after ready to push
import serial
import gps
from LetOS.MPU6050 import MPU6050
from accelerometer import setupAccelerometer
import smbus
from LetOS import rockBlock
from RockBlock import letsatRockBlock
from RockBlock.rockBlock import rockBlockException
from altimeter import letsatAltimeter
from TX2i import TX2i
from time import sleep
import logging

#<><><><>
POP_ALTITUDE = 100
CAPTURE_ALTITUDE = 50

"""
(1) Setup logging
"""
logger = logging.getLogger("DataLog")
logger.setLevel('INFO')
formatter = logging.Formatter('%(asctime)s, %(message)s')
logFile = 'testLog.csv'
handler = logging.FileHandler(logFile)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)


def pollData(gps, accel, alt):
	data = []

	try:
		if (not gps.update()):
			raise IOError("No GPS")
		data.append(gps.latlong)
		data.append(gps.time)
		data.append(gps.course)
		data.append(gps.speed)
	except (IOError):
		#gps IOError
		#set the data to all 0'
		for i in range(0, 4):
			data.append(0)
		logger.error("GPS IO Error")

        try:
		if (accel is None):
			raise IOError("No accelerometer")
		data.append(accel.get_accel_data())
		data.append(accel.get_gyro_data())
		data.append(accel.get_temp())
	except (IOError):
		#accelerometer IOError
		#set data to all 0's
		for i in range(0,3):
			data.append(0)
		logger.error("Acceleromter IO Error")

	try:
		if (alt is None):
			raise IOError("No altimeter")
		data.append(alt.get_temp())
		data.append(alt.get_pressure())
		data.append(alt.get_altitude())
		data.append(alt.get_sealevel())
	except (IOError):
		#Altimeter IOError
		#set data to all 0's
		for i in range(0,4):
			data.append(0)
		logger.error("Altimeter IO Error")

	return data



"""
(2) Perform status checks of all sensors
"""

gpsStatus = False
accelStatus = True
rbStatus = True
altStatus = True
payloadStatus = True
payloadPower = False
falling = False

#<><><><> retry if get errors???? or just transmit failure???

#gps
#/dev/ttyO4
gps.init(4)
#loop until get fix
gpsValue = 0
#timeoutCount = 300
timeoutCount = 2
while((gpsValue == 0) and (timeoutCount > 0)):
	gpsValue = gps.update()
	sleep(1)
	timeoutCount = timeoutCount - 1

#no execution if fails
if(gpsValue is not False):
	#success
	gpsStatus = True
else:
	print("Error with GPS")

#accelerometer
#address 0x68, i2c bus 1
accelerometer = None
try:
	accelerometer = MPU6050(0x68, 1)
	#apply hardcoded offsets
	accelSatus = setupAccelerometer(accelerometer)
except:
	#error in MPU6050 init
	print("Error with accel")
	accelStatus = False

#<><><><><>
#thermocouple

#altimeter
#i2c-2 port. Known altitude 111m, sea level pressure 102472 pa
altimeter = None
try:
	altimeter = letsatAltimeter(2, 111, 102472)
	if (not altimeter.verify):
		altStatus = False

except:
	print("Error with altimeter")
	altStatus = False



#TX2i
payload = TX2i.TX2i("/dev/ttyO1")
statResponse = None
#statResponse = payload.init()
if ((statResponse == 0) or (statResponse is None)):
	payloadStatus = False
	print("Error with TX2i")

#RockBlock
rb = None
try:
	rb = letsatRockBlock("/dev/tty02")
	rb.stateOfHealth()

#<><><><> if rbStatus false, try again??? blink some LEDS????
	signal = rb.signalStrength()
	if(rbStatus and signal > 0):
		#transmit OK and signal
		#make a byte message with statuses of each as 0 or 1
		message = gpsStatus + "," + accelStatus + "," + altStatus + "," + payloadStatus
		okMessage = "ER"
		if(gpsStaus and accelStaus and altStatus and payloadStatus):
			okMessage = "OK"
		message = message + okMessage + str(signal)
		success = rb.sendMessage(message.encode())
except:
        rbStatus = False
#if rbStatus false, output red color to debug LED

stats = (int(gpsStatus), int(accelStatus), int(altStatus), int(payloadStatus), int(rbStatus))
logger.info('%d, %d, %d, %d, %d' % stats)


print("GPS status: " + str(gpsStatus))
print("Accelerometer status: " + str(accelStatus))
print("Altimeter status: " + str(altStatus))
print("Payload status: " + str(payloadStatus))
print("RB Status: " + str(rbStatus))


"""
(3) Get initial data from sensors
Send all data for initial transmit
"""

try:
	#<><><><> what will be max size of these??
	initData = pollData(gps, accelerometer, altimeter)
	print("Polling Data")
	#send to rb
	initMessage = ""
	for m in initData:
		initMessage = initMessage + str(m) + ","
	if (rb is None):
		raise rockBlockException("No RB")
	else:
		rb.sendMessage(initMessage.encode())
	logger.info(initMessage)

except (rockBlockException):
	logger.error("Failure to transmit")
except Exception as e :
        #<><><><> What to log/do if fails to get data
	print(str(e))
	logger.error("Failure to initialize")
	rb.sendMessage("ER")


"""
(4) Polling sensors at 1 Hz
"""
#put in loop. Sleep(~1sec) after polling/logging
#Setup counter. Counts to 60
#transmits at 60. Resets.
#<><><><>sleep or just loop?? allow to be broken?
#put try catch block inside While loop so it will continue after exception caught
#needs to conintue logging other working sensors though...
while(True):
	try:
		counter = 0
		messagePoll = ""
		sensorData = None
		while(counter < 60):
			counter += 1
			messagePoll = ""
			sensorData = pollData(gps, accelerometer, altimeter)
			for m in sensorData:
				messagePoll = messagePoll + str(m) + ","

			logger.info(messagePoll)
			#<><><><> sleep for 1 second. How accurate does this need to be??
			sleep(1)

		#<><><><>check for capture altitude
		if ((not payloadPower) and (sensorData[9] >= CAPTURE_ALTITUDE) and (not falling)):
			stat = payload.start()
			if (stat != 0):
				payloadPower = True

		#><><><><>check for burst altitude and/or?? acceleration
		if (payloadPower and (sensorData[9] >= POP_ALTITUDE)):
			stat = payload.stop()
			if (stat != 0):
				payloadPower = False
				falling = True

		#<><><> add timeout in case altimeter breaks or something
		#after breaking out of loop
		rb.sendMessage(messagePoll.encode())
		counter = 0

	except (IOError):
		logger.error("RB IO Error")
		continue
	except (KeyboardInterrupt):
		handlers = logger.handlers[:]
		for h in handlers:
			h.close()
			logger.removeHandler(h)
		exit()

	except Exception as e:
		print(str(e))
		logger.error("RB Error")
		continue

