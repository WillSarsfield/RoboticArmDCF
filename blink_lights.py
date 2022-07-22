import serial
import time

arduinoPort = '/dev/cu.usbmodem1301' #for mac

arduino = serial.Serial(port=arduinoPort,baudrate=9600, timeout=.1)
time.sleep(1)

def write_read(x):
    arduino.write(bytes(x,'utf-8'))
    time.sleep(0.05)
    data=int(arduino.readline().decode())
    return data

num = input("input: ")
while True:
    print("sent:",num)
    num = str(write_read(num))
    print("recieved:",num)