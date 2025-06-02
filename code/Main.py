from tkinter import *
from TextArea import *
from TopBar import *
from RightBar import *
from BlockManager import *
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

title="LEO (Lupsakkaasti ja Ehjästi Ohjelmoit)"
root = Tk()
root.geometry(f'600x800')
root.title(title)
root.resizable(False, True)

top_bar_container = Frame(root, padx=5, pady=5)
top_bar_container.pack(fill=X)

right_bar_container = Frame(root, padx=5, pady=5)
right_bar_container.pack(side=RIGHT, fill=BOTH, expand=False)

block_manager = BlockManager(root,title)
right_bar = RightBar(right_bar_container, block_manager, root)
top_bar = TopBar(top_bar_container, block_manager, right_bar)
block_manager.topBar=top_bar



root.mainloop()
