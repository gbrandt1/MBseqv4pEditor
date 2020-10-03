

import logging
import os
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import *

from helpers import *

logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


class SessionBar(LabelFrame):

    def __init__(self, parent, controller):
        super().__init__(
            parent,
            text='Session',
            #borderwidth=[8,],
            #padding=8,
        )
        self.controller = controller

        #self.svar = StringVar()

        self.cb = Combobox(self,
            width=20,
            font='TkFixedFont',
            #textvariable=self.svar,
            postcommand=self.update_values,
        )
        self.cb.pack(side=LEFT)
        self.cb.bind("<<ComboboxSelected>>", self.selected)
        #self.cb.bind('<FocusOut>', self.selected)

        buttons = [
            #('Open', self.open_session),
            ('Set As Last', self.last_session),
            ('Rename', self.rename_session),
            ('Save', self.save_session),
            ('Save As', self.save_session_as),
            #('Edit Session Config', self.edit_config),
        ]

        for name, cmd in buttons:
            btn = Button(self, text=name, command=cmd)
            btn.pack(side=LEFT)

    def set_sdcard(self, sdcard):
        self.sdcard = sdcard
        self.cb['values'] = list(self.sdcard.sessions.keys())

    def select(self, s):
        self.cb.set(s)
        #self.selected()

    def selected(self, event=None):
        print(event)
        print(self.cb.current(), self.cb.get(), self.controller.session.name)
        name = self.controller.session.name
        name2 = self.cb.get()
        if name2 != name:
            result = True
            if self.controller.session.has_modifications():
                result = messagebox.askokcancel(
                    f"Session {name} modified!",
                    f"Would you like to switch to {name2}?",
                )
            if result:
                self.controller.set_session(name2)


    def update_values(self):
        print(f'update_values')
        values = list(self.cb['values'])
        v = self.cb.get()
        if not v in values:
            values.insert(0, v)
        self.cb['values']=values

    def last_session(self):
        self.controller.do('open_session')

    def open_session(self):
        name = self.cb.get()
        self.controller.do('open_session', name)

    def rename_session(self):
        self.controller.do('rename_session')

    def save_session(self):
        self.controller.do('save_session')

    def save_session_as(self):
        self.controller.do('save_session_as')

    def edit_config(self):
        self.controller.do('edit_config', 'session')

