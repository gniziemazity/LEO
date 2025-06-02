from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename
from tkinter import ttk

class RightBar:
    def __init__(self, container, block_manager, root):
        self.container = container
        self.root=root
        font = ('Consolas', 12)
        
        b = Button(
            container,
            text='+',
            font=font,
            command=block_manager.on_add_code
        )
        b.pack(side=TOP, fill=X)
        b = Button(
            container,
            text='+',
            bg='#F0E68C',
            font=font,
            command=block_manager.on_add_comment
        )
        b.pack(side=TOP, fill=X)
        
        sep = ttk.Separator(container)
        sep.pack(side=TOP, fill=X,pady=10)

        b = Button(
            container,
            text='-',
            bg='#E3735E',
            font=font,
            command=block_manager.on_remove
        )
        b.pack(side=TOP, fill=X)

        sep = ttk.Separator(container)
        sep.pack(side=TOP, fill=X,pady=10)

        b = Button(
            container,
            text='F',
            bg='#0096FF',
            font=font,
            command=block_manager.on_format
        )
        b.pack(side=TOP, fill=X)
        b = Button(
            container,
            text='V',
            bg='#0096FF',
            font=font,
            command=block_manager.on_format_v_code
        )
        b.pack(side=TOP, fill=X)

        sep = ttk.Separator(container)
        sep.pack(side=TOP, fill=X,pady=10)

        b = Button(
            container,
            text='💾',
            font=font,
            command=lambda: block_manager.add_emoji("💾")
        )
        b.pack(side=TOP, fill=X)
        b = Button(
            container,
            text='↢',
            font=font,
            command=lambda: block_manager.add_emoji("↢")
        )
        b.pack(side=TOP, fill=X)
        b = Button(
            container,
            text='←',
            font=font,
            command=lambda: block_manager.add_emoji("←")
        )
        b.pack(side=TOP, fill=X)
        b = Button(
            container,
            text='↓',
            font=font,
            command=lambda: block_manager.add_emoji("↓")
        )
        b.pack(side=TOP, fill=X)
        b = Button(
            container,
            text='→',
            font=font,
            command=lambda: block_manager.add_emoji("→")
        )
        b.pack(side=TOP, fill=X)
        b = Button(
            container,
            text='↑',
            font=font,
            command=lambda: block_manager.add_emoji("↑")
        )
        b.pack(side=TOP, fill=X)
        b = Button(
            container,
            text='►',
            font=font,
            command=lambda: block_manager.add_emoji("►")
        )
        b.pack(side=TOP, fill=X)
        b = Button(
            container,
            text='◄',
            font=font,
            command=lambda: block_manager.add_emoji("◄")
        )
        b.pack(side=TOP, fill=X)
        b = Button(
            container,
            text='⇩',
            font=font,
            command=lambda: block_manager.add_emoji("⇩")
        )
        b.pack(side=TOP, fill=X)
        b = Button(
            container,
            text='―',
            font=font,
            command=lambda: block_manager.add_emoji("―")
        )
        b.pack(side=TOP, fill=X)
        

    def toggle(self):
        self.toggle_frame_visibility(self.container)

    def toggle_frame_visibility(self, frame):
        current_height = self.root.winfo_height()
        if frame.winfo_viewable():
            frame.pack_forget()
            self.root.geometry(f'560x{current_height}')
        else:
            frame.pack(side=RIGHT, fill=BOTH, expand=False)
            self.root.geometry(f'600x{current_height}')
