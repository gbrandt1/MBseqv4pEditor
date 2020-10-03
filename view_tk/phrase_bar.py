import logging
from tkinter import *
from tkinter.ttk import *

from helpers import *

logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


class PhraseBar(LabelFrame):

    def __init__(self, parent, controller):
        super().__init__(
            parent,
            text='Phrase',
            # padding=2,
        )
        self.controller = controller
        self.group_var = []
        self.track_var = []
        self.phrase_var = []
        self.grp_btn = []
        self.trk_btn = []
        self.multiple = False

        self.grp_selected = [False]*4
        self.trk_selected = [False]*16

        for g in range(4):
            self.group_var.append(StringVar(value=f'Group {g+1}'))
            grp_frm = Frame(
                self,
            )
            grp_frm.pack(side=LEFT, fill=X, expand=TRUE)
            self.grp_btn.append(
                Button(
                    grp_frm,
                    textvariable=self.group_var[g],
                    command=lambda g=g: self.on_click_group(g),
                )
            )
            self.grp_btn[g].pack(fill=X, expand=TRUE)
            for t in range(4):
                self.track_var.append(StringVar(value=f'G{g+1}T{t+1}'))
                self.phrase_var.append(StringVar())
                self.trk_btn.append(
                    Button(
                        grp_frm,
                        width=4,
                        textvariable=self.phrase_var[4*g+t],
                        command=lambda g=g, t=t: self.on_click_track(g, t),
                    )
                )
                self.trk_btn[4*g+t].pack(side=LEFT, fill=X, expand=TRUE)
            # if g < 3:
            #    Separator(self, orient=VERTICAL).pack(
            #        side=LEFT, fill=Y, expand=TRUE)

    def set_from_phrase(self):
        if not self.controller.session:
            return
        for g, npn in enumerate(self.controller.phrase):
            pattern = self.controller.session.get_pattern(npn)
            if not pattern:
                continue
            self.group_var[g].set(f'"{npn:4} {pattern.cat}-{pattern.label}"')
            for t in range(4):
                track = self.controller.tracks[4*g+t]
                if track:
                    m = track.modified_symbol()
                else:
                    m = ' '
                self.phrase_var[4*g+t].set(f'G{g+1}T{t+1}{m}')
        pattern = self.controller.pattern

    def on_click_group(self, g):
        if not self.controller.phrase:
            return
        npn = self.controller.phrase[g]
        sel = [npn]
        self.controller.do('set_pattern_selection', sel)
        self.controller.set_pattern(npn)
        self.controller.set_track(4*g)
        logger.info(f'on_click_group {npn} {g}')
        self.controller.do('show_editor', 'pattern_banks_editor')
        self.set_group_button_state(g)
        self.controller.show_status()

    def set_group_button_state(self, g):
        if not self.multiple:
            [b.state(['!pressed']) for b in self.grp_btn]
            [b.state(['!pressed']) for b in self.trk_btn]
            self.grp_btn[g].state(['pressed'])

    def on_click_track(self, g, t):
        if not self.controller.phrase:
            return
        npn = self.controller.phrase[g]
        sel = [npn]
        nt = 4*g+t
        logger.info(f'\non_click_track {npn} {g} {t} {nt}')
        self.controller.do('set_pattern_selection', sel)
        #self.controller.set_pattern(npn)
        self.controller.set_track(nt)
        self.controller.do('show_editor', 'track')
        self.set_track_button_state(g, t)
        #self.controller.show_status()
        #dump(self.controller)

    def set_track_button_state(self, g, t):
        if not self.multiple:
            [b.state(['!pressed']) for b in self.grp_btn]
            [b.state(['!pressed']) for b in self.trk_btn]
            self.trk_btn[4*g+t].state(['pressed'])

    #def __repr__(self):
    #    buf = ''
    #    for g in controller.group
     #   return (
     #       f''
     #   )