import serial
import time

arduinoPort = '/dev/cu.usbmodem1301' #for mac

arduino = serial.Serial(port=arduinoPort,baudrate=9600, timeout=.1)

num = b''

while num==b'':
    num = arduino.read()

print("recieved:",num)
if num==b'0':
    num=b'1'
elif num==b'1':
    num=b'0'
arduino.write(num)
print("sent:",num)