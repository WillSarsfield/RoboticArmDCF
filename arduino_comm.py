import serial
import time

arduinoPort = '/dev/cu.usbmodem1301' #for mac

arduino = serial.Serial(port=arduinoPort,baudrate=9600, timeout=.1)

def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data=arduino.readline()
    return data

while True:
    num = input("Enter a number: ")
    value = write_read(num)
    #print(value)
    #print(type(value))