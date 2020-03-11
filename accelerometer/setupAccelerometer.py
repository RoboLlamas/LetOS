#!/usr/bin/python
"""
Initial offsets
Accel
X 236
Y 1281
Z 542
"""

# Import the MPU6050 class from the MPU6050.py file
from MPU6050 import MPU6050
from time import sleep


#sensor is a MPU6050 object
def setupAccelerometer(sensor):

	try:
		#zero sensors and apply offsets
		sensor.bus.write_word_data(sensor.address, 0x06, 0)
		sensor.bus.write_word_data(sensor.address, 0x08, 0)
		sensor.bus.write_word_data(sensor.address, 0x0A, 0)

		#In little Endian. So 1329d -> 0531h -> enter as 3105h = 12549
		sensor.bus.write_word_data(sensor.address, 0x06, 20736)
		sensor.bus.write_word_data(sensor.address, 0x08, 12549)
		sensor.bus.write_word_data(sensor.address, 0x0A, 15362)

		#acceleration
		xOffset = sensor.read_i2c_word(0x06)
		yOffset = sensor.read_i2c_word(0x08)
		zOffset = sensor.read_i2c_word(0x0A)

		"""
		print("Accel offsets")
		print("X " + str(xOffset))
		print("Y " + str(yOffset))
		print("Z " + str(zOffset))
		"""

		#gyroscopes
		sensor.bus.write_byte_data(sensor.address, 0x00, 131)
		sensor.bus.write_byte_data(sensor.address, 0x01, 127)
		sensor.bus.write_byte_data(sensor.address, 0x02, 129)

		xGOffset = sensor.bus.read_byte_data(sensor.address, 0x00)
		yGOffset = sensor.bus.read_byte_data(sensor.address, 0x01)
		zGOffset = sensor.bus.read_byte_data(sensor.address, 0x02)

		"""
		print("Gyro offsets")
		print("X " + str(xGOffset))
		print("Y " + str(yGOffset))
		print("Z " + str(zGOffset))
		"""
		return True
	except:
		#couldn't read or write properly
		return False


