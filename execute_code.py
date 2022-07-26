import serial
import time


class execute_code():

    def __init__(self):
        arduinoPort = '/dev/cu.usbmodem1101' #for mac - check bottom of arduino editor and modify
        # arduinoPort = 'COM5' #for windows - may be a different number

        self.arduino = serial.Serial(port=arduinoPort,baudrate=9600, timeout=1)

    def start(self,cmd_list=None):
        for cmd in cmd_list:
            print(cmd)
            if int(cmd)<0:
                self.arduino.write(bytes('0','utf-8'))
                time.sleep(-(int(cmd)+1)/1000)
            else:
                self.arduino.write(bytes(str(cmd),'utf-8'))
            time.sleep(2)

        print('done')