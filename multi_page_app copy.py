from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfile, asksaveasfile
from os.path import basename as basename
from pathlib import Path
import re 
from execute_code import execute_code
import time

class MultiPageApp(Tk):

    def __init__(self, *args, **kwargs):

        Tk.__init__(self,*args,**kwargs)
        self.custom_style = 'awdark'            #tkinter theme downloadable from https://sourceforge.net/projects/tcl-awthemes
        self.geometry('460x500')
        self.minsize(460,300)
        self.title('Robot Arm Interface')
        self.configure(background='#323232')
        self.tk.call('lappend', 'auto_path', './awthemes-10.4.0')
        self.tk.call('package', 'require', self.custom_style)
        self.style = ttk.Style()
        self.style.theme_use(self.custom_style)
        container=Frame(self)

        container.pack(fill='both',expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        self.frames = {}

        for F in (StartPage, TextEditor, ReadMe):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0,column=0,sticky='nsew')

        self.show_frame(StartPage)

    def show_frame(self,cont):

        frame = self.frames[cont]
        frame.tkraise()

class StartPage(Frame):

    def __init__(self,parent,controller):
        Frame.__init__(self,parent)

        self.header_frame = Frame(self)#contains window swapping buttons
        self.center_frame = Frame(self)#contains robotic arm movement presets
        self.header_frame.grid(row=0,column=0,sticky='nsew')
        self.center_frame.grid(row=1,column=0,sticky='nsew')
        self.grid_columnconfigure(0,weight=1)   

        label = Label(self.header_frame,text='Start Page')
        label.grid(column=0,row=0,columnspan=3)
        button1 = ttk.Button(self.header_frame, text='Start Page', command=lambda: controller.show_frame(StartPage))
        button1.grid(column=0,row=1,sticky='ew')
        button2 = ttk.Button(self.header_frame, text='Text Editor', command=lambda: controller.show_frame(TextEditor))
        button2.grid(column=1,row=1,sticky='ew')
        button3 = ttk.Button(self.header_frame, text='Help Page', command=lambda: controller.show_frame(ReadMe))
        button3.grid(column=2,row=1,sticky='ew')

        self.header_frame.grid_columnconfigure(0,weight=1)
        self.header_frame.grid_columnconfigure(1,weight=1)
        self.header_frame.grid_columnconfigure(2,weight=1)
        self.header_frame.grid_rowconfigure(2, weight=1)

class TextEditor(Frame):
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)

        self.current_filename='Untitled.txt'
        self.current_compilename='Untitled_cmd.txt'
        self.compilepath=''

        self.header_frame = Frame(self)#frame containing window swapping buttons
        self.center_frame = Frame(self)#frame containing textbox and scrollbars
        self.footer_frame = Frame(self)#frame containing file manipulation buttons
        self.header_frame.grid(row=0,column=0,sticky='nsew')
        self.center_frame.grid(row=1,column=0,sticky='nsew')
        self.footer_frame.grid(row=2,column=0,sticky='nsew')

        label = Label(self.header_frame,text='Text Editor')
        label.grid(column=0,row=0,columnspan=3) 
        button1 = ttk.Button(self.header_frame, text='Start Page', command=lambda: controller.show_frame(StartPage))
        button1.grid(column=0,row=1,sticky='ew')
        button2 = ttk.Button(self.header_frame, text='Text Editor', command=lambda: controller.show_frame(TextEditor))
        button2.grid(column=1,row=1,sticky='ew')
        button3 = ttk.Button(self.header_frame, text='Help Page', command=lambda: controller.show_frame(ReadMe))
        button3.grid(column=2,row=1,sticky='ew')

        self.header_frame.grid_columnconfigure(0,weight=1)
        self.header_frame.grid_columnconfigure(1,weight=1)
        self.header_frame.grid_columnconfigure(2,weight=1)

        self.center_frame.text_box = Text(self.center_frame, height=5, wrap=NONE)
        self.center_frame.text_box.grid(row=0,column=0,sticky='nsew')
        scrollBary = ttk.Scrollbar(self.center_frame, orient=VERTICAL, command=self.center_frame.text_box.yview)
        scrollBary.grid(row=0,column=1,sticky='ns')
        self.center_frame.text_box['yscrollcommand'] = scrollBary.set
        scrollBarx = ttk.Scrollbar(self.center_frame, orient=HORIZONTAL, command=self.center_frame.text_box.xview)
        scrollBarx.grid(row=1,column=0,sticky='ew')
        self.center_frame.text_box['xscrollcommand'] = scrollBarx.set

        self.center_frame.grid_columnconfigure(0,weight=1)
        self.center_frame.grid_rowconfigure(0,weight=1)
        
        saveButton = ttk.Button(self.footer_frame, text='Save File', command=lambda:self.save_file())
        saveButton.grid(column=4,row=0,sticky='e',padx=2.5,pady=5)
        openButton = ttk.Button(self.footer_frame, text='Open File', command=lambda:self.open_file())
        openButton.grid(column=3,row=0,sticky='e',padx=2.5,pady=5)
        clearButton = ttk.Button(self.footer_frame, text='Clear', command=lambda:self.clear_text())
        clearButton.grid(column=0,row=0,sticky='e',padx=2.5,pady=5)
        compileButton = ttk.Button(self.footer_frame, text='Compile', command=lambda:self.compile_text())
        compileButton.grid(column=1,row=0,sticky='e',padx=2.5,pady=5)
        executeButton = ttk.Button(self.footer_frame, text='Execute', command=lambda:self.execute_text())
        executeButton.grid(column=2,row=0,sticky='e',padx=2.5,pady=5)

        self.footer_frame.grid_rowconfigure(0,weight=1)
        self.footer_frame.grid_columnconfigure(0,weight=1)

        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1, weight=1)

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

    def execute_text(self):
        try:
            self.compile_text()
            execute_file=open(self.compilepath,'r')
            cmd_list=execute_file.read().split()
            #print(cmd_list)
            executer=execute_code()
            if messagebox.askokcancel(parent=self, title='Executer',message='Wait for calibration to complete'):
                #time.sleep(1)       #need to give executer time to set up
                #cmd_list=[int(x)for x in cmd_list] #if commands are needed as ints rather than string
                executer.start(cmd_list=cmd_list)
                messagebox.showinfo(parent=self, title='Executer',message='Execution complete')
        except Exception as e:
            messagebox.showerror('IOError','Unable to execute file:\n'+str(e),parent=self)

    def save_file(self): #opens saveasfile dialog , saves text from text box to file
        try:
            new_file=asksaveasfile(parent=self,initialdir='./',initialfile=self.current_filename,defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            self.current_filename=basename(new_file.name)
            if type(new_file)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
                new_file.writelines(self.get_text())
                new_file.close()
        except Exception as e:
            messagebox.showerror('IOError','Unable to save file:\n'+str(e),parent=self)

    def open_file(self):
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
        label = Label(self,text='Help Page')
        label.grid(column=0,row=0,columnspan=3)

        button1 = ttk.Button(self, text='Start Page', command=lambda: controller.show_frame(StartPage))
        button1.grid(column=0,row=1,sticky='ew')

        button2 = ttk.Button(self, text='Text Editor', command=lambda: controller.show_frame(TextEditor))
        button2.grid(column=1,row=1,sticky='ew')
    
        button3 = ttk.Button(self, text='Help Page', command=lambda: controller.show_frame(ReadMe))
        button3.grid(column=2,row=1,sticky='ew')

        readme_text = Label(self,text='help')
        readme_text.grid(row=2,column=0,columnspan=3)

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_rowconfigure(2, weight=1)
        
app=MultiPageApp()
app.mainloop()
