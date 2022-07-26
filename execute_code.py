import serial
import time


class execute_code():

    def __init__(self):
        arduinoPort = '/dev/cu.usbmodem11301' #for mac - check bottom of arduino editor any modify
        #arduinoPort = 'COM4' #for windows - may be a different number

        self.arduino = serial.Serial(port=arduinoPort,baudrate=9600, timeout=.1)

    def start(self,cmd_list=None):
        print(cmd_list)
        for cmd in cmd_list:
            if int(cmd)<0:
                self.arduino.write(bytes('-1','utf-8'))
                time.sleep(-(cmd+1))
            else:
                self.arduino.write(bytes(cmd,'utf-8'))