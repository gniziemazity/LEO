from tkinter import *


class TextArea:
    def __init__(self, container, on_enter, on_leave, after=None, type="code", text=None):
        self.type = type
        bg = "white"
        if type == "comment":
            bg = "yellow"

        self.frame = Frame(container, padx=5, pady=2)  
        if after != None:
            self.frame.pack(after=after, fill=BOTH, expand=True)
        else:
            self.frame.pack(fill=BOTH, expand=True)

        self.text_area = Text(
            self.frame,
            height=2,
            width=58,
            background=bg,
            font=('Consolas', 10)
        )

        self.text_area.tag_configure(
            "completed", background="#D8D8D8", foreground="#505050")
        self.text_area.tag_configure(
            "cursor", background="#0000CD", foreground="#eeeeee")

        if text != None:
            self.set_text(text)

        bindtags = list(self.text_area.bindtags())
        bindtags.insert(1, "custom")
        self.text_area.bindtags(tuple(bindtags))

        self.text_area.custom_type = type

        self.text_area.pack(fill=BOTH, expand=True)

        self.frame.bind("<Enter>", on_enter)
        self.frame.bind("<Leave>", on_leave)

        def on_focus_in(event):
            self.text_area.config(highlightcolor="blue", highlightthickness=2)

        def on_focus_out(event):
            self.text_area.config(highlightcolor="black", highlightthickness=2)

        self.text_area.bind("<FocusIn>", on_focus_in)
        self.text_area.bind("<FocusOut>", on_focus_out)

        self.text_area.focus_set()

        def adjust_text_height(event):
            text_widget = event.widget
            text_widget.configure(
                height=text_widget.index("end").split(".")[0])

        self.text_area.bind("<<Modified>>", adjust_text_height)
        self.text_area.bind("<Key>", adjust_text_height)
        container.update_idletasks()

    def get_text(self):
        return self.text_area.get(1.0, END)

    def set_text(self, text):
        self.text_area.delete(1.0, END)
        self.text_area.insert(END, text)