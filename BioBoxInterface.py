from tkinter import *
from tkinter import ttk,messagebox,font
from tkinter.filedialog import askopenfile, asksaveasfile
from os.path import basename as basename
from pathlib import Path
import re 
from execute_code import execute_code
from CommandInterpreter import CommandInterpreter
import serial

class BioBoxInterface(Tk):
    #-----!!!need to choose port based on connection!!!-------
    arduinoPort = '/dev/cu.usbmodem1301' #for mac - check bottom of arduino editor and modify 
    #arduinoPort = 'COM5' #for windows - may be a different number
    #---------------------------------------------------------
    timeout=.1005
    arduino=serial.Serial()
    def __init__(self, *args, **kwargs):   

        self.compiler=Compiler(self)
        self.executer=Executer(self) 

        self.current_filename='./COMMANDS/Untitled.txt' #relevant to execute_text, compile_text, open_file, save_file methods
        self.current_compilename='./COMMANDS/Untitled_cmd.txt'
        self.compilepath=''

        Tk.__init__(self,*args,**kwargs)
        self.title('BioBox Interface')

        #setting up arduino comms
        try: #attempt to establish arduino connection
            BioBoxInterface.arduino.close()
            BioBoxInterface.arduino = serial.Serial(port=self.arduinoPort,baudrate=115200, timeout=self.timeout)
        except Exception as e:
            messagebox.showerror('IOError','Unable to establish connection:\n'+str(e),parent=self)
            #self.destroy()
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

        self.compiler = controller.compiler
        self.executer = controller.executer

        self.controller=controller
        Frame.__init__(self,parent) #contains header_frame and center_frame

        self.header_frame = Frame(self)#contains window swapping buttons
        self.center_frame = Frame(self,background='#323232')#contains robotic arm movement presets
        self.footer_frame = Frame(self,relief='raised',border=6,background='#323232')#contains reset and save position buttons
        self.header_frame.grid(row=0,column=0,sticky='nsew')
        self.center_frame.grid(row=1,column=0,sticky='nsew')
        self.footer_frame.grid(row=2,column=0,sticky='nsew')

        label = ttk.Label(self.header_frame,text='Presets') #setting up tabs at top of page
        label.grid(column=0,row=0,columnspan=3,sticky='nsew')
        button1 = ttk.Button(self.header_frame,text='Presets', command=lambda: controller.show_frame(PresetPage))
        button1.grid(column=0,row=1,sticky='ew')
        button2 = ttk.Button(self.header_frame, text='Text Editor', command=lambda: controller.show_frame(TextEditor))
        button2.grid(column=1,row=1,sticky='ew')
        button3 = ttk.Button(self.header_frame, text='Help Page', command=lambda: controller.show_frame(ReadMe))
        button3.grid(column=2,row=1,sticky='ew')

        self.header_frame.grid_columnconfigure((0,1,2),weight=1)

        command_names=[         #names of each preset button, changing these renames the buttons
            'Reset', #0
            '<< x',  #1
            '<< y',  #2
            '<< z',  #3
            'x >>',  #4
            'y >>',  #5
            'z >>'   #6
        ]

        presets_matrix = {      #names of compiled files corresponding to each button, change these to change what file the button executes
            0:'./COMMANDS/RESET_cmd.txt',
            1:'./COMMANDS/SHFTDWN_X_cmd.txt',
            2:'./COMMANDS/SHFTUP_X_cmd.txt',
            3:'./COMMANDS/SHFTDWN_Y_cmd.txt',
            4:'./COMMANDS/SHFTUP_Y_cmd.txt',
            5:'./COMMANDS/SHFTDWN_Z_cmd.txt',
            6:'./COMMANDS/SHFTUP_Z_cmd.txt'
        }

        #setting up preset buttons, change the command_names text and presets_matrix filename to execute different programs
        command1 = ttk.Button(self.footer_frame,text=command_names[0],cursor='exchange',command=lambda:self.execute_preset(filename=presets_matrix[0]))
        command1.grid(column=0,row=0,padx=2.5,pady=5,sticky='nsew') #this first one is actually in the footer (reset button)
        command2 = ttk.Button(self.center_frame,text=command_names[1],cursor='cross',command=lambda:self.execute_preset(filename=presets_matrix[1]))
        command2.grid(column=0,row=0,padx=5,pady=2.5,sticky='nsew')
        command3 = ttk.Button(self.center_frame,text=command_names[2],cursor='cross',command=lambda:self.execute_preset(filename=presets_matrix[2]))
        command3.grid(column=0,row=1,padx=5,pady=2.5,sticky='nsew')
        command4 = ttk.Button(self.center_frame,text=command_names[3],cursor='cross',command=lambda:self.execute_preset(filename=presets_matrix[3]))
        command4.grid(column=0,row=2,padx=5,pady=2.5,sticky='nsew')
        command5 = ttk.Button(self.center_frame,text=command_names[4],cursor='cross',command=lambda:self.execute_preset(filename=presets_matrix[4]))
        command5.grid(column=2,row=0,padx=5,pady=2.5,sticky='nsew')
        command6 = ttk.Button(self.center_frame,text=command_names[5],cursor='cross',command=lambda:self.execute_preset(filename=presets_matrix[5]))
        command6.grid(column=2,row=1,padx=5,pady=2.5,sticky='nsew')
        command7 = ttk.Button(self.center_frame,text=command_names[6],cursor='cross',command=lambda:self.execute_preset(filename=presets_matrix[6]))
        command7.grid(column=2,row=2,padx=5,pady=2.5,sticky='nsew')

        xentry = ttk.Entry(self.center_frame,justify='center')
        xentry.insert(0,'0')
        yentry = ttk.Entry(self.center_frame,justify='center')
        yentry.insert(0,'0')
        zentry = ttk.Entry(self.center_frame,justify='center')
        zentry.insert(0,'0')

        xentry.grid(column=1,row=0,padx=2.5,pady=2.5,sticky='ew')
        yentry.grid(column=1,row=1,padx=2.5,pady=2.5,sticky='ew')
        zentry.grid(column=1,row=2,padx=2.5,pady=2.5,sticky='ew')

        self.center_frame.grid_columnconfigure((0,2),weight=1)
        self.center_frame.grid_rowconfigure((0,1,2),weight=1)

        # other neccessary functions, unlikely to need changed
        learn_pos_btn = ttk.Button(self.footer_frame,text='Learn As..')
        learn_pos_btn.grid(column=2,row=0,padx=2.5,pady=5,sticky='nsew')
        move_btn = ttk.Button(self.footer_frame,text='Move')
        move_btn.grid(column=1,row=0,padx=2.5,pady=5,sticky='nsew')

        self.footer_frame.grid_columnconfigure((0,1,2),weight=1)
        self.footer_frame.grid_rowconfigure(0,weight=1)

        self.grid_columnconfigure(0,weight=1) #position of frames within PresetPage
        self.grid_rowconfigure(1,weight=1)

    def execute_preset(self, filename='RESET_cmd.txt'): #reads commands from _cmd.txt file and sends them to the arduino
        self.executer.execute_preset(filename=filename)

class TextEditor(Frame): #code editor page for manually programming robot arm or editing presets

    def __init__(self,parent,controller):
        Frame.__init__(self,parent) # contains header_frame,center_frame,footer_frame

        self.executer=controller.executer
        self.compiler=controller.compiler
        self.controller=controller

        self.header_frame = Frame(self)#frame containing window swapping buttons
        self.center_frame = Frame(self,bg='#323232')#frame containing textbox and scrollbars
        self.footer_frame = Frame(self,relief='raised',border=6,background='#323232')#frame containing file manipulation buttons
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
        saveButton.grid(column=4,row=0,sticky='ew',padx=2.5,pady=5)
        openButton = ttk.Button(self.footer_frame, text='Open File', command=lambda:self.open_file())
        openButton.grid(column=3,row=0,sticky='ew',padx=2.5,pady=5)
        clearButton = ttk.Button(self.footer_frame, text='Clear', command=lambda:self.clear_text())
        clearButton.grid(column=0,row=0,sticky='ew',padx=2.5,pady=5)
        compileButton = ttk.Button(self.footer_frame, text='Compile', command=lambda:self.compile_text())
        compileButton.grid(column=1,row=0,sticky='ew',padx=2.5,pady=5)
        executeButton = ttk.Button(self.footer_frame, text='Execute', command=lambda:self.execute_text(BioBoxInterface.arduinoPort))
        executeButton.grid(column=2,row=0,sticky='ew',padx=2.5,pady=5)

        self.footer_frame.grid_rowconfigure(0,weight=1)
        self.footer_frame.grid_columnconfigure((0,1,2,3,4),weight=1)

        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)

    def get_text(self): #get program as a string from the text box
        text=self.center_frame.text_box.get('1.0','end-1c')
        return text

    def clear_text(self): #remove all text from text box
        self.center_frame.text_box.delete(1.0,'end')

    def compile_text(self): #converts text into format ready for serial comms
        return self.compiler.compile_text(text=self.get_text())

    def execute_text(self,port):
        self.executer.execute_text()

    def save_file(self): #opens saveasfile dialog, saves text from text box to file
        try:
            new_file=asksaveasfile(parent=self,initialdir='./COMMANDS',initialfile=self.controller.current_filename,defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            self.controller.current_filename=basename(new_file.name)
            if type(new_file)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
                new_file.writelines(self.get_text())
                new_file.close()
        except Exception as e:
            messagebox.showerror('IOError','Unable to save file:\n'+str(e),parent=self)

    def open_file(self): #opens askopenfile dialog, sets textbox text to file contents
        try:
            new_file=askopenfile(parent=self,initialdir='./COMMANDS',defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            self.controller.current_filename=basename(new_file.name) #saves the name of the file that was opened, so when it is saved that name is set as default
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

class Compiler:
    def __init__(self,parent):
        self.parent=parent
        self.interpreter=CommandInterpreter(0,0,0) #initial offset valuesß

    def get_raw(self,command,type=''):
        return self.interpreter.get_encoded_command(command=command,type=type)

    def save_compiled_file(self,cmd_list):
        self.parent.current_compilename=self.parent.current_filename.replace('.txt','_cmd.txt') #can be replaced - this is to distinguish between compiled and uncompiled files
        savefile=open(self.parent.current_compilename,'w')
        self.parent.compilepath=savefile.name
        if type(savefile)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
            for cmd in cmd_list:
                savefile.write(str(cmd))
                savefile.write('\n')
            savefile.close()

    def compile_text(self,text=''):
        text=''.join(text.split()).lower() #formatting text: remove whitespace and convert to lowercase
        command_list=text.split(';') #splits strings into commands separated by ';'

        cmd_regex={}
        #FUNDAMENTAL COMMANDS    
        cmd_regex['move']=re.compile('^move\([0-3],(0\d{2}|1([0-7]\d|80))\)$')          #matches 'MOVE(#,###)' as servo (unsigned), angle (unsigned)
        cmd_regex['do']=re.compile('^do\(\d+\)$')                                       #matches 'DO(#)' (unsigned)
        cmd_regex['bit']=re.compile('^bit\(\d+,(high|low|1|0)\)$')                      #matches 'BIT(#,HIGH/LOW)' or 'BIT(#,1/0)' as pin (unsigned), pin_val (unsigned)
        cmd_regex['pump']=re.compile('^pump\(\d+,-?\d+\)$')                             #matches 'PUMP(#,#)' as pump_num (unsigned), num_steps (signed)
        cmd_regex['spin']=re.compile('^spin\(\d+\)$')                                   #matches 'SPIN()' as rpm(unsigned)                                               
        # cmd_regex['mckirrd']=re.compile('^mckirrd\(\)$')                                #matches 'MCKIRRD()'
        cmd_regex['irrd']=re.compile('^irrd\(\d+\)$')                                   #matches 'IRRD(#)' as dose (unsigned)

        #HIGH LEVEL COMMANDS
        cmd_regex['offset']=re.compile('^offset\(-?\d+,-?\d+,-?\d+\)$')                 #matches 'OFFSET(#,#,#)' as x,y,z (signed) - need to add angle?
        cmd_regex['moveall']=re.compile('^moveall\(-?\d+,-?\d+,-?\d+\)$')               #matches 'MOVEALL(#,#,#)' as x,y,z (signed)
        cmd_regex['shift']=re.compile('^shift\(-?\d+,-?\d+,-?\d+\)$')                   #matches 'SHIFT(#,#,#)' as x,y,z (signed)
        cmd_regex['dispense']=re.compile('^dispense\(\d+,\d+\)$')                       #matches 'DISPENSE(#,#)' as pump_num (unsigned), sample_vol (unsigned)
        cmd_regex['learnas']=re.compile('^learnas\([a-z0-9]{3,}\)$')                    #matches 'LEARNAS([string][3+])'
        cmd_regex['takepose']=re.compile('^takepose\([a-z0-9]{3,}\)$')                  #matches 'TAKEPOSE([string][3+])'
        
        #FUNCTION-LIKE COMMANDS
        cmd_regex['repeat']=re.compile('^repeat\([0-9]+,.+\)$')                         #matches 'REPEAT(#,[string])' where string should be an accepted command
        cmd_regex['macro']=re.compile('^macro\(.+\)$')                                  #matches 'MACRO(#,[string])' where string should be an existing macro file

        encoded_cmds=[]
        match=False                                                     
        for command in command_list:                                         
            for name, pattern in cmd_regex.items():
                if pattern.match(command):
                    match=True
                    if name=='repeat': #contains a command within itself that needs checked
                        match=False
                        for sub_name,sub_pattern in cmd_regex.items():
                            if sub_pattern.match(command[7:-1].split(',',1)[-1]): #checking inner command is valid
                                match=True
                                command=command[:7]+sub_name+','+command[7:] #pass through the subcommand type
                                encoded_cmd=self.compile_text(text=command[7:-1].split(',',1)[-1])
                    if name=='macro': # contains a command(s) within itself that needs checked
                        match=False
                        try:
                            match=True
                            with open('./COMMANDS/MACROS/'+filename.upper()+'.txt','r') as macro_file:
                                text = macro_file.readlines()
                                macro_file.close()
                            encoded_cmd=self.compile_text(text=text)
                        except Exception as e:
                            messagebox.showerror(parent=self.parent,title='Compiler',message='Macro error: '+e+'\nSee \'README.txt\' for help')
                    else: #command is low-level and can be passed through to the interpreter
                        pass
                    if type(encoded_cmd)==type(0):
                        encoded_cmds.append(encoded_cmd)
                    elif type(encoded_cmd)==type([]):
                        encoded_cmds.append(encoded_cmd[i] for i in range(len(encoded_cmd)))
                elif command=='': #caused by having a ; at the very end of the string
                    match=True

            if not(match):
                if len(command)>=100:
                    command=command[:100]+'[...]' #limit length of message string
                messagebox.showerror(parent=self.parent,title='Compiler',message='Unrecognised command: '+command+'\nSee \'README.txt\' for help')
                return False
            match=False

        print(encoded_cmds)
        self.save_compiled_file(encoded_cmds)
        messagebox.showinfo(parent=self.parent, title='Compiler',message='Compiled successfully')
        return True

class Executer:
    def __init__(self,parent,port=''):
        self.parent=parent
        self.port=port

    def execute_text(self):
        try:
            if self.parent.compile_text(): #if successfully compiled:
                execute_file=open(self.parent.compilepath,'r') #opens last successfully compiled file ----------ISSUE:
                cmd_list=execute_file.read().split()    #--------- if the last compilation failed this will run the
                                                        #last successful compilation which may be a different file.
                #print(cmd_list)
                BioBoxInterface.arduino.close()
                BioBoxInterface.arduino = serial.Serial(port=self.port,baudrate=115200, timeout=BioBoxInterface.timeout) #establish arduino connection to start calibration
                executer=execute_code(BioBoxInterface.arduino)
                if messagebox.askokcancel(parent=self.parent, title='Executer',message='Wait for calibration to complete'):
                    #cmd_list=[int(x)for x in cmd_list] #if commands are needed as ints rather than string
                    executer.start(cmd_list=cmd_list)
                    messagebox.showinfo(parent=self.parent, title='Executer',message='Execution complete')
        except Exception as e:
            messagebox.showerror('IOError','Unable to execute file:\n'+str(e),parent=self.parent)

    def execute_preset(self,filename=''):
        try:
            with open(filename,'r') as command_file:
                command_list=command_file.read().splitlines()
                #print(command_list)
                execute_code(self.parent.arduino).start(command_list) #implements execute_code.py
        except Exception as e:
            messagebox.showerror('IOError','Unable to execute file:\n'+str(e),parent=self.parent)

app=BioBoxInterface()
app.mainloop()
