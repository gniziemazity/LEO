from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename
import json
from TextArea import *
from Utils import *
import os
from ahk import AHK
import threading
import time
import shutil


class BlockManager:
    def __init__(self, root, title):
        self.root = root
        self.title=title

        self.tmp_prefix = os.getenv('LEO_PROGRAMDATA')
        if not os.path.exists(self.tmp_prefix +".\\tmp"):
            os.makedirs(self.tmp_prefix +".\\tmp")
        
        self.file_path = self.tmp_prefix + "\\tmp\\cnt.txt"
        self.sync_file_path = self.tmp_prefix + "\\tmp\\sync.txt"
        self.safe_file_path = self.tmp_prefix + "\\tmp\\safe_cnt.txt"
        self.load_file_path = self.tmp_prefix + "\\tmp\\last_load.txt"
        self.suspended_file_path = self.tmp_prefix + "\\tmp\\suspended.txt"
        
        self.last_m_time = None
        self.last_m_suspended_time = None
        self.started = False
        self.scrollbar = Scrollbar(root)
        self.scrollbar.pack(side=LEFT, fill=Y)

        if os.path.isfile(self.sync_file_path):
            os.remove(self.sync_file_path)

        self.canvas = Canvas(root, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.scrollbar.config(command=self.canvas.yview)

        block_container = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=block_container, anchor="ne")

        self.container = block_container
        ta = TextArea(self.container, self.on_enter, self.on_leave)

        # Update the canvas scroll region
        self.container.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(
            "all"), highlightthickness=0)


        # Create and start the thread
        thread = threading.Thread(target=self.check_file_changes)
        thread.start()

        try:
            with open(self.load_file_path, "r") as file:
                filepath = file.read().strip()
                self.loadFile(filepath)
        except:
            pass

    def on_cursor_change(self, event):
        if not event.state & 4:  # 4 represents the state of the Ctrl key
            return
        textAreas = self.get_text_areas()
        text_widget = event.widget

        cnt = 0
        for textArea in textAreas:
            if textArea.custom_type == "comment":
                cnt += 2
            elif textArea.custom_type == "code":
                if textArea == text_widget:
                    cursor_pos = text_widget.index(CURRENT)
                    text = text_widget.get("1.0", "end-1c")
                    line, char = cursor_pos.split(".")
                    intLine = int(line)
                    intChar = int(char)
                    cnt += specialCountUntil(text, intLine, intChar)
                    break
                else:
                    text = textArea.get("1.0", "end-1c")
                    cnt += specialCount(text)
                    cnt += 1

        with open(self.file_path, 'w') as file:
            file.write(str(cnt))
            file.close();

        with open(self.sync_file_path, 'w') as file:
            file.write(str(cnt))
            file.close();

    def emphasize(self, cnt):
        textAreas = self.get_text_areas()
        blocks = self.get_blocks()

        prevTextArea = None
        lastScrollWindow = None
        for textArea in textAreas:
            textArea.configure(state="disabled")
            if textArea.custom_type == "comment":
                if cnt > 0:
                    cnt -= 1
                    if cnt < 0:
                        textArea.configure(background='#F0E68C')  # yellow
                    elif cnt == 0:
                        textArea.configure(background='#D0C690')
                    else:
                        cnt -= 1
                        textArea.configure(background='#B5B0A0')
            elif textArea.custom_type == "code":
                textArea.bind("<Button-1>", self.on_cursor_change)
                
                text = textArea.get("1.0", "end-1c")
                textArea.tag_remove("completed", "1.0", "end")
                textArea.tag_remove("cursor", "1.0", "end")
                if cnt > 0:
                    if prevTextArea != None:
                        prevTextArea.tag_remove("cursor", "1.0", "end")
                        prevTextArea.tag_add("completed", "1.0", "end")
                    prevTextArea = textArea
                    c = specialCount(text)
                    m = min(c, cnt)
                    cc, end_line, end_char, cur_char = decreaseCount(
                        text, m)

                    end_index = f"{end_line}.{end_char}"
                    cur_index = f"{end_line}.{cur_char}"
                    if c == m:
                        textArea.tag_add("completed", "1.0", cur_index)
                    else:
                        textArea.tag_add("completed", "1.0", end_index)
                        textArea.tag_add("cursor", end_index, cur_index)
                    cnt -= m
                    lastScrollWindow = textArea
                cnt -= 1
        for b in blocks:
            for taWidget in b.winfo_children():
                if isinstance(taWidget, Text):
                    if (lastScrollWindow == taWidget):
                        self.canvas.yview_moveto(
                            (b.winfo_y()+end_line*20-self.canvas.winfo_height()/2)
                            / self.container.winfo_height()
                        )

    def check_file_changes(self):
        previous_value = None

        while True:
            if self.started:
                try:
                    m_time = os.path.getmtime(self.file_path)
                    if self.last_m_time != m_time:
                        self.last_m_time = m_time
                        try:
                           shutil.copyfile(self.file_path, self.safe_file_path)
                           with open(self.safe_file_path, "r") as file:
                              current_value = file.read().strip()
                              self.emphasize(int(current_value))
                              m_time = os.path.getmtime(self.file_path)
                        except:
                            print("err")

                    m_suspended_time = os.path.getmtime(
                        self.suspended_file_path)
                    if self.last_m_suspended_time != m_suspended_time:
                        self.last_m_suspended_time = m_suspended_time
                        with open(self.suspended_file_path, "r") as file:
                            self.paused = file.read().strip()
                            if (self.paused == "1"):
                                self.topBar.label.pack(side=LEFT)
                            else:
                                self.topBar.label.pack_forget()

                except:
                    pass
            time.sleep(0.2)

    def on_enter(self, event):
        self.canvas.bind_all("<MouseWheel>", self.scroll_text)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_leave(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.configure(yscrollcommand=None)

    def scroll_text(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def new(self):
        filepath = asksaveasfilename(defaultextension="json", filetypes=[
            ("Text Files", "*.json"), ("All Files", "*.*")])
        if not filepath:
            return

        array = []
        array.append({"type": "code", "text": "Your Code Here"})

        # Convert the texts to a JSON array
        json_array = json.dumps(array)
        with open(filepath, "w") as output_file:
            output_file.write(json_array)
            # root.title(f"Entitled - {filepath}")
        with open(self.load_file_path, "w") as output_file:
            output_file.write(filepath)
        with open(self.load_file_path, "r") as file:
            filepath = file.read().strip()
            self.loadFile(filepath)

    def save(self):
        with open(self.load_file_path, "r") as file:
            filepath = file.read().strip()

        texts = self.get_text_areas()

        array = []
        for text in texts:
            if text.custom_type == "comment":
                array.append(
                    {"type": "comment", "text": text.get("1.0", "end-1c")})
            elif text.custom_type == "code":
                array.append(
                    {"type": "code", "text": text.get("1.0", "end-1c")})

        # Convert the texts to a JSON array
        json_array = json.dumps(array)
        with open(filepath, "w") as output_file:
            output_file.write(json_array)
            # root.title(f"Entitled - {filepath}")
        with open(self.load_file_path, "w") as output_file:
            output_file.write(filepath)

    def get_text(self):
        texts = self.get_text_areas()
        all_text = ""
        for text in texts:
            if text.custom_type == "comment":
                all_text += "🛑"
                all_text += "🛑"
            elif text.custom_type == "code":
                all_text += text.get("1.0", "end-1c")+"🛑"
        return all_text

    def loadFile(self, filepath):
        if not filepath:
            return
        
        self.root.title(self.title+" : "+os.path.basename(filepath))
        with open(filepath, "r") as input_file:
            json_array = json.load(input_file)
            self.remove_blocks()
            for taInfo in json_array:
                ta = TextArea(self.container, self.on_enter, self.on_leave,
                              None, taInfo["type"], taInfo["text"])

    def load(self):
        filepath = askopenfilename(
            filetypes=[("Text Files", "*.json"), ("All Files", "*.*")])
        self.loadFile(filepath)
        with open(self.load_file_path, "w") as output_file:
            output_file.write(filepath)

    def add_emoji(self, emoji):
        focused_widget = self.container.focus_get()
        focused_widget.insert(INSERT, emoji)

    def get_blocks(self):

        # Sort the container children by y-coordinate
        sorted_blocks = sorted(
            self.container.winfo_children(),
            key=lambda widget: widget.winfo_y()
        )

        return sorted_blocks

    def get_text_areas(self):
        text_areas = []

        # Sort the container children by y-coordinate
        sorted_children = sorted(
            self.container.winfo_children(),
            key=lambda widget: widget.winfo_y()
        )

        for widget in sorted_children:
            for taWidget in widget.winfo_children():
                if isinstance(taWidget, Text):
                    text_areas.append(taWidget)

        return text_areas

    def remove_blocks(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def on_add_code(self):
        focused_widget = self.container.focus_get()
        if isinstance(focused_widget, Text):
            parent_widget = focused_widget.winfo_parent()
            ta = TextArea(self.container, self.on_enter,
                          self.on_leave, parent_widget)
        else:
            ta = TextArea(self.container, self.on_enter,
                          self.on_leave, None)

    def on_add_comment(self):
        focused_widget = self.container.focus_get()
        if isinstance(focused_widget, Text):
            parent_widget = focused_widget.winfo_parent()
            ta = TextArea(self.container, self.on_enter,
                          self.on_leave, parent_widget, "comment")
        else:
            ta = TextArea(self.container, self.on_enter,
                          self.on_leave, None, "comment")

    def on_format(self):
        focused_widget = self.container.focus_get()
        text = focused_widget.get("1.0", "end-1c")

        text = re.sub('↑►', '', text)

        for tag in ["html", "head", "body", "script", "div"]:
            text = re.sub('</'+tag+'>', '↓', text)
            text = re.sub('<'+tag+'>', '<'+tag+'>\n</'+tag+'>↑►', text)

        text = re.sub(' +', ' ', text)
        text = re.sub('\n ', '\n', text)
        text = re.sub('\n}', '↓', text)
        text = re.sub('{\n', '{\n}↑►\n', text)

        text = re.sub('\n↓', '↓', text)
        text = re.sub('↓💾', '💾', text)

        text = re.sub('↑►↓', '↑►', text)

        focused_widget.delete(1.0, END)
        focused_widget.insert(END, text)

        
    def on_format_v_code(self):
        focused_widget = self.container.focus_get()
        text = focused_widget.get("1.0", "end-1c")

        text = re.sub('↑►', '', text)

        for tag in ["html", "head", "body", "script", "style", "div"]:
            text = re.sub('</'+tag+'>', '↓', text)
            if tag in ["html","script","style"]:
               text = re.sub('<'+tag+'>', '<'+tag+'>\n</'+tag+'>↑►', text)
            else:
               text = re.sub('<'+tag+'>', '<'+tag+'>\n</'+tag+'>↑►', text)

        text = re.sub(' +', ' ', text)
        text = re.sub('\n ', '\n', text)
        text = re.sub('\n}', '↓', text)
        text = re.sub('{\n', '{\n}↑►\n', text)

        text = re.sub('\n↓', '↓', text)
        text = re.sub('↓💾', '💾', text)

        text = re.sub('↑►↓', '↑►', text)

        focused_widget.delete(1.0, END)
        focused_widget.insert(END, text)

    def on_remove(self):
        focused_widget = self.container.focus_get()
        if isinstance(focused_widget, Text):
            parent_id = focused_widget.winfo_parent()
            parent_widget = focused_widget._nametowidget(parent_id)

            parent_parent_id = parent_widget.winfo_parent()
            parent_parent_widget = parent_widget._nametowidget(
                parent_parent_id)

            siblings = parent_parent_widget.winfo_children()
            index = siblings.index(parent_widget)

            if index < len(siblings) - 1:
                sibling = siblings[index + 1]
                sibling.winfo_children()[0].focus_set()
            elif index > 0:
                sibling = siblings[index - 1]
                sibling.winfo_children()[0].focus_set()

            parent_widget.destroy()

    def toggleStartStop(self):
        if not self.started:
            self.start()
        else:
            self.stop()

    def start(self):

        chars_file_path = self.tmp_prefix + ".\\tmp\\chars.txt"
        script_file_path = self.tmp_prefix + ".\\tmp\\script.ahk"

        # GET TEXT IN CODE

        text = self.get_text()

        code = prefilter(text)
        arrayContent = ""
        for i in range(len(code)):
            c = code[i]
            arrayContent += fix(c)
            if i < len(code)-1:
                arrayContent += "\n"

        f = open(chars_file_path, "w")
        f.write(arrayContent)
        f.close()

        script = "index_file_path := \""+self.file_path+"\"\n"
        script += "chars_file_path := \""+chars_file_path+"\"\n"
        script += "suspended_file_path := \""+self.suspended_file_path+"\"\n"
        script += "sync_file_path := \""+self.sync_file_path+"\"\n"

        script += "FileRead, variable_value, %chars_file_path%\n"
        script += "longString :=variable_value\n"

        script += 'myArray := StrSplit(longString, "`n")\n'

        script += 'for index, element in myArray\n'
        script += '{\n'
        script += '\tmyArray[index] := StrReplace(element, "`r", "")\n'
        script += '}\n'

        script += "\n"

        script += "index:=1\n"
        script += "Locked := False\n"
        script += "LockDuration := 30\n"
        
        #script += "ReadIndex()\n"
        script += "\n"

        script += "\n"

        for l in "qwertyuiopasdfghjklzxcvbnm":
            script += "$"+l+"::\n"

        script += "If !Locked {\n"


        script += "\tLocked := true\n"
        
        '''
        script += "\tif (ReadIndex()) {\n"

        script += "\t\tSend, % myArray[index]\n"
        
        script += "\t\tIncreaseIndex()\n"
        '''
         
        script += "\tTryReadIndex()\n"
        script += "\tSend, % myArray[index]\n"
        script += "\tIncreaseIndex()\n"
    
        #script += "\t}\n"
        script += "\tSetTimer, UnlockInput, % -LockDuration\n"

    
        script += "\treturn\n"

        script += "} else {\n"
    
        script += "\treturn\n"

        script += "}\n"


        script += "UnlockInput:\n"
        script += "\tLocked := false\n"
        script += "\tSetTimer, UnlockInput, off\n"
        script += "\tReturn\n"
        '''
        script += "\tReadIndex()\n"


        script += "\tSendInput, % myArray[index]\n"
        script += "\tIncreaseIndex()\n"
        script += "\treturn\n"
        script += "}\n"
        script += "Else\n"
        script += "\treturn\n"
        script += "\n"
        '''
        script += "Suspended := False\n"
        script += "\n"
        script += "^p::\n"
        script += "\tSuspend\n"
        script += "\tSuspended := !Suspended\n"
        script += "\tSetSuspended(Suspended)\n"

        script += "\tReturn\n\n"

        script += "^r::Reload\n"
        script += "return\n"
        script += "\n"

        script += "^Left::DecreaseIndex()\n"
        script += "^Right::IncreaseIndex()\n"
        script += "\n"

        script += "IncreaseIndex()\n"
        script += "{\n"
        script += "\tglobal index\n"
        script += "\tSetIndex(index+1)\n"
        script += "}\n"
        script += "\n"

        script += "DecreaseIndex()\n"
        script += "{\n"
        script += "\tglobal index\n"
        script += "\tSetIndex(index-1)\n"
        script += "}\n"
        script += "\n"

        script += "SetIndex(newIndex)\n"
        script += "{\n"
        script += "\tglobal index\n"
        script += "\tindex:=newIndex\n"
        script += "\tglobal index_file_path\n"
        script += "\tFileDelete, %index_file_path%\n"
        script += "\tFileAppend, %index%, %index_file_path%\n"
        script += "}\n"
        script += "\n"

        script += "SetSuspended(val)\n"
        script += "{\n"
        script += "\tglobal suspended_file_path\n"
        script += "\tFileDelete, %suspended_file_path%\n"
        script += "\tFileAppend, %val%, %suspended_file_path%\n"
        script += "}\n"
        script += "\n"

        script += "TryReadIndex()\n"
        script += "{\n"
        script += "\tglobal index\n"
        script += "\tglobal sync_file_path\n"
        script += "\tFileRead, variable_value, %sync_file_path%\n"
        script += '\tif RegExMatch(variable_value, "^\d+$") {\n'
        script += "\t\tindex:=variable_value\n"
        script += "\t\tFileDelete, %sync_file_path%\n"
        script += "\t\treturn true\n"
        script += "\t}\n"
        script += "\treturn false\n"
        script += "}"


        f = open(script_file_path, "w")
        f.write(script)
        f.close()

        # Set the variable value
        variable_value = "1"

        # Write the variable value to the file
        with open(self.file_path, 'w') as file:
            file.write(variable_value)
            file.close()

        with open(self.suspended_file_path, 'w') as file:
            file.write("0")

        # Run the AHK script
        def long_running_process():
            os.system(script_file_path)

        thread = threading.Thread(target=long_running_process)
        thread.start()

        self.started = True

    def stop(self):
        os.system("kill.bat")
        textAreas = self.get_text_areas()
        for textArea in textAreas:
            textArea.configure(state="normal")
            if textArea.custom_type == "comment":
                textArea.configure(background='#F0E68C')  # yellow
            elif textArea.custom_type == "code":
                textArea.tag_remove("completed", "1.0", "end")
                textArea.tag_remove("cursor", "1.0", "end")
        self.started = False
