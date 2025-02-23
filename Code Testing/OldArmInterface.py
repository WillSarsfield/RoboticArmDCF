from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfile, asksaveasfile
from os.path import basename as basename
from pathlib import Path
import re 
from execute_code import execute_code
import time

class RobotArmInterface:

    def __init__(self):
        self.current_filename='Untitled.txt'
        self.current_compilename='Untitled_cmd.txt'
        self.compilepath=''

        self.custom_style = 'awdark'            #tkinter theme downloadable from https://sourceforge.net/projects/tcl-awthemes
        self.root = Tk()
        self.root.title("Arm Programming Interface")
        self.root.geometry('460x500')
        self.root.minsize(460,300)
        self.root.configure(background='#323232')
        self.root.tk.call('lappend', 'auto_path', './awthemes-10.4.0')
        self.root.tk.call('package', 'require', self.custom_style)
        self.style = ttk.Style()
        self.style.theme_use(self.custom_style)

        self.text_box = Text(self.root, height=5, wrap=NONE)
        self.text_box.grid(column=0, columnspan=6, row=0, sticky='nsew')
        self.scrollBary = ttk.Scrollbar(self.root, orient=VERTICAL, command=self.text_box.yview)
        self.scrollBary.grid(column=6, row=0, sticky='ns')
        self.text_box['yscrollcommand'] = self.scrollBary.set
        self.scrollBarx = ttk.Scrollbar(self.root, orient=HORIZONTAL, command=self.text_box.xview)
        self.scrollBarx.grid(column=0, columnspan=6,row=1, sticky='ew')
        self.text_box['xscrollcommand'] = self.scrollBarx.set

        self.saveButton = ttk.Button(self.root, text='Save File', command=lambda:self.save_file())
        self.saveButton.grid(column=5,columnspan=2,row=2,padx=2.5,pady=5,sticky='e')
        self.openButton = ttk.Button(self.root, text='Open File', command=lambda:self.open_file())
        self.openButton.grid(column=4,row=2,padx=2.5,pady=5)
        self.clearButton = ttk.Button(self.root, text='Clear', command=lambda:self.clear_text())
        self.clearButton.grid(column=1,row=2,padx=2.5,pady=5,sticky='w')
        self.compileButton = ttk.Button(self.root, text='Compile', command=lambda:self.compile_text())
        self.compileButton.grid(column=2,row=2,padx=2.5,pady=5,sticky='w')
        self.executeButton = ttk.Button(self.root, text='Execute', command=lambda:self.execute_text())
        self.executeButton.grid(column=3,row=2,padx=2.5,pady=5,sticky='w')

        self.root.grid_columnconfigure(0,weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.mainloop()

    def get_text(self): #get program as a string from the text box 
        text=self.text_box.get('1.0','end-1c')
        return text

    def clear_text(self): #remove all text from text box
        self.text_box.delete(1.0,'end')

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
                messagebox.showerror(parent=self.root,title='Compiler',message='Unrecognised command: '+command+'\nSee \'README.txt\' for help')    #include command description here
                return False

        #print(encoded_cmds)
        save_compiled_file(encoded_cmds)
        messagebox.showinfo(parent=self.root, title='Compiler',message='Compiled successfully')

    def execute_text(self):
        try:
            self.compile_text()
            execute_file=open(self.compilepath,'r')
            cmd_list=execute_file.read().split()
            #print(cmd_list)
            executer=execute_code()
            if messagebox.askokcancel(parent=self.root, title='Executer',message='Wait for calibration to complete'):
                #time.sleep(1)       #need to give executer time to set up
                #cmd_list=[int(x)for x in cmd_list] #if commands are needed as ints rather than string
                executer.start(cmd_list=cmd_list)
                messagebox.showinfo(parent=self.root, title='Executer',message='Execution complete')
        except Exception as e:
            messagebox.showerror('IOError','Unable to execute file:\n'+str(e),parent=self.root)

 
    def save_file(self): #opens saveasfile dialog , saves text from text box to file
        try:
            new_file=asksaveasfile(parent=self.root,initialdir='./',initialfile=self.current_filename,defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            self.current_filename=basename(new_file.name)
            if type(new_file)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
                new_file.writelines(self.get_text())
                new_file.close()
        except Exception as e:
            messagebox.showerror('IOError','Unable to save file:\n'+str(e),parent=self.root)

    def open_file(self):
        try:
            new_file=askopenfile(parent=self.root,initialdir='./',defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            self.current_filename=basename(new_file.name) #saves the name of the file that was opened, so when it is saved that name is set as default
            if type(new_file)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
                self.clear_text()
                self.text_box.insert('1.0',new_file.read())
                new_file.close()
        except Exception as e:
            messagebox.showerror('IOError','Unable to open file:\n'+str(e),parent=self.root)

application=RobotArmInterface()