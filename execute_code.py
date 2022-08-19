import serial
import time

class execute_code:
    timeout=.1005
    min_delay=4050
    def __init__(self,arduino):
        self.arduino=arduino

    def start(self,cmd_list=None):
        print(cmd_list)
        for cmd in cmd_list:
            print(cmd)
            if cmd=='':
                continue
            elif float(cmd)<0:
                self.arduino.write(bytes('0','utf-8'))
                time.sleep((-(float(cmd)+1)+self.min_delay)/1000)
                print("DO")
            else:
                self.arduino.write(bytes(cmd,'utf-8'))
                print("MOVE")
            time.sleep(self.timeout)

        print('done')