import serial
import time
import socket

class execute_code:
    timeout=.1005
    min_delay=4050
    def __init__(self,arduino):
        self.arduino=arduino

    def start(self,cmd_list=None):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        HOST = socket.gethostname()  # Standard loopback interface address (localhost)
        PORT = 6181  # Port to listen on (non-privileged ports are > 1023)
        s.bind((HOST,PORT))
        for cmd in cmd_list:
            print(cmd)
            if cmd=='':
                continue
            elif float(cmd)<0:
                self.arduino.write(bytes('0','utf-8'))
                time.sleep((-(float(cmd)+1)+self.min_delay)/1000)
            elif float(cmd) > 15000:
                s.listen(5)
                clientsocket, addr = s.accept()
                print(f"Connection to {addr} establshed")
                msg = "FC  L3-1|PosSC|1.03"
                clientsocket.send(bytes(msg, "utf-8"))
                clientsocket.close()
                time.sleep(int(cmd) - 15000)
            elif float(cmd) == 15000:
                s.listen(5)
                clientsocket, addr = s.accept()
                print(f"Connection to {addr} establshed")
                msg = "FC  L3-1|PosSC|0.03"
                clientsocket.send(bytes(msg, "utf-8"))
                clientsocket.close()
            else:
                self.arduino.write(bytes(cmd,'utf-8'))
            time.sleep(self.timeout)
        s.shutdown()
        print('done')