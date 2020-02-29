class Thermo:
	def __init__(self, heaterpin, mintemp, maxtemp):
		self.pin = heaterpin
		self.min = mintemp
		self.max = maxtemp
		#setup(pin, out)
		
		self.heating = False
	
	def update(self, sensortemp):
		if self.heating and sensortemp >= self.max:
			self.heating = False
			#output(pin, 0)
		elif (not self.heating) and sensortemp <= self.min:
			self.heating = True
			#output(pin, 1)
