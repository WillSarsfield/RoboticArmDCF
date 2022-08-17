import serial
import time

class execute_code:
    timeout=.1005
    min_delay=4050
    def __init__(self,arduino):
        self.arduino=arduino

    def start(self,cmd_list=None):
        for cmd in cmd_list:
            print(cmd)
            if cmd=='':
                continue
            elif int(cmd)<0:
                self.arduino.write(bytes('0','utf-8'))
                time.sleep((-(int(cmd)+1)+self.min_delay)/1000)
            else:
                self.arduino.write(bytes(str(cmd),'utf-8'))
            time.sleep(self.timeout)

        print('done')