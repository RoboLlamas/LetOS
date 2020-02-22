import Adafruit_BBIO.UART as uart
import serial

def init(tty):
	global ser
	uart.setup("UART" + str(tty))
	ser = serial.Serial(port = "/dev/ttyO" + str(tty), baudrate = 9600, timeout = 1)

fix = False
latlong = ""
altitude = 0.0	# meters
time = ""	# hhmmss
nSats = 0
course = 0.0	# degrees
speed = 0.0	# knots

def update():
	global fix, latlong, altitude, time, nSats, course, speed

	while ser.inWaiting():
		data = ser.readline().split(",")
		if data[0] == "$GPGGA":
			try:
				fix = (data[6] != "0")
				latlong = data[2] + data[3] + data[4] + data[5]
				altitude = float(data[9])
				time = data[1][0:6]
				nSats = int(data[7])
			except ValueError:
				pass

		elif data[0] == "$GPVTG":
			try:
				course = float(data[1])
				speed = float(data[5])
			except ValueError:
				pass

	return fix


if __name__ == '__main__':
	from time import sleep

	init(4)

	while(1):
		sleep(1)
		update()
		print("~~~~~ " + time + "Z - Fix:" + str(fix) + " ~~~~~")
		print(str(nSats) + " satellites")
		print(latlong)
		print(str(altitude) + "m")
		print("moving " + str(course) + "deg at " + str(speed) + "knots")
