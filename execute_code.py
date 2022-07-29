import serial
import time


class execute_code():

    def __init__(self,arduino):
        self.arduino=arduino

    def start(self,cmd_list=None):
        for cmd in cmd_list:
            print(cmd)
            if int(cmd)<0:
                self.arduino.write(bytes('0','utf-8'))
                time.sleep(-(int(cmd)+1+min_delay)/1000)
            else:
                self.arduino.write(bytes(str(cmd),'utf-8'))
            time.sleep(self.timeout)

        print('done')