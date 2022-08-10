import serial
import time

arduinoPort = '/dev/cu.usbmodem1301' #for mac

arduino = serial.Serial(port=arduinoPort,baudrate=9600, timeout=.1)
time.sleep(1)

def write_read(x):
    arduino.write(x)
    time.sleep(0.05)
    data=arduino.readline()
    return data

num = bytes(input("input: "),'utf-8')
while True:
    print("sent:",num)
    num = write_read(num)
    print("recieved:",num)