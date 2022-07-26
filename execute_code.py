import serial
import time


class execute_code():

    def __init__(self):
        #arduinoPort = '/dev/cu.usbmodem1301' #for mac
        #arduinoPort = 'COM4' #for windows - may be a different number
        pass
        #arduino = serial.Serial(port=arduinoPort,baudrate=9600, timeout=.1)

    def start(self,cmd_list=None):
        print(cmd_list)

    #num = bytes(input("input: "),'utf-8')
    #while True:
        #print("sent:",num)
       # num = write_read(num)
        #print("recieved:",num)