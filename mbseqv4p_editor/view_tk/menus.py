from tkinter import *
from tkinter.ttk import *

from ..helpers import *

logger = logging.getLogger(f"{__name__:{LOGW_NAME}}")


class SDCardMenu(Menu):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.add_command(
            label="Open",
            command=self.open_sdcard,
            accelerator="Cmd+O",
            underline=0,
        )
        self.add_command(
            label="Save", command=self.save_sdcard, accelerator="Cmd+S", underline=0
        )
        self.add_command(
            label="Save As",
            command=self.save_as_sdcard,
            accelerator="Shift-Cmd+S",
            underline=0,
        )

    # self.add_separator()
    # self.add_command(
    #     label="Quit",
    #     command=self.quit,
    #     accelerator='Cmd+Q',
    #     underline=0,
    # )

    def open_sdcard(self):
        name = filedialog.askdirectory()
        self.controller.do("open_sdcard", name)

    def save_sdcard(self):
        # name = filedialog.asksavefilename()
        self.controller.do("save_sdcard")

    def save_as_sdcard(self):
        name = filedialog.asksaveasfilename()
        self.controller.do("save_sdcard", name)

    # def quit(self):
    #     self.controller.do('quit')


class SessionMenu(Menu):
    def __init__(self, parent, controller):
        super().__init__(
            parent,
            postcommand=self.update_sessions,
        )
        self.controller = controller
        self.open_sessions = Menu(
            self,
        )
        self.add_cascade(
            label="Sessions",
            menu=self.open_sessions,
            # command=self.set_session,
            # accelerator='Ctrl+O',
            # inderline=0,
            state="disabled",
        )
        self.add_separator()
        self.add_command(
            label="Set As Last",
            command=lambda: None,
            accelerator="Ctrl+L",
            underline=0,
        )
        self.add_command(
            label="Save",
            command=lambda: None,
            accelerator="Ctrl+S",
            underline=0,
        )
        self.add_command(
            label="Save as",
            command=lambda: None,
            accelerator="Shift+Ctrl+S",
            underline=0,
        )
        self.add_command(
            label="New",
            command=lambda: None,
            # accelerator='Shift+Ctrl+S',
            underline=0,
            state="disabled",
        )
        self.add_command(
            label="Delete",
            command=lambda: None,
            # accelerator='Shift+Ctrl+S',
            underline=0,
            state="disabled",
        )

    def update_sessions(self):
        if not self.controller.sdcard:
            self.entryconfig("Sessions", state="disabled")
            return
        self.entryconfig("Sessions", state="normal")
        self.open_sessions.delete(0, END)
        for s in self.controller.sdcard.sessions:
            logger.info(f"update_sessions: add {s}")
            self.open_sessions.add_command(
                label=s,
                command=lambda s=s: self.set_session(s),
            )

    def set_session(self, s):
        self.controller.set_session(s)


class ViewMenu(Menu):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.session_bar_var = BooleanVar(value=False)
        self.phrase_bar_var = BooleanVar(value=True)
        self.status_bar_var = BooleanVar(value=True)

        self.add_checkbutton(
            label="Session Bar",
            command=self.toggle_session_bar,
            variable=self.session_bar_var,
            # accelerator='Ctrl+L',
            # underline=0,
        )
        self.add_checkbutton(
            label="Phrase Bar",
            command=self.toggle_phrase_bar,
            variable=self.phrase_bar_var,
            # accelerator='Ctrl+L',
            # underline=0,
        )
        self.add_checkbutton(
            label="Status Bar",
            command=self.toggle_status_bar,
            variable=self.status_bar_var,
            # accelerator='Ctrl+L',
            # underline=0,
        )

    def toggle_session_bar(self):
        logger.info(f"Show Session Bar")
        self.controller.show_object("session_bar", self.session_bar_var.get())

    def toggle_phrase_bar(self):
        logger.info(f"Show Phrase Bar")
        self.controller.show_object("phrase_bar", self.phrase_bar_var.get())

    def toggle_status_bar(self):
        logger.info(f"Show Status Bar")
        self.controller.show_object("status_bar", self.status_bar_var.get())
