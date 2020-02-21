#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol

class letsatRockBlock():

	#make the rb global
	def __init__(self, port):
		rb = rockBlock.rockBlock(port, self)
		self.rb = rb

	#returns boolean to indicate if ping worked
	def stateOfHealth(self):
		print("State of Health");
		status = self.rb.ping()
		return status

	#returns an integer to represent signal strength
	def signalStrength(self):
		print("Requesting signal strength")
		signal = self.rb.requestSignalStrength()
		return signal

	#returns true if it can get a connection and automatically calls
	#rockBlockRxMessageQueue
	def messageCheck(self):
		count = self.rb.messageCheck()
		return count

	#returns system time if network service available
	#else it returns 0
	def networkTime(self):
		time = self.rb.networkTime()
		return time

	#returns true if message sent
	#else returns false
	#calls rockBlockTxStarted and rockBlockTxFailed
	def sendMessage(self, msg):
		success = self.rb.sendMessage(msg)
		return success

	#close serial connection
	def done(self):
		self.rb.close()

	#returns all serial ports on system
	#returns as an array
	def listPorts(self):
		ports = self.rb.listPorts()
		return ports


	#Do something for when failures occur

	def rockBlockConnected(self):
		print("rockBlockConnected")

	def rockBlockDisconnected(self):
		print("rockBlockDisconnected")

	def rockBlockSignalUpdate(self, signal):
		print("rockBlockSignalUpdate " + str(signal))

	def rockBlockSignalPass(self):
		print("rockBlockSignalPass")

	def rockBlockSignalFail(self):
		print("rockBlockSignalFail")

	def rockBlockRxStarted(self):
		print("rockBlockRxStarted")

	def rockBlockRxFailed(self):
		print("rockBlockRxFailed")

	def rockBlockRxReceived(self, mtmsn, data):
		print("rockBlockRxReceived")

	def rockBlockRxMessageQueue(self, count):
		print("rockBlockRxMessageQueue " + str(count))

	def rockBlockTxStarted(self):
		print ("rockBlockTxStarted")

	def rockBlockTxFailed(self):
		print("rockBlockTxFailed")

	def rockBlockTxSuccess(self, momsn):
		print("rockBlockTxSuccess " + str(momsn))

