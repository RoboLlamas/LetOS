#!/usr/bin/env python
import Adafruit_BMP.BMP085 as BMP085

class letsatAltimeter():

	verify = False
	#port should be an integer for i2c port
	#known altitude should be in meters and sealevel in pa
	def __init__(self, port, knownAlt, seaLevel_pa):
		altimeter = BMP085.BMP085(busnum=port)
		#make object global
		self.altimeter = altimeter
		self.seaLevel_pa = seaLevel_pa
		#check altitude is close to accurate
		temp = altimeter.read_temperature()
		pres = altimeter.read_pressure()
		alt = altimeter.read_altitude(sealevel_pa = seaLevel_pa)

		#sets variable letsatAltimeter.verify to T/F
		#Handle exceptions in main script!
		if (abs(knownAlt - alt) < 30 ):
			self.verify = True
		else:
			self.verify = False


	def get_temp(self):
		temp = self.altimeter.read_temperature()
		return temp

	def get_pressure(self):
		pres = self.altimeter.read_pressure()
		return pres

	def get_altitude(self):
		alt = self.altimeter.read_altitude(sealevel_pa = self.seaLevel_pa)
		return alt

	def get_sealevel(self):
		sPres = self.altimeter.read_sealevel_pressure()
		return sPres


