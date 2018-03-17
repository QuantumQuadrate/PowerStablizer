import serial
import sys
import os
import time
import string
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import LED
factory = PiGPIOFactory(host='192.168.1.136')
led1 = LED(18, pin_factory=factory)
port = serial.Serial('COM3',baudrate = 115200,bytesize=8,parity=serial.PARITY_NONE,timeout=3)
print "port setup"
setpoint = 59700000
#setpoint = 22000
print "setpoint is:  " , setpoint
threshold = 0.05
print "threshold is:  " , threshold
while True:
	port.write(b'C?\r\n')
	readout = float(string.split((port.readline()),"e")[0]) * (10**int(port.readline()[13]))
	print readout
	if readout/setpoint > (1 + threshold) or readout/setpoint < (1 - threshold):
		led1.on()
		print "pin on"
	else:
		led1.off()
		#print "pin off"
