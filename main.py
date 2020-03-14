#!/usr/bin/env python

"""
Main script for LetOS flight software
"""
#<><><><> write script to install all necessary dependencies
import serial
import gps
from accelerometer import MPU6050
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


#<><><> round some numbers
"""
pollData, Private
Summary: gets data from gps, accelerometer, and altimeter and stores in array
Params: gps object, accelerometer object, altimeter object
Returns: the array of length 11
Exceptions: Catches IOErrors and other exceptions  and sets values for that sensor to 0
"""
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
		print("GPS IO Error")
	except Exception as e:
		for i in range(0, 4):
			data.appen(0)
		logger.error("GPS " + str(e))
		print("GPS " + str(e))

        try:
		#<><><><><> change MPU6050 so returns x, y, z seperately??
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
		print("Accelerometer IO Error")
	except Exception as e:
		for i in range(0,3):
			data.append(0)
		logger.error("Accelerometer " + str(e))
		print("Accelerometer " + str(e))

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
		print("altimeter IO Error")
	except Exception as e:
		for i in range(0,4):
			data.apppend(0)
		logger.error("Altimeter " + str(e))
		print("Altimeter " + str(e))

	return data



"""
(2) Perform status checks of all sensors
"""

#sensor statuses initial setting
gpsStatus = False
accelStatus = True
rbStatus = True
altStatus = True
payloadStatus = True
payloadPower = False
falling = False

#gps
#/dev/ttyO4
gps.init(4)
#loop until get fix
gpsValue = 0
#timeoutCount = 300
timeoutCount = 2
while((gpsValue == 0) and (timeoutCount > 0)):
	#try to update again
	gpsValue = gps.update()
	sleep(1)
	timeoutCount = timeoutCount - 1

if(gpsValue is not False):
	#success
	gpsStatus = True
else:
	#log any errors
	print("GPS init error")
	logger.error("GPS init error")

#accelerometer
#address 0x68, i2c bus 1
accelerometer = None
try:
	accelerometer = MPU6050.MPU6050(0x68, 1)
	#apply hardcoded offsets
	accelSatus = setupAccelerometer.setupAccelerometer(accelerometer)
except Exception as e:
	#error in MPU6050 init
	print("Accelerometer init " + str(e))
	logger.error("Accelerometer init " + str(e))
	accelStatus = False

#<><><><><>
#thermocouple

#altimeter
#i2c-2 port. Set known altitude and sea level pressure
altimeter = None
try:
	altimeter = letsatAltimeter.letsatAltimeter(2, 111, 101020)
	if (not altimeter.verify):
		print("Could not verify altimeter")
		logger.error("Could not verify altimeter")
		altStatus = False

except Exception as e:
	print("Altimeter init " + str(e))
	logger.error("Altimeter init " + str(e))
	altStatus = False



#TX2i
payload = TX2i.TX2i("/dev/ttyO1")
statResponse = payload.init()
if not statResponse:
	#no response: sleep and try again
	sleep(5)
	statResponse = payload.init()

#If 0, then error has occured or couldn't get response
if "0" in statResponse or (not statResponse):
	payloadStatus = False
	print("TX2i init " + str(statResponse))
	logger.error("TX2i init " + str(statResponse))


#RockBlock
stats = (int(gpsStatus), int(accelStatus), int(altStatus), int(payloadStatus))
rb = None
try:
	rb = letsatRockBlock.letsatRockBlock("/dev/ttyO2")
	rbStatus = rb.stateOfHealth()

	stats = stats + (int(rbStatus),)
#<><><><> if rbStatus false, try again??? blink some LEDS????
	signal = rb.signalStrength()
	count = 3
	#try a couple times to get good signal
	if ((signal == 0) and (count > 0)):
		signal = rb.signalStrength()
		sleep(1)
		count = count - 1

	print("Signal: " + str(signal))

	message = ""
	if((rbStatus) and (int(signal) > 0)):
		#transmit OK and signal
		for x in stats:
			message = message + str(x) + ","
		#make a byte message with statuses of each as 0 or 1
		#message = gpsStatus + "," + accelStatus + "," + altStatus + "," + payloadStatus
		okMessage = "ER"
		if(gpsStatus and accelStatus and altStatus and payloadStatus):
			okMessage = "OK"
		message = message + okMessage + str(signal)
		success = rb.sendMessage(message.encode())
		if(not success):
			print("Could not transmit")
			logger.error("Could not transmit")

	else:
		print("Signal error")
		logger.error("Signal error")

except Exception as e:
	print(str(e))
	logger.error(str(e))
        rbStatus = False
#if rbStatus false, output red color to debug LED

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
#exceptions caught inside while loop will log then continue
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
			print(messagePoll)
			#sleep for 1 second
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
		print("RB IO Error")
		continue
	except (KeyboardInterrupt):
		#close everything properly after keyboard interrupt
		handlers = logger.handlers[:]
		for h in handlers:
			h.close()
			logger.removeHandler(h)
		exit()

	except Exception as e:
		print(str(e))
		logger.error("RB Error")
		continue

