import logging
import os
from collections import OrderedDict
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import *

from .mixer_map_tv import MMapTreeview
from .pattern import PatternBanksEditor
# from view_tk.song import SongsBankEditor
# from view_tk.mixer_map import MMapsBankEditor
from .phrase_bar import PhraseBar
from .session import SessionBar
from .song_tv import SongBankTreeview
from .step_edit import TVStepEditor
from .track_config import TrackEditor
from .tracks import TracksView

from ..helpers import *

logger = logging.getLogger(f"{__name__:{LOGW_NAME}}")


class ConfigEditor(LabelFrame):
    def __init__(self, parent):
        self.name = "Config Editor"
        LabelFrame.__init__(self, parent, text=self.name)
        self.content = Text(self, wrap="word")
        scrollbar = Scrollbar(self.content)

        self.content.pack(expand="yes", fill="both")
        scrollbar.pack(side="right", fill="y")

        self.content.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.content.yview)

    def update(self, seq_config):
        self.content.delete(1.0, END)
        self.content.insert(1.0, seq_config)


class ConfigEntryEditor(LabelFrame):
    def __init__(self, parent):
        self.name = "Config Editor"
        LabelFrame.__init__(self, parent, text=self.name)
        # self.pack(fill=BOTH, expand=TRUE)
        self.canvas = Canvas(self, borderwidth=0, background="#ff0000")
        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.hsb = Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.configure(xscrollcommand=self.hsb.set)
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.create_content_frame()
        self.svars = []

    def create_content_frame(self):
        self.content = Frame(self.canvas)
        self.content.pack(fill=BOTH, expand=TRUE)
        self.content.bind("<Configure>", self.on_configure)
        self.canvas.create_window(
            (4, 4), anchor="nw", window=self.content, tags="self.content"
        )

    def on_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update(self, seq_config):

        if self.content:
            self.content.destroy()
            self.svars = []
            self.create_content_frame()

        for r in range(len(seq_config)):
            print(seq_config[r])
            self.svars.append([])
            for d in range(len(seq_config[r])):
                if d == 0:
                    data = Label(self.content, text=seq_config[r][d])
                else:
                    svar = StringVar()
                    self.svars[r].append(svar)
                    svar.set(seq_config[r][d])
                    data = Entry(self.content, width=4, textvariable=svar)
                data.grid(row=r, column=d)


class StatusBar(Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=2)
        pad_frm = Frame(
            self,
            borderwidth=1,
            relief="sunken",
        )
        self.left = StringVar()
        self.midleft = StringVar()
        self.midright = StringVar()
        self.right = StringVar()

        lbl_l = Label(pad_frm, textvariable=self.left)
        lbl_ml = Label(pad_frm, textvariable=self.midleft)
        lbl_mr = Label(pad_frm, textvariable=self.midright)
        lbl_r = Label(pad_frm, textvariable=self.right)
        sep_l = Separator(pad_frm, orient=VERTICAL)
        sep_m = Separator(pad_frm, orient=VERTICAL)
        sep_r = Separator(pad_frm, orient=VERTICAL)

        pad_frm.pack(fill=X, expand=TRUE)
        lbl_l.pack(side=LEFT, fill=X, expand=TRUE, anchor=W)
        sep_l.pack(side=LEFT, fill=Y, expand=TRUE)
        lbl_ml.pack(side=LEFT, fill=X, expand=TRUE, anchor=W)
        sep_m.pack(side=LEFT, fill=Y, expand=TRUE)
        lbl_r.pack(side=RIGHT, fill=X, expand=TRUE, anchor=W)
        sep_r.pack(side=RIGHT, fill=Y, expand=TRUE)
        lbl_mr.pack(side=RIGHT, fill=X, expand=TRUE, anchor=W)

    def update(self, l, ml, mr, r):
        self.left.set(l)
        self.midleft.set(ml)
        self.midright.set(mr)
        self.right.set(r)


