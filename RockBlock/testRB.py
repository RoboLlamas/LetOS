#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol

class Example(rockBlockProtocol):
	def main(self):
		rb = rockBlock.rockBlock("/dev/ttyO1", self)
		print("testing")
		#rb.sendMessage(b'Hello World!')
		status = rb.ping()
		print(str(status))
		#rb.setup()
		rb.close()

	def rockBlockConnected(self):
		print("rockBlockConnected")

	def rockBlockTxStarted(self):
		print ("rockBlockTxStarted")

	def rockBlockTxFailed(self):
		print("rockBlockTxFailed")

	def rockBlockTxSuccess(self, momsn):
		print("rockBlockTxSuccess " + str(momsn))

if __name__ == 'main':
	Example().main()


