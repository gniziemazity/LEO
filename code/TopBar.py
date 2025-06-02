from tkinter import *

from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename

from TextArea import *
from Utils import *


class TopBar:
    def __init__(self, container, block_manager, left_bar):
        self.block_manager = block_manager
        self.left_bar = left_bar
        font = ('Consolas', 12)
        

        # Create a Load button in the top bar
        self.start_button = Button(
            container,
            text='Start',
            font=font,
            bg="#50C878",
            command=self.toggle_edit,
        )
        self.start_button.pack(side=LEFT)

        # Create a Load button in the top bar
        self.new_button = Button(
            container,
            text='New',
            font=font,
            command=block_manager.new,
        )
        self.new_button.pack(side=LEFT)
        # Create a Save button in the top bar
        self.save_button = Button(
            container,
            text='Save',
            font=font,
            command=block_manager.save,
        )
        self.save_button.pack(side=LEFT)

        # Create a Load button in the top bar
        self.load_button = Button(
            container,
            text='Load',
            font=font,
            command=block_manager.load,
        )
        self.load_button.pack(side=LEFT)

        self.label = Label(container, text='PAUSED', fg='red', font=('Consolas', 17, 'bold'))
        self.label.pack(side=LEFT)
        self.label.pack_forget()



    def toggle_edit(self):
        self.block_manager.toggleStartStop()
        self.left_bar.toggle()
        if self.start_button["text"]=="Start":
            self.start_button.config(text="Stop",background="#E3735E")
            self.new_button.pack_forget()
            self.save_button.pack_forget()
            self.load_button.pack_forget()
        else:
            self.start_button.config(text="Start",background="#50C878")
            self.new_button.pack(side=LEFT)
            self.save_button.pack(side=LEFT)
            self.load_button.pack(side=LEFT)
            self.label.pack_forget()
