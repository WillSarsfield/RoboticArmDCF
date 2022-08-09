from tkinter import *
from tkinter import ttk
import sys
import os
import serial
import time

arduinoPort = '/dev/cu.usbmodem1301' #for mac
#arduino = serial.Serial(port=arduinoPort,baudrate=9600, timeout=.1)
time.sleep(2)


custom_style = 'awdark'
root = Tk()
root.tk.call('lappend', 'auto_path', './awthemes-10.4.0')
root.tk.call('package', 'require', custom_style)
style = ttk.Style()
style.theme_use(custom_style)

def encode(servo_num,angle,max_angle=180):
    return servo_num*(max_angle+1)+angle

def servo0_right():
    data=encode(0,180)
    arduino.write(bytes(str(data),'utf-8'))
    time.sleep(0.05)

def servo0_left():
    data=encode(0,0)
    arduino.write(bytes(str(data),'utf-8'))
    time.sleep(0.05)

def servo1_right():
    data=encode(1,180)
    arduino.write(bytes(str(data),'utf-8'))
    time.sleep(0.05)
    
def servo1_left():
    data=encode(1,0)
    arduino.write(bytes(str(data),'utf-8'))
    time.sleep(0.05)
        
button1 = ttk.Button(root, text="Move 1 Left", command=servo0_left).grid(column=0,row=0,sticky='nsew')
button2 = ttk.Button(root, text="Move 1 Right", command=servo0_right).grid(column=0,row=1,sticky='nsew')
button3 = ttk.Button(root, text="Move 2 Left", command=servo1_left).grid(column=0,row=2,sticky='nsew')
button4 = ttk.Button(root, text="Move 2 Right", command=servo1_right).grid(column=0,row=3,sticky='nsew')
root.grid_columnconfigure(0,weight=1)
root.mainloop() 