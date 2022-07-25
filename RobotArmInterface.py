from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfile, asksaveasfile
from os.path import basename as basename

class RobotArmInterface:

    def __init__(self):
        self.current_filename='Untitled.txt'
        self.custom_style = 'awdark'
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

        self.root.grid_columnconfigure(0,weight=2) #what does this actually do
        self.root.grid_rowconfigure(0, weight=1)
        self.root.mainloop()

    def get_text(self): #get program as a string from the text box 
        text=self.text_box.get('1.0','end-1c')
        return text
    
    def clear_text(self): #remove all text from text box
        self.text_box.delete(1.0,'end')
        
    def compile_text(self): #converts text into format ready for serial comms
        text=self.get_text()
        text=text.replace('\n','')

    def execute_text(self):
        pass
 
    def save_file(self): #opens saveasfile dialog , saves text from text box to file
        try:
            new_file=asksaveasfile(parent=self.root,initialdir='./',initialfile=self.current_filename,defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            self.current_filename=basename(newfile.name)
            if type(new_file)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
                new_file.writelines(self.get_text())
                new_file.close()
        except:
            messagebox.showerror('IOError','Unable to save file',parent=self.root)

    def open_file(self):
        try:
            new_file=askopenfile(parent=self.root,initialdir='./',defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
            self.current_filename=basename(new_file.name) #saves the name of the file that was opened, so when it is saved that name is set as default
            if type(new_file)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
                self.clear_text()
                self.text_box.insert('1.0',new_file.read())
                new_file.close()
        except:
            messagebox.showerror('IOError','Unable to open file',parent=self.root)

application=RobotArmInterface()