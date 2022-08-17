from tkinter import *
from tkinter import ttk,messagebox,font
from tkinter.filedialog import askopenfile, asksaveasfile
from os.path import basename as basename
from pathlib import Path
import re 
from execute_code import execute_code
from CommandInterpreter import CommandInterpreter
import serial
import time

class BioBoxInterface(Tk):

    timeout=.1005
    arduino=serial.Serial()
    def __init__(self, *args, **kwargs):
        #-----!!!need to choose port based on connection!!!-------
        #self.arduinoPort = '/dev/cu.usbmodem1301' #for mac - check bottom of arduino editor and modify 
        self.arduinoPort = 'COM5' #for windows - may be a different number
        #---------------------------------------------------------

        self.current_filename='./COMMANDS/Untitled.txt' #relevant to execute_text, compile_text, open_file, save_file methods

        Tk.__init__(self,*args,**kwargs)
        self.title('BioBox Interface')

        #setting up arduino comms
        try: #attempt to establish arduino connection
            self.arduino.close()
            self.arduino = serial.Serial(port=self.arduinoPort,baudrate=115200, timeout=self.timeout)
            time.sleep(2)
        except Exception as e:
            messagebox.showerror('IOError','Unable to establish connection:\n'+str(e),parent=self)
            #self.destroy()

        self.compiler=Compiler(self)
        self.executer=Executer(self,connection = self.arduino)     

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
            '<< θ',  #4
            'x >>',  #5
            'y >>',  #6
            'z >>',  #7
            'θ >>'   #8
        ]

        presets_matrix = {      #names of compiled files corresponding to each button, change these to change what file the button executes
            0:'./COMMANDS/RESET.txt',
            1:'./COMMANDS/SHFTDWN_X.txt',
            2:'./COMMANDS/SHFTDWN_Y.txt',
            3:'./COMMANDS/SHFTDWN_Z.txt',
            4:'./COMMANDS/SHFTDWN_T.txt',
            5:'./COMMANDS/SHFTUP_X.txt',
            6:'./COMMANDS/SHFTUP_Y.txt',
            7:'./COMMANDS/SHFTUP_Z.txt',
            8:'./COMMANDS/SHFTUP_T.txt'
        }

        xentry_text,yentry_text,zentry_text,tentry_text=[StringVar() for i in range(4)] #setting up variable text for the text entries
        xentry_text.set('0')
        yentry_text.set('0')
        zentry_text.set('0')
        tentry_text.set('90')

        #setting up preset buttons, change the command_names text and presets_matrix filename to execute different programs
        command1 = ttk.Button(self.footer_frame,text=command_names[0],cursor='exchange',command=lambda:[self.execute_preset(presets_matrix[0]),xentry_text.set('0'),yentry_text.set('0'),zentry_text.set('0'),tentry_text.set('90')])
        command1.grid(column=0,row=0,padx=2.5,pady=5,sticky='nsew') #this first one is actually in the footer (reset button)

        command2 = ttk.Button(self.center_frame,text=command_names[1],cursor='cross',command=lambda:[self.execute_preset(presets_matrix[1]),xentry_text.set(str(int(xentry_text.get())-1))])
        command2.grid(column=0,row=0,padx=5,pady=2.5,sticky='nse')
        command3 = ttk.Button(self.center_frame,text=command_names[2],cursor='cross',command=lambda:[self.execute_preset(presets_matrix[2]),yentry_text.set(str(int(yentry_text.get())-1))])
        command3.grid(column=0,row=1,padx=5,pady=2.5,sticky='nse')
        command4 = ttk.Button(self.center_frame,text=command_names[3],cursor='cross',command=lambda:[self.execute_preset(presets_matrix[3]),zentry_text.set(str(int(zentry_text.get())-1))])
        command4.grid(column=0,row=2,padx=5,pady=2.5,sticky='nse')
        command5 = ttk.Button(self.center_frame,text=command_names[4],cursor='cross',command=lambda:[self.execute_preset(presets_matrix[4]),tentry_text.set(str(int(tentry_text.get())-1))])
        command5.grid(column=0,row=3,padx=5,pady=2.5,sticky='nse')

        command6 = ttk.Button(self.center_frame,text=command_names[5],cursor='cross',command=lambda:[self.execute_preset(presets_matrix[5]),xentry_text.set(str(int(xentry_text.get())+1))])
        command6.grid(column=2,row=0,padx=5,pady=2.5,sticky='nsw')
        command7 = ttk.Button(self.center_frame,text=command_names[6],cursor='cross',command=lambda:[self.execute_preset(presets_matrix[6]),yentry_text.set(str(int(yentry_text.get())+1))])
        command7.grid(column=2,row=1,padx=5,pady=2.5,sticky='nsw')
        command8 = ttk.Button(self.center_frame,text=command_names[7],cursor='cross',command=lambda:[self.execute_preset(presets_matrix[7]),zentry_text.set(str(int(zentry_text.get())+1))])
        command8.grid(column=2,row=2,padx=5,pady=2.5,sticky='nsw')
        command9 = ttk.Button(self.center_frame,text=command_names[8],cursor='cross',command=lambda:[self.execute_preset(presets_matrix[8]),tentry_text.set(str(int(tentry_text.get())+1))])
        command9.grid(column=2,row=3,padx=5,pady=2.5,sticky='nsw')

        xentry,yentry,zentry,tentry=[ttk.Entry() for i in range(4)] #setting up text entry boxes
        entry_list = {
            xentry:xentry_text, yentry:yentry_text, zentry:zentry_text, tentry:tentry_text
            }
        for index, (entry, entry_text) in enumerate(entry_list.items()):
            entry = ttk.Entry(self.center_frame,justify='center',textvariable=entry_text)
            entry.grid(column=1,row=index,padx=2.5,pady=2.5,sticky='ew')

        self.center_frame.grid_columnconfigure((0,2),weight=1)
        self.center_frame.grid_rowconfigure((0,1,2,3),weight=1)

        # other neccessary functions, unlikely to need changed
        learn_pos_btn = ttk.Button(self.footer_frame,text='Learn As..',command=lambda:self.save_position(xentry_text.get(), yentry_text.get(), zentry_text.get(), tentry_text.get()))
        learn_pos_btn.grid(column=2,row=0,padx=2.5,pady=5,sticky='nsew')
        move_btn = ttk.Button(self.footer_frame,text='Move',command=lambda:self.move_to_coords(xentry_text.get(), yentry_text.get(), zentry_text.get(), tentry_text.get()))
        move_btn.grid(column=1,row=0,padx=2.5,pady=5,sticky='nsew')

        self.footer_frame.grid_columnconfigure((0,1,2),weight=1)
        self.footer_frame.grid_rowconfigure(0,weight=1)

        self.grid_columnconfigure(0,weight=1) #position of frames within PresetPage
        self.grid_rowconfigure(1,weight=1)

    def execute_preset(self, filename='./COMMANDS/RESET.txt'): #reads commands from _cmd.txt file and sends them to the arduino
        with open(filename,'r') as preset_file: #need to recompile every time if using SHIFT or another relative command
            text = preset_file.read()
            preset_file.close()
        cmd_lst=self.compiler.compile_text(text=text)
        self.compiler.save_compiled_file(cmd_lst,filename)
        self.executer.execute_without_compile(filename.replace('.txt','_cmd.txt'))

    def save_position(self,x,y,z,tilt):
        try:
            x,y,z=int(x),int(y),int(z)
            pos_file=asksaveasfile(parent=self,initialdir='./SAVED_POSITIONS',initialfile='POS1.txt',defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            if type(pos_file)!=type(None): #cancelling the dialog box returns nonetype, file should only be saved if one was specified
                pos_file.write('%s,%s,%s,%s'%(x,y,z,tilt))
                pos_file.close()            
        except Exception as e:
            messagebox.showerror('IOError','Unable to save position:\n'+str(e),parent=self)

    def move_to_coords(self,x,y,z,tilt):
        command='moveall(%s,%s,%s,%s);'%(x,y,z,tilt)



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
        executeButton = ttk.Button(self.footer_frame, text='Execute', command=lambda:self.execute_text(controller.arduinoPort))
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
        cmd_text = self.compiler.compile_text(text=self.get_text())
        self.controller.current_filename = self.compiler.save_compiled_file(cmd_text=cmd_text, filepath=self.controller.current_filename)


    def execute_text(self,port):
        self.executer.execute_with_compile(self.controller.current_filename)

    def save_file(self): #opens saveasfile dialog, saves text from text box to file
        try:
            new_file=asksaveasfile(parent=self,initialdir='./COMMANDS',initialfile=self.controller.current_filename,defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            self.controller.current_filename=new_file.name
            if type(new_file)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
                new_file.writelines(self.get_text())
                new_file.close()
        except Exception as e:
            messagebox.showerror('IOError','Unable to save file:\n'+str(e),parent=self)

    def open_file(self): #opens askopenfile dialog, sets textbox text to file contents
        try:
            new_file=askopenfile(parent=self,initialdir='./COMMANDS',defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            self.controller.current_filename=new_file.name #saves the name of the file that was opened, so when it is saved that name is set as default
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
        self.interpreter=CommandInterpreter(0,0,0) #initial offset values

    def get_raw(self,command,cmd_type=''):
        encoded_cmds = self.interpreter.get_encoded_command(command=command,cmd_type=cmd_type)
        return encoded_cmds

    def save_compiled_file(self,cmd_text,filepath):
        compilename=filepath.replace('.txt','_cmd.txt') #can be replaced - this is to distinguish between compiled and uncompiled files
        savefile=open(compilename,'w')
        if type(savefile)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
            savefile.write(cmd_text)
            savefile.close()
        return filepath

    def is_valid(self,command_list):
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
        cmd_regex['moveall']=re.compile('^moveall\(-?\d+,-?\d+,-?\d+,\d+\)$')           #matches 'MOVEALL(#,#,#,#)' as x,y,z (signed), tilt(unsigned)
        cmd_regex['shift']=re.compile('^shift\(-?\d+,-?\d+,-?\d+,-?\d+\)$')             #matches 'SHIFT(#,#,#,#)' as x,y,z,tilt (signed)
        cmd_regex['dispense']=re.compile('^dispense\(\d+,\d+\)$')                       #matches 'DISPENSE(#,#)' as pump_num (unsigned), sample_vol (unsigned)
        cmd_regex['learnas']=re.compile('^learnas\([a-z0-9]{3,}\)$')                    #matches 'LEARNAS([string][3+])'
        cmd_regex['takepose']=re.compile('^takepose\([a-z0-9]{3,}\)$')                  #matches 'TAKEPOSE([string][3+])'
        
        #FUNCTION-LIKE COMMANDS
        cmd_regex['repeat']=re.compile('^repeat\([0-9]+,.+\)$')                         #matches 'REPEAT(#,[string])' where string should be an accepted command
        cmd_regex['macro']=re.compile('^macro\(.+\)$')                                  #matches 'MACRO(#,[string])' where string should be an existing macro file

        match = False
        for command in command_list:
            for name, pattern in cmd_regex.items():
                if pattern.match(command):
                    match=True
                    if name == 'repeat':
                        match = False
                        for sub_name,sub_pattern in cmd_regex.items():
                            if self.is_valid([command[7:-1].split(',',1)[-1]]):
                                match = True
                    elif name == 'macro':
                        match=False
                        filename=command[6:-1]
                        try:
                            with open('./COMMANDS/MACROS/'+filename.upper()+'.txt','r') as macro_file:
                                text = macro_file.read()
                                macro_file.close()
                            text=''.join(text.split()).lower()
                            command_list=text.split(';')
                            match=self.is_valid(command_list)
                        except Exception as e:
                            messagebox.showerror(parent=self.parent,title='Compiler',message='Macro error: '+e+'\nSee \'README.txt\' for help')
                elif command == '': #caused by .split() returning '' when a semicolon is the last character of a string
                    match = True
            if not(match):
                if len(command)>=100:
                    command=command[:100]+'[...]' #limit length of message string
                messagebox.showerror(parent=self.parent,title='Compiler',message='Unrecognised command: '+command+'\nSee \'README.txt\' for help')
                return False
        return True

    def compile_text(self,text=''):
        text=''.join(text.split()).lower() #formatting text: remove whitespace and convert to lowercase
        command_list=text.split(';') #splits strings into commands separated by ';'
        encoded_cmds=''
        if self.is_valid(command_list):
            for command in command_list:
                cmd_type=command.split('(',1)[0]
                enc_cmd = self.get_raw(command,cmd_type=cmd_type)
                if type(enc_cmd)==int:
                    encoded_cmds+=str(enc_cmd)
                elif type(enc_cmd)==list:
                    for cmd in enc_cmd:
                        encoded_cmds += str(cmd)+'\n'
                    
        return encoded_cmds
        

class Executer:
    def __init__(self,parent,connection=None):
        self.connection=connection
        self.parent=parent

    def execute_with_compile(self,filename):
        try:
            with open(filename,'r') as compiled_file:
                text = compiled_file.read()
                compiled_file.close()
            cmd_text = self.parent.compiler.compile_text(text=text) #if successfully compiled:
            self.parent.current_filename = self.parent.compiler.save_compiled_file(cmd_text,filepath=filename)
            with open(filename.replace('.txt','_cmd.txt'),'r') as compiled_file:
                comp_cmds=compiled_file.read()
                compiled_file.close()
            comp_cmds=comp_cmds.split('\n')
            executer=execute_code(self.parent.arduino)
            if messagebox.askokcancel(parent=self.parent, title='Executer',message='Compile complete: Execute file %s?'%(filename)):
                executer.start(cmd_list=comp_cmds)
                messagebox.showinfo(parent=self.parent, title='Executer',message='Execution complete: %s'%(filename))
        except Exception as e:
            messagebox.showerror('IOError','Unable to execute file %s:\n%s'%(filename,str(e)),parent=self.parent)

    def execute_without_compile(self,filename):
        try:
            with open(filename,'r') as command_file:
                command_list=command_file.read().splitlines()
                #print(command_list)
                execute_code(self.parent.arduino).start(command_list) #implements execute_code.py
        except Exception as e:
            messagebox.showerror('IOError','Unable to execute file:\n'+str(e),parent=self.parent)

app=BioBoxInterface()
app.mainloop()
