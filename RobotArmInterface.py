from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfile, asksaveasfile
from os.path import basename as basename

class RobotArmInterface():
    current_filename='Untitled.txt'

    def __init__(self):
        custom_style = 'awdark'
        self.root = Tk()
        self.root.title("Arm Programming Interface")
        self.root.geometry('300x400')
        self.root.minsize(300,300)                                   #get the minimum size of the window to work
        self.root.tk.call('lappend', 'auto_path', './awthemes-10.4.0')
        self.root.tk.call('package', 'require', custom_style)
        self.style = ttk.Style()
        self.style.theme_use(custom_style)

        self.text_box = Text(self.root, height=5, wrap=NONE)
        self.text_box.grid(column=0, columnspan=3, row=0, sticky='nsew')
        self.scrollBary = ttk.Scrollbar(self.root, orient=VERTICAL, command=self.text_box.yview)
        self.scrollBary.grid(column=3, row=0, sticky='ns')
        self.text_box['yscrollcommand'] = self.scrollBary.set
        self.scrollBarx = ttk.Scrollbar(self.root, orient=HORIZONTAL, command=self.text_box.xview)
        self.scrollBarx.grid(column=0, columnspan=3,row=1, sticky='ew')
        self.text_box['xscrollcommand'] = self.scrollBarx.set

        self.saveButton = ttk.Button(self.root, text='Save File', command=lambda:self.save_file())
        self.saveButton.grid(column=2,columnspan=2,row=2,padx=5,pady=5,sticky='e')
        self.openButton = ttk.Button(self.root, text='Open File', command=lambda:self.open_file())
        self.openButton.grid(column=1,row=2,pady=5)
        self.clearButton = ttk.Button(self.root, text='Clear Text', command=lambda:self.clear_text())
        self.clearButton.grid(column=0,row=2,padx=5,pady=5,sticky='w')

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.mainloop()

    def get_text(self): #get program as a string from the text box 
        text=self.text_box.get('1.0','end-1c')
        return text
    
    def clear_text(self): #remove all text from text box
        self.text_box.delete(1.0,'end')
 
    def save_file(self): #opens saveasfile dialog , saves text from text box to file
        global current_filename
        new_file=asksaveasfile(parent=self.root,initialdir='./',initialfile=current_filename,defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
        if type(new_file)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
            new_file.writelines(self.get_text())
            new_file.close()

    def open_file(self):
        global current_filename
        new_file=askopenfile(parent=self.root,initialdir='./',defaultextension='.txt',filetypes=[('All Files','*.*'),('Text Documents','*.txt')])
        current_filename=basename(new_file.name)
        if type(new_file)!=type(None): #cancelling the dialog box returns nonetype, text should only be replaced if there is a file to replace it
            self.clear_text()
            self.text_box.insert('1.0',new_file.read())
            new_file.close()


application=RobotArmInterface()