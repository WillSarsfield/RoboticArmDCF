from tkinter import *
from tkinter import ttk,messagebox,font
from tkinter.filedialog import askopenfile, asksaveasfile
from os.path import basename as basename
from pathlib import Path
import re 
from execute_code import execute_code
import serial

class RobotArmInterface(Tk):
    #-----!!!need to choose port based on connection!!!-------
    arduinoPort = '/dev/cu.usbmodem1301' #for mac - check bottom of arduino editor and modify 
    #arduinoPort = 'COM5' #for windows - may be a different number
    #---------------------------------------------------------
    timeout=.1005
    arduino=serial.Serial()
    def __init__(self, *args, **kwargs):    
        #setting up arduino comms

        Tk.__init__(self,*args,**kwargs)
        self.title('Robot Arm Interface')
        try: #attempt to establish arduino connection
            self.arduino.close()
            self.arduino = serial.Serial(port=self.arduinoPort,baudrate=115200, timeout=self.timeout)
        except Exception as e:
            messagebox.showerror('IOError','Unable to establish connection:\n'+str(e),parent=self)
            self.destroy()
        self.custom_style = 'awdark'            #tkinter theme downloadable from https://sourceforge.net/projects/tcl-awthemes
        self.geometry('460x300')#window start size
        self.minsize(460,300)
        self.maxsize(600,1000)
        self.configure(background='#323232')
        self.tk.call('lappend', 'auto_path', './awthemes-10.4.0') #link tkinter style to awthemes folder
        self.tk.call('package', 'require', self.custom_style)
        self.style = ttk.Style(self)
        self.style.theme_use(self.custom_style)
        buttonFont=font.Font(family='Helvetica',size=16) #adjusting font of buttons and labels
        labelFont=font.Font(family='Helvetica',size=15,weight='bold')
        self.style.configure('TButton',font=buttonFont)
        self.style.configure('TLabel',font=labelFont,background='#323232',anchor='center')
        container=Frame(self) #container frame contains all pages of application

        container.pack(fill='both',expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        self.frames = {} #dictionary listing all page frames

        for F in (PresetPage, TextEditor, ReadMe): #for each page to construct (list page class in here if extending)
            frame = F(container,self) #construct each page passing container as parent and self as controller
            self.frames[F] = frame #store each page in self.frames
            frame.grid(row=0,column=0,sticky='nsew')

        self.show_frame(PresetPage) #raise PresetPage to top on application start

    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise() #make desired frame visible (switching pages)

class PresetPage(Frame): #start page with preset command buttons for robot arm

    def __init__(self,parent,controller):
        self.controller=controller
        Frame.__init__(self,parent) #contains header_frame and center_frame

        self.header_frame = Frame(self)#contains window swapping buttons
        self.center_frame = Frame(self,relief='raised',border=6,background='#323232')#contains robotic arm movement presets
        self.header_frame.grid(row=0,column=0,sticky='nsew')
        self.center_frame.grid(row=1,column=0,sticky='nsew')   

        label = ttk.Label(self.header_frame,text='Presets') #setting up tabs at top of page
        label.grid(column=0,row=0,columnspan=3,sticky='nsew')
        button1 = ttk.Button(self.header_frame,text='Presets', command=lambda: controller.show_frame(PresetPage))
        button1.grid(column=0,row=1,sticky='ew')
        button2 = ttk.Button(self.header_frame, text='Text Editor', command=lambda: controller.show_frame(TextEditor))
        button2.grid(column=1,row=1,sticky='ew')
        button3 = ttk.Button(self.header_frame, text='Help Page', command=lambda: controller.show_frame(ReadMe))
        button3.grid(column=2,row=1,sticky='ew')

        self.header_frame.grid_columnconfigure((0,1,2),weight=1)

        #setting up preset buttons, change the text attribute and filename argument within command attribute to execute different programs
        command1 = ttk.Button(self.center_frame,text='Reset',cursor='exchange',command=lambda:self.execute_preset(filename='RESET_cmd.txt'))
        command1.grid(column=0,columnspan=2,row=0,padx=5,pady=2.5,sticky='nsew')
        command2 = ttk.Button(self.center_frame,text='Command One',cursor='cross',command=lambda:self.execute_preset(filename='COLLECT_SAMPLE_cmd.txt'))
        command2.grid(column=0,row=1,padx=5,pady=2.5,sticky='nsew')
        command3 = ttk.Button(self.center_frame,text='Command Two',cursor='cross',command=lambda:self.execute_preset(filename='IRRADIATE_cmd.txt'))
        command3.grid(column=0,row=2,padx=5,pady=2.5,sticky='nsew')
        command4 = ttk.Button(self.center_frame,text='Command Three',cursor='cross',command=lambda:self.execute_preset(filename='POUR_EXAMPLE_cmd.txt'))
        command4.grid(column=0,row=3,padx=5,pady=2.5,sticky='nsew')
        command5 = ttk.Button(self.center_frame,text='Command Four',cursor='cross',command=lambda:self.execute_preset(filename='TEST_BOUNDARIES_cmd.txt'))
        command5.grid(column=1,row=1,padx=5,pady=2.5,sticky='nsew')
        command6 = ttk.Button(self.center_frame,text='Command Five',cursor='cross',command=lambda:self.execute_preset(filename='TEST_RANGE_cmd.txt'))
        command6.grid(column=1,row=2,padx=5,pady=2.5,sticky='nsew')
        command7 = ttk.Button(self.center_frame,text='Command Six',cursor='cross',command=lambda:self.execute_preset())
        command7.grid(column=1,row=3,padx=5,pady=2.5,sticky='nsew')

        self.center_frame.grid_columnconfigure((0,1),weight=1)
        self.center_frame.grid_rowconfigure((0,1,2,3),weight=1)

        self.grid_columnconfigure(0,weight=1) #position of center_frame and header_frame within PresetPage
        self.grid_rowconfigure(1,weight=1)

    def execute_preset(self, filename='RESET_cmd.txt'): #reads commands from _cmd.txt file and sends them to the arduino
        try:
            with open(filename,'r') as command_file:
                command_list=command_file.read().splitlines()
                #print(command_list)
                executer=execute_code(self.controller.arduino) #implements execute_code.py
                executer.start(command_list)
        except Exception as e:
            messagebox.showerror('IOError','Unable to execute file:\n'+str(e),parent=self)

class TextEditor(Frame): #code editor page for manually programming robot arm or editing presets
    def __init__(self,parent,controller):
        Frame.__init__(self,parent) # contains header_frame,center_frame,footer_frame

        self.current_filename='Untitled.txt' #relevant to execute_text, compile_text, open_file, save_file methods
        self.current_compilename='Untitled_cmd.txt'
        self.compilepath=''

        self.header_frame = Frame(self)#frame containing window swapping buttons
        self.center_frame = Frame(self)#frame containing textbox and scrollbars
        self.footer_frame = Frame(self)#frame containing file manipulation buttons
        self.header_frame.grid(row=0,column=0,sticky='nsew')
        self.center_frame.grid(row=1,column=0,sticky='nsew')
        self.footer_frame.grid(row=2,column=0,sticky='nsew')

        label = ttk.Label(self.header_frame,text='Text Editor') #menubar contained within header_frame
        label.grid(column=0,row=0,columnspan=3,sticky='nsew') 
        button1 = ttk.Button(self.header_frame, text='Presets', command=lambda: controller.show_frame(PresetPage))
        button1.grid(column=0,row=1,sticky='ew')
        button2 = ttk.Button(self.header_frame, text='Text Editor', command=lambda: controller.show_frame(TextEditor))
        button2.grid(column=1,row=1,sticky='ew')
        button3 = ttk.Button(self.header_frame, text='Help Page', command=lambda: controller.show_frame(ReadMe))
        button3.grid(column=2,row=1,sticky='ew')

        self.header_frame.grid_columnconfigure((0,1,2),weight=1)

        self.center_frame.text_box = Text(self.center_frame, height=5, wrap=NONE)#textbox and scrollbars within center_frame
        self.center_frame.text_box.grid(row=0,column=0,sticky='nsew')
        scrollBary = ttk.Scrollbar(self.center_frame, orient=VERTICAL, command=self.center_frame.text_box.yview)
        scrollBary.grid(row=0,column=1,sticky='ns')
        self.center_frame.text_box['yscrollcommand'] = scrollBary.set
        scrollBarx = ttk.Scrollbar(self.center_frame, orient=HORIZONTAL, command=self.center_frame.text_box.xview)
        scrollBarx.grid(row=1,column=0,sticky='ew')
        self.center_frame.text_box['xscrollcommand'] = scrollBarx.set

        self.center_frame.grid_columnconfigure(0,weight=1)
        self.center_frame.grid_rowconfigure(0,weight=1)
        
        saveButton = ttk.Button(self.footer_frame, text='Save File', command=lambda:self.save_file()) #file manipulation buttons within footer_frame
        saveButton.grid(column=4,row=0,sticky='e',padx=2.5,pady=5)
        openButton = ttk.Button(self.footer_frame, text='Open File', command=lambda:self.open_file())
        openButton.grid(column=3,row=0,sticky='e',padx=2.5,pady=5)
        clearButton = ttk.Button(self.footer_frame, text='Clear', command=lambda:self.clear_text())
        clearButton.grid(column=0,row=0,sticky='e',padx=2.5,pady=5)
        compileButton = ttk.Button(self.footer_frame, text='Compile', command=lambda:self.compile_text())
        compileButton.grid(column=1,row=0,sticky='e',padx=2.5,pady=5)
        executeButton = ttk.Button(self.footer_frame, text='Execute', command=lambda:self.execute_text(RobotArmInterface.arduinoPort))
        executeButton.grid(column=2,row=0,sticky='e',padx=2.5,pady=5)

        self.footer_frame.grid_rowconfigure(0,weight=1)
        self.footer_frame.grid_columnconfigure(0,weight=1)

        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)

    def get_text(self): #get program as a string from the text box
        text=self.center_frame.text_box.get('1.0','end-1c')
        return text

    def clear_text(self): #remove all text from text box
        self.center_frame.text_box.delete(1.0,'end')

    def compile_text(self): #converts text into format ready for serial comms
        text=self.get_text()
        text=''.join(text.split()).lower() #formatting text: remove whitespace and convert to lowercase
        command_list=text.split(';') #splits strings into commands separated by ';'

        def get_raw(*,command,type='move'):
            max_angle=180           #refers to the maximum range of motion the servo has in degrees
            if type=='move':
                paramList=re.findall(r'\d+',command)
                servo_num,angle=int(paramList[0]),int(paramList[1]) # gets all numbers from the move command
                encoded_val= servo_num*(max_angle+1)+angle      # maps (RxR)->R i.e. there is a unique positive encoded_val for each combination of servo&angle
                encoded_val+=1                                  # need to reserve zero for a separate commmand 
                # print(servo_num,angle,'encoded as',encoded_val)
            elif type=='do':
                waitTime=int(re.findall(r'\d+', command)[0]) # gets the wait time from the do command
                encoded_val= -waitTime-1                        #wait command is encoded as the negative numbers (1 is subtracted as the value 0 is already used)
                # print(waitTime,'encoded as',encoded_val)
            return encoded_val
        
        def save_compiled_file(cmd_list):
            self.current_compilename=self.current_filename.replace('.txt','_cmd.txt') #can be replaced - this is to distinguish between compiled and uncompiled files
            savefile=open(self.current_compilename,'w')
            self.compilepath=savefile.name
            if type(savefile)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
                for cmd in cmd_list:
                    savefile.write(str(cmd))
                    savefile.write('\n')
                savefile.close()
            
        move_cmd=re.compile('^s\([0-3]\)a\((0[0-9]{2}|1([0-7][0-9]|80))\)$')#matches input of the form 'S(#)A(###)' with # representing the desired servo & angle
        wait_cmd=re.compile('^do\([0-9]+\)$')                               #matches input of the form 'DO(#)' with # representing the wait time
                                                                            #note angle must be three digits (i.e. use 003 not 3) & servo # must be between 0-3
        encoded_cmds=[]                                                     #also note angle must be less than or equal to 180 to match
                                                                            #move commands are only executed when a do command is executed
        for command in command_list:                                         
            if command=='': #caused by having a ; at the very end of the string
                continue
            elif move_cmd.match(command):
                # print('move command detected:',command)
                encoded_cmds.append(get_raw(command=command,type='move'))
            elif wait_cmd.match(command):
                # print('wait command detected:',command)
                encoded_cmds.append(get_raw(command=command,type='do'))
            else:
                if len(command)>=100:
                    command=command[:100]+'[...]' #limit length of message string
                messagebox.showerror(parent=self,title='Compiler',message='Unrecognised command: '+command+'\nSee \'README.txt\' for help')    #include command description here
                return False

        #print(encoded_cmds)
        save_compiled_file(encoded_cmds)
        messagebox.showinfo(parent=self, title='Compiler',message='Compiled successfully')

    def execute_text(self,port):
        try:
            self.compile_text()
            execute_file=open(self.compilepath,'r') #opens last successfully compiled file ----------ISSUE:
            cmd_list=execute_file.read().split()    #--------- if the last compilation failed this will run the
                                                    #last successful compilation which may be a different file.
            #print(cmd_list)
            RobotArmInterface.arduino.close()
            RobotArmInterface.arduino = serial.Serial(port=port,baudrate=115200, timeout=RobotArmInterface.timeout) #establish arduino connection to start calibration
            executer=execute_code(RobotArmInterface.arduino)
            if messagebox.askokcancel(parent=self, title='Executer',message='Wait for calibration to complete'):
                #time.sleep(1)       #need to give executer time to set up
                #cmd_list=[int(x)for x in cmd_list] #if commands are needed as ints rather than string
                executer.start(cmd_list=cmd_list)
                messagebox.showinfo(parent=self, title='Executer',message='Execution complete')
        except Exception as e:
            messagebox.showerror('IOError','Unable to execute file:\n'+str(e),parent=self)

    def save_file(self): #opens saveasfile dialog, saves text from text box to file
        try:
            new_file=asksaveasfile(parent=self,initialdir='./',initialfile=self.current_filename,defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            self.current_filename=basename(new_file.name)
            if type(new_file)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
                new_file.writelines(self.get_text())
                new_file.close()
        except Exception as e:
            messagebox.showerror('IOError','Unable to save file:\n'+str(e),parent=self)

    def open_file(self): #opens askopenfile dialog, sets textbox text to file contents
        try:
            new_file=askopenfile(parent=self,initialdir='./',defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            self.current_filename=basename(new_file.name) #saves the name of the file that was opened, so when it is saved that name is set as default
            if type(new_file)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
                self.clear_text()
                self.center_frame.text_box.insert('1.0',new_file.read())
                new_file.close()
        except Exception as e:
            messagebox.showerror('IOError','Unable to open file:\n'+str(e),parent=self)

class ReadMe(Frame):
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)

        self.header_frame = Frame(self)#frame containing window swapping buttons
        self.center_frame = Frame(self)#frame containing textbox and scrollbars
        self.header_frame.grid(row=0,column=0,sticky='nsew')
        self.center_frame.grid(row=1,column=0,sticky='nsew')
        self.grid_columnconfigure(0,weight=1) #positioning header_frame and center_frame within ReadMe Frame
        self.grid_rowconfigure(1,weight=1)


        label = ttk.Label(self.header_frame,text='Help Page')#menu bar contained within header_frame
        label.grid(column=0,row=0,columnspan=3,sticky='nsew')
        button1 = ttk.Button(self.header_frame, text='Presets', command=lambda: controller.show_frame(PresetPage))
        button1.grid(column=0,row=1,sticky='ew')
        button2 = ttk.Button(self.header_frame, text='Text Editor', command=lambda: controller.show_frame(TextEditor))
        button2.grid(column=1,row=1,sticky='ew')
        button3 = ttk.Button(self.header_frame, text='Help Page', command=lambda: controller.show_frame(ReadMe))
        button3.grid(column=2,row=1,sticky='ew')

        with open('./README.txt','r') as readme_file:#open README.txt and put its contents in the textbox
            self.center_frame.readme_text = Text(self.center_frame,wrap='word')
            self.center_frame.readme_text.insert('1.0',readme_file.read())
            readme_file.close()       
        self.center_frame.readme_text.grid(row=0,column=0,sticky='nsew')
        self.center_frame.readme_text.config(state='disabled') # make textbox uneditable
        scrollBary = ttk.Scrollbar(self.center_frame, orient=VERTICAL, command=self.center_frame.readme_text.yview)
        scrollBary.grid(row=0,column=1,sticky='ns')
        self.center_frame.readme_text['yscrollcommand'] = scrollBary.set

        self.header_frame.grid_columnconfigure((0,1,2),weight=1)
        self.center_frame.grid_columnconfigure(0,weight=1)
        self.center_frame.grid_rowconfigure(0,weight=1)

        
app=RobotArmInterface()
app.mainloop()
