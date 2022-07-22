from tkinter import *
from tkinter import ttk
import sys
import os
import serial
import time

arduinoPort = '/dev/cu.usbmodem1301' #for mac
arduino = serial.Serial(port=arduinoPort,baudrate=9600, timeout=.1)
time.sleep(2)


custom_style = 'awdark'
root = Tk()
root.tk.call('lappend', 'auto_path', './awthemes-10.4.0')
root.tk.call('package', 'require', custom_style)
style = ttk.Style()
style.theme_use(custom_style)


def servo1_right():
    arduino.write(bytes("1",'utf-8'))
    
def servo1_left():
    arduino.write(bytes("1",'utf-8'))

def servo2_right():
    arduino.write(bytes("2",'utf-8'))
    
def servo2_left():
    arduino.write(bytes("2",'utf-8'))
        


button1 = ttk.Button(root, text="Move 1 Left", command=servo1_left)
button2 = ttk.Button(root, text="Move 1 Right", command=servo1_right)
button3 = ttk.Button(root, text="Move 2 Left", command=servo2_left)
button4 = ttk.Button(root, text="Move 2 Right", command=servo2_right)
button1.pack(side="top")
button2.pack(side="top")
button3.pack(side="top")
button4.pack(side="top")
root.mainloop() 