from tkinter import *
from tkinter import ttk
import sys
import os
import serial
import time

arduinoPort = '/dev/cu.usbmodem1301' #for mac
arduino = serial.Serial(port=arduinoPort,baudrate=9600, timeout=.1)
time.sleep(2)

root = Tk()
root.tk.call('lappend', 'auto_path', './awthemes-10.4.0')
root.tk.call('package', 'require', 'awdark')
style = ttk.Style()
style.theme_use('awdark')
l = Listbox(root, height=5)
l.grid(column=0, row=0, sticky=(N,W,E,S))
s = ttk.Scrollbar(root, orient=VERTICAL, command=l.yview)
s.grid(column=1, row=0, sticky=(N,S))
l['yscrollcommand'] = s.set

def hello_world():
    os.system('python3 hello_world.py')
    
lightState="0"
def toggle_lights():
    global lightState
    arduino.write(bytes(lightState,'utf-8'))
    time.sleep(0.05)
    lightState=arduino.readline().decode()
        


button1 = ttk.Button(root, text="Hello World", command=hello_world).grid(column=0, columnspan=2, row=1, sticky=(W))
button3 = ttk.Button(root, text="Toggle Lights", command=toggle_lights).grid(column=0, columnspan=2, row=1, sticky=(E))
button2 = ttk.Button(root, text="Button2").grid(column=0, columnspan=2, row=1)
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
for i in range(1,101):
    l.insert('end', 'Line %d of 100' % i)
root.mainloop() 