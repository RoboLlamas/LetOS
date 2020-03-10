#!/usr/bin/env python
import rockBlock
from rockBlock import rockBlockProtocol
import letsatRockBlock
from letsatRockBlock import letsatRockBlock

rb = letsatRockBlock("/dev/ttyO1")
print("Testing state of health")
rb.stateOfHealth()

print("Testing signal strength")
signal =rb.signalStrength()
print("Signal " + str(signal))

print("Testing message check")
count = rb.messageCheck()
print("Count " + str(count))

print("Testing network time")
time = rb.networkTime()
print("Time " + str(time))

#print("Testing send message")
#success = rb.sendMessage(b'Hello World')
#print("Success " + str(success))

print("Testing list ports")
ports = rb.listPorts()
for i in ports:
	print(str(i))

print("Closing serial connection")
rb.done()

