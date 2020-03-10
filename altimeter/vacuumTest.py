#!/usr/bin/env python
from letsatAltimeter import letsatAltimeter
from time import sleep

import logging

# For the Beaglebone Black the library will assume bus 1 by default, which is
# exposed with SCL = P9_19 and SDA = P9_20.
#sensor = BMP085.BMP085()

#P9_19 and P9_20
sensor = letsatAltimeter(2, 111, 102472.12)

#exception handling
"""
if (not sensor.verify):
	print(str(sensor.get_altitude()))
	print("Inaccurate initial altitude")
	exit()
"""
# You can also optionally change the BMP085 mode to one of BMP085_ULTRALOWPOWER,
# BMP085_STANDARD, BMP085_HIGHRES, or BMP085_ULTRAHIGHRES.  See the BMP085
# datasheet for more details on the meanings of each mode (accuracy and power
# consumption are primarily the differences).  The default mode is STANDARD.
#sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

#setup logging. One file logs every second
#second file only logs when altitude is 5% > than the avg
loggerMain = logging.getLogger("DataLog")
loggerMain.setLevel('DEBUG')
loggerChange = logging.getLogger("ChangeLog")
loggerChange.setLevel('DEBUG')
formatter = logging.Formatter('%(asctime)s, %(message)s')
logFileMain = 'DataLog.csv'
logFileChange = 'ChangeLog.csv'
handlerMain = logging.FileHandler(logFileMain)
handlerChange = logging.FileHandler(logFileChange)
handlerMain.setLevel(logging.DEBUG)
handlerChange.setLevel(logging.DEBUG)
handlerMain.setFormatter(formatter)
handlerChange.setFormatter(formatter)
loggerMain.addHandler(handlerMain)
loggerChange.addHandler(handlerChange)

#get first 10 reads and find average for comparison purposes
initReadings = [None] * 10
for i in range(0, 10):
	initReadings[i] = sensor.get_altitude()
	sleep(1)
avgAlt = round(sum(initReadings) / len(initReadings), 2)
print('Average altitude = {0:0.2f} Pa'.format(avgAlt))

#<><><><> allow clean break of loop upon keyboard interrupt
while(True):
	try:
		temp = sensor.get_temp()
		pressure = sensor.get_pressure()
		altitude = sensor.get_altitude()
		sPressure = sensor.get_sealevel()

		print('Temp = {0:0.2f} *C'.format(temp))
		print('Pressure = {0:0.2f} Pa'.format(pressure))
		print('Altitude = {0:0.2f} m'.format(altitude))
		print('Sealevel Pressure = {0:0.2f} Pa'.format(sPressure))


		loggerMain.debug('%0.3f,%0.3f,%0.3f,%0.3f' % (temp, pressure, altitude, sPressure))

		#check for significant change
		if (altitude > (1.05 * avgAlt)):
			loggerChange.debug('%0.3f,%0.3f,%0.3f,%0.3f' % (temp, pressure, altitude, sPressure))
			#avgAlt = altitude
		sleep(1)

	except (KeyboardInterrupt):
		#clean exit
		handlerMain.close()
		handlerChange.close()
		loggerMain.removeHandler(handlerMain)
		loggerChange.removeHandler(handlerChange)
		exit()


