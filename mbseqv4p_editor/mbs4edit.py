#!/usr/bin/env python3

import logging
import os
from tkinter import *
from tkinter.ttk import *

from ttkthemes import ThemedTk

from .controller import Controller
from .helpers import *
from .model.pattern import MAX_NUM_BANKS
from .view_tk.main_app import MainApplication
from .view_tk.menus import SDCardMenu, SessionMenu, ViewMenu

logger = logging.getLogger(f"{__name__:{LOGW_NAME}}")


class TkinterController(Controller):
    def __init__(self, path):
        super().__init__(path)
        self.last_track_editor = "tracks_editor"

    def show_status(self):
        """Update status and phrase bar information. (Tkinter)"""
        left = ""
        midleft = ""
        midright = ""
        right = ""
        if not self.sdcard:
            self.main_app.status_bar.update("No SDCard open.", "", "", "")
            return
        m = self.sdcard.modified_symbol()
        left = f"{self.sdcard.path} {m}"
        if self.session:
            m2 = self.session.modified_symbol()
            midleft = f"{self.session.name}{m2}"
        if self.track:
            midright = f"{self.track.layer_config_repr()}"
            # midright = f'{track_str:30}'
            if self.track.event_mode != "Drum":
                midright += f": {self.track.cat} {self.track.label}"
        npn = self.phrase[self.group]
        if self.pattern:
            m3 = self.pattern.modified_symbol()
        else:
            m3 = "-"
        right = f"{npn}{m3}"
        self.main_app.status_bar.update(left, midleft, midright, right)

    def show_object(self, obj, show=True):
        attr = getattr(self.main_app, obj)
        if show:
            attr.grid()
        else:
            attr.grid_remove()

    def open_sdcard(self, path):
        super().open_sdcard(path)
        # pbe = self.main_app.pattern_banks_editor
        self.main_app.track_editor.set_sdcard(self.sdcard)
        self.main_app.session_bar.set_sdcard(self.sdcard)

    def save_session_as(self, path=None):
        pass

    def set_session(self, name=None):
        super().set_session(name)
        self.main_app.session_bar.select(self.session.name)
        self.update_pattern_bank_editors(force=True)
        self.main_app.song_editor.update_from_session()
        self.main_app.mixer_map_editor.set_mixer_map_bank(self.session.mixer_map_bank)

    def update_pattern_bank_editors(self, force=False):
        pbe = self.main_app.pattern_banks_editor
        for nb in range(MAX_NUM_BANKS):
            pbe.update_from_bank(nb, force)
            pbe.tv[nb].see(self.phrase[nb])

    def set_pattern_selection(self, selection=None):
        """set new selection or if None given
        just refresh view of existing one
        """
        super().set_pattern_selection(selection)
        logger.debug("set_pattern_selection Tkinter")
        if not self.session:
            return
        pbe = self.main_app.pattern_banks_editor
        for nbank in range(MAX_NUM_BANKS - 1, -1, -1):
            for npn in self.pattern_selection:
                nb, np = npn2idx(npn)
                if nb == nbank:
                    first = self.session.get_pattern(npn)
                    pbe.pattern_editor[nb].set_pattern(npn, first)
                    first_track = self.session.get_track(npn, 0)
                    self.track = first_track
                    self.main_app.step_editor.set_track(first_track)
                    self.main_app.track_editor.set_track(first_track)
                    break
        self.main_app.phrase_bar.set_from_phrase()
        self.show_status()

    def set_phrase(self, npn):
        super().set_phrase(npn)
        self.main_app.phrase_bar.set_from_phrase()
        self.main_app.tracks_editor.set_from_phrase()
        self.show_status()

    def set_track(self, nt=0):
        super().set_track(nt)
        self.main_app.step_editor.set_track(self.track)
        self.main_app.tracks_editor.set_track(nt)
        self.main_app.phrase_bar.set_track_button_state(nt // 4, nt % 4)
        self.show_status()

    def paste_pattern(self, arg=None):
        super().paste_pattern(arg)
        # logger.debug('paste_pattern Tkinter')
        self.update_pattern_bank_editors()
        self.show_status()

    def clear_pattern(self):
        super().clear_pattern()
        # logger.debug('reset_pattern Tkinter')
        self.update_pattern_bank_editors()
        self.show_status()

    def save_pattern_banks(self, arg=None):
        super().save_pattern_banks()
        # logger.debug('save_pattern_banks Tkinter')
        self.update_pattern_bank_editors(force=True)
        self.show_status()

    def paste_track(self, arg=None):
        super().paste_track(arg=arg)
        self.main_app.tracks_editor.set_from_phrase()
        self.update_pattern_bank_editors()
        # self.main_app.tracks_editor.set
        self.show_status()

    def show_editor(self, name):
        if name == "track":
            name = self.last_track_editor

        ne = self.main_app.tabs.get(name, 0)
        logger.info(f"show_editor {name} {ne}")
        self.main_app.nb.select(ne)

    def select_mixer_map(self, nmap):
        nmap = int(nmap) - 1
        logger.info(f"select_mixer_map {nmap}")
        if nmap < 0:
            return
        mme = self.main_app.mixer_map_editor
        mme.collapse_all()
        item = f"mmap{nmap:02}"
        mme.tv.item(item, open=True)
        mme.tv.focus(item)
        mme.tv.selection_set(item)
        mme.tv.see(item)
        self.show_editor("mixer_map_editor")


# def configure_styles():
#    '''Configure ttk Styles.
#    '''
#
#    s = Style()


def run():

    homedir = os.path.normpath(os.getcwd())
    ctrl = TkinterController(homedir)
    root = ThemedTk(theme="plastik")

    root.resizable(True, True)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    ctrl.root = root

    #  Menus
    menubar = Menu(root)
    sdcard_menu = SDCardMenu(menubar, ctrl)
    session_menu = SessionMenu(menubar, ctrl)
    view_menu = ViewMenu(menubar, ctrl)

    root.configure(menu=menubar)
    menubar.add_cascade(label="SD Card", menu=sdcard_menu)
    menubar.add_cascade(label="Session", menu=session_menu)
    menubar.add_cascade(label="View", menu=view_menu)

    app = MainApplication(root, ctrl)
    app.grid()
    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)

    # hide session bar by default
    ctrl.main_app = app
    ctrl.show_object("session_bar", False)

    # TODO load last sdcard from .last_sdcard file
    # ctrl.open_sdcard(homedir)
    ctrl.do("show_editor", "tracks_editor")

    # run(root)
    #  self.root.minsize(1000,1200)
    root.title("MIDIbox SEQ V4+ Editor")
    root.deiconify()
    root.update()
    # print(self.root.winfo_width(), self.root.winfo_height())
    root.mainloop()


if __name__ == "__main__":

    run()