class SDCardSelector(LabelFrame):
    def __init__(self, parent, controller):
        LabelFrame.__init__(self, parent, text="SD Card", padding=5)
        self.controller = controller

        # state
        self.sdcard_var = StringVar()

        # widgets
        f = Frame(self)
        f.pack(anchor=W, fill=X, expand=TRUE)

        sdc_entry = Entry(f, textvariable=self.sdcard_var)
        sdc_entry.pack(side=LEFT, fill=X, expand=TRUE)

        buttons = [
            ("Open", self.open_sdcard),
            ("Save As", self.save_sdcard),
            ("Edit Global Config", self.edit_config),
            ("Edit Presets", self.edit_config),
        ]

        for name, cmd in buttons:
            btn = Button(f, text=name, command=cmd)
            btn.pack(side=LEFT)

        self.session_bar = SessionSelector(self, controller)
        self.session_bar.pack(side=BOTTOM, fill=X)


class MainApplication(Frame):
    def __init__(self, root, controller):
        super().__init__(root)
        self.controller = controller

        # self.sdcard_bar = SDCardSelector(root, controller)
        # self.sdcard_bar.pack(fill=X)

        self.session_bar = SessionBar(self, controller)
        self.phrase_bar = PhraseBar(self, controller)
        self.status_bar = StatusBar(self)

        self.nb = nb = Notebook(self)

        self.step_editor = TVStepEditor(nb, controller)
        self.tracks_editor = TracksView(nb, controller)
        self.track_editor = TrackEditor(nb, controller)
        self.pattern_banks_editor = PatternBanksEditor(nb, controller)
        self.song_editor = SongBankTreeview(nb, controller)
        self.mixer_map_editor = MMapTreeview(nb, controller)

        nb.enable_traversal()
        nb.add(
            self.pattern_banks_editor,
            text="Pattern Banks",
            underline=0,
        )
        nb.add(
            self.tracks_editor,
            text="Tracks",
            underline=0,
        )
        nb.add(
            self.step_editor,
            text="Step View",
            underline=0,
        )
        nb.add(
            self.track_editor.config_editors,
            text="Track Configuration",
            underline=0,
        )
        nb.add(
            self.track_editor.fx_editors,
            text="FX Configuration",
            underline=1,
        )
        nb.add(
            self.song_editor,
            text="Songs",
            underline=1,
        )
        nb.add(
            self.mixer_map_editor,
            text="Mixer Maps",
            underline=0,
        )
        nb.add(Frame(nb), text="Session Config", state="disabled")
        nb.add(Frame(nb), text="Global Config", state="disabled")
        nb.add(Frame(nb), text="Bookmarks", state="disabled")
        nb.add(Frame(nb), text="Grooves", state="disabled")

        nb.bind("<<NotebookTabChanged>>", self.tab_update)

        self.tabs = {
            "pattern_banks_editor": 0,
            "tracks_editor": 1,
            "step_editor": 2,
            "track_config_editor": 3,
            "track_fx_editor": 4,
            "song_editor": 5,
            "mixer_map_editor": 6,
        }
        self.tabs_inv = {}
        for k, v in self.tabs.items():
            self.tabs_inv[v] = k

        # main layout
        for tab in nb.tabs():
            nb.tab(tab, padding=4, sticky=NSEW)

        self.nb.columnconfigure(0, weight=1)
        self.nb.rowconfigure(0, weight=1)

        self.session_bar.grid(row=0, sticky=EW)
        self.nb.grid(row=1, sticky=EW)
        self.phrase_bar.grid(row=2, sticky=EW)
        self.status_bar.grid(row=3, sticky=EW)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

    def edit_config(self):
        self.controller.do("edit_config", "global")

    def show_editor(self, event):
        print(event)

    def tab_update(self, event):
        index = event.widget.index("current")
        logger.debug(f"switch to tab {index}")
        if self.controller.session:
            session = self.controller.session
            if session.has_modifications():
                self.controller.do("update_pattern_bank_editors")
        name = self.tabs_inv[index]
        if name in [
            "tracks_editor",
            "step_editor",
            "track_config_editor",
            "track_fx_editor",
        ]:
            self.controller.last_track_editor = name
