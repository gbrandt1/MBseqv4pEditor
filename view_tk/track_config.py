#!/usr/bin/env python3

import logging
import os
from collections import defaultdict
from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import askokcancel
from tkinter.ttk import *

#from view_tk.catname import CatNameEditor
from helpers import *
from track_cc import *
from track_gui import *

logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


class TrackPresetSelector():
    def __init__(self, parent, controller):  # , track):
        self.parent = parent
        self.controller = controller


class TrackEditor():
    def __init__(self, parent, controller):  # , track):
        self.parent = parent
        self.controller = controller
        #self.track = track
        self.name = 'Track Editor'
        self.svar = defaultdict(StringVar)
        # self.svar['event_mode']=StringVar()

        self.const_label_var = {
            'a': StringVar(value=''),
            'b': StringVar(value=''),
            'c': StringVar(value=''),
        }
        # self.set_track()
        self.config_editors = self.init_config_editors(self.parent)
        self.fx_editors = self.init_fx_editors(self.parent)

        disable_children(self.config_editors)
        disable_children(self.fx_editors)

    def set_sdcard(self, sdcard=None):
        """ Set preset names from sdcard """
        # self.cbx_trkcat.configure(values=sdcard.trkcat)
        # self.cbx_trklabel.configure(values=sdcard.trklabel)
        # self.cbx_trkdrum.configure(values=sdcard.trkdrum)
        self.cbx_track_preset.configure(
            values=list(sdcard.track_presets.keys()))

    def set_track(self, track):
        """ Copy Track to var skipping cc, par, trg arrays """
        if not track:
            return
        self.track = track
        tv = vars(self.track)
        for k, v in tv.items():
            if k in ['cc', 'par', 'trg']:
                continue
            # if k in self.svar:
            self.svar[k].set(v)
            # else:
            #    self.svar[k] = StringVar(value=v)
            #logging.info(f'set_track: {k} = {v}')

        self.svar['layer_config'] = StringVar(
            value=list(TRACK_LAYER_CONFIG.keys())[0])

        # show drum or note specific GUI elements
        for abc in ['a', 'b', 'c']:
            lv = self.const_label_var[abc]
            lv.set(TRACK_CONST_LABELS[self.track.event_mode][abc])

        enable_children(self.config_editors)
        enable_children(self.fx_editors)
        self.set_name_editor_state()
        self.cbx_mode.configure(state='readonly')
        self.cbx_trkcfg.configure(state='readonly')
        disable_children(self.frm_trkcfg)

    def update_track_attr(self, key):
        """ Copy tkinter variable back to Track
            (in MVC this would be observer callback)
        """
        if key:
            value = self.svar[key].get()
            setattr(self.track, key, value)
            # self.track.notify()
            logging.info(f'update_track_attr: {key} = {value}')
        # else:
        #    for k, v in self.svar.items():
        #        value = v.get()
        #        setattr(self.track, k, value)
        #        #logging.info(f'update_track: {k} = {value} ({v})')

    def init_toolbar(self, parent):
        bf = Frame(parent)
        buttons = [
            ('Copy', self.copy_track),
            ('Paste', self.paste_track),
            ('Reset', self.reset_track),
            ('Dump', self.dump_track),
        ]
        for name, cmd in buttons:
            btn = Button(bf, text=name, command=cmd)
            btn.pack(side=LEFT)
        return bf

    def init_config_editors(self, parent):
        frm_tab = Frame(parent)

        tb = self.init_toolbar(frm_tab)
        tb.pack(fill=X, expand=TRUE, anchor=W)

        frm_cfg = Frame(frm_tab, padding=PAD_FRM)
        tce = self.init_track_config_editor(frm_cfg)
        tpe = self.init_track_preset_editor(frm_cfg)

        frm_ne = Frame(frm_tab)  # , padding=PAD_FRM)
        dne = self.drum_name_editor = self.init_drum_name_editor(frm_ne)

        row0 = self.init_row(frm_tab, ('MIDI',))
        row1 = self.init_row(frm_tab, ('Length', 'Direction',))
        row2 = self.init_row(
            frm_tab, (
                'Clock Divider', 'Transpose', 'Groove', 'Morphing',
            )
        )
        row3 = self.init_row(
            frm_tab, (
                'Trigger Layers', 'Drum Parameters',
            )
        )
        lce = self.init_lay_const_abc_editor(frm_tab)

        frm_cfg.pack(fill=BOTH, expand=TRUE)
        tce.pack(fill=BOTH, expand=TRUE, side=LEFT, padx=PAD_LF)
        tpe.pack(fill=BOTH, expand=TRUE, side=RIGHT, padx=PAD_LF)
        frm_ne.pack(fill=X, expand=TRUE, anchor=W)
        dne.pack(side=LEFT, fill=BOTH, expand=TRUE, padx=PAD_LF)
        row0.pack(fill=BOTH, expand=TRUE)
        row1.pack(fill=BOTH, expand=TRUE)
        row2.pack(fill=BOTH, expand=TRUE)
        row3.pack(fill=BOTH, expand=TRUE)
        lce.pack(fill=BOTH, expand=TRUE, padx=PAD_LF)

        return frm_tab

    def init_fx_editors(self, parent):
        frm_tab = Frame(parent)
        row1 = self.init_row(
            frm_tab, ('FX: Echo', 'FX: Humanize', 'FX: Limit',)
        )
        row2 = self.init_row(
            frm_tab, ('FX: LFO', 'FX: LFO Flags',)
        )
        row3 = self.init_row(
            frm_tab, ('FX: Duplicate',)
        )

        frm_tab.pack()  # , expand=TRUE)
        row1.pack(fill=X)  # , expand=TRUE, anchor=N)
        row2.pack(fill=X)  # , expand=TRUE, anchor=N)
        row3.pack(fill=X)  # , expand=TRUE, anchor=N)
        return frm_tab

    def init_row(self, parent, sections):
        frm = Frame(parent)
        for s in sections:
            self.init_page(frm, s).pack(
                side=LEFT,
                #fill=X, expand=TRUE, anchor=N,
                padx=PAD_LF)
        return frm

    def init_page(self, parent, page):
        lf = LabelFrame(parent, text=page, padding=PAD_LF)
        c = 2
        r = 0
        for txt, var in TRACK_GUI_PAGES[page]:
            lbl = Label(lf, text=txt, justify=LEFT)
            lbl.grid(row=r, column=c, sticky=W)
            ent = Entry(lf, width=6, textvariable=self.svar[var])
            ent.grid(row=r+1, column=c, sticky=W)
            ent.bind(
                '<FocusOut>',
                lambda e, var=var: self.update_track_attr(var)
            )
            logging.debug(f'bound {var} ({txt})')
            c += 1
        return lf

    def init_lay_const_abc_editor(self, parent):
        lf = LabelFrame(parent, text='Constants', padding=PAD_LF)
        r = 0
        for c in range(16):
            lbl = Label(lf, text=f'{c+1}', justify=LEFT)
            lbl.grid(row=r, column=c+1, sticky=W)
        for abc in ['a', 'b', 'c']:
            lbl = Label(
                lf,
                textvariable=self.const_label_var[abc],
                justify=LEFT,
            )
            lbl.grid(row=r+1, column=0, sticky=W)
            for c in range(1, 17):
                ent = Entry(
                    lf,
                    width=4,
                    textvariable=self.svar[f'lay_const_{abc}{c}'],
                )
                ent.grid(row=r+1, column=c, sticky=W)
            r += 1
        return lf

    def init_pattern_info(self, parent):
        frm_pattern = Frame(parent)
        frm_pattern.pack(fill=X, anchor=W)  # , padx=8, pady=8)
        Label(frm_pattern, text='Pattern Name: ').pack(side=LEFT)
        Label(frm_pattern, textvariable=self.svar['pattern_name']).pack(
            side=LEFT)
        return frm_pattern

    def init_track_config_editor(self, parent):
        frm_tab = LabelFrame(
            parent, text='Track Configuration', padding=PAD_LF
        )
        self.frm_trkcfg = frm_tab
        # frm_tab.pack()  # fill=X) #, expand=TRUE)
        frm_cfg = Frame(frm_tab)
        frm_cfg.pack(fill=X, anchor=W)
        Label(frm_cfg, text='Event Mode').pack(side=LEFT)
        self.cbx_mode = Combobox(
            frm_cfg,
            width=8,
            textvariable=self.svar['event_mode'],
            values=EVENT_MODES,
            state='readonly',
            # self.svar['event_mode'].get(),
            # *EVENT_MODES,
        )
        # print(*EVENT_MODES)
        self.cbx_mode.pack(side=LEFT)
        self.cbx_mode.bind(
            '<FocusOut>',
            lambda e: self.do_configure_track('event_mode')
        )

        def ent_cfg(parent, text, var, row, col):
            lbl = Label(parent, text=text, justify=RIGHT)
            lbl.grid(row=row, column=col)
            ent = Entry(parent, width=3, textvariable=self.svar[var])
            ent.grid(row=row, column=col+1)
            ent.bind(
                '<FocusOut>',
                lambda e, var=var: self.do_configure_track(var)
            )
        frm_par = Frame(frm_tab)
        frm_par.pack(fill=X, anchor=W)
        ent_cfg(frm_par, 'Parameter: Instruments', 'num_p_instruments', 0, 0)
        ent_cfg(frm_par, 'Layers', 'num_p_layers', 0, 2)
        ent_cfg(frm_par, 'Steps', 'p_layer_steps', 0, 4)

        frm_trg = frm_par  # Frame(frm_tab)
        frm_trg.pack(fill=X, anchor=W)
        ent_cfg(frm_trg, 'Trigger: Instruments', 'num_t_instruments', 1, 0)
        ent_cfg(frm_trg, 'Layers', 'num_t_layers', 1, 2)
        ent_cfg(frm_trg, 'Steps', 't_layer_steps', 1, 4)

        frm_cfg2 = Frame(frm_tab)
        frm_cfg2.pack(fill=X, anchor=W)
        Label(frm_cfg2, text='Configuration Defaults').pack(side=LEFT)
        self.cbx_trkcfg = Combobox(
            frm_cfg2,
            textvariable=self.svar['layer_config'],
            values=TRACK_LAYER_CONFIG.keys(),
            state='readonly',
        )
        self.cbx_trkcfg.pack(side=LEFT)
        btn_trkcfg = Button(
            frm_cfg,
            text='Configure',
            command=self.do_configure_track
        )
        btn_trkcfg.pack()
        return frm_tab

    def init_track_preset_editor(self, parent):
        frm_pre = LabelFrame(parent, text='Presets', padding=3)
        self.cbx_track_preset = Combobox(
            frm_pre,
            width=8,
        )
        btn_new = Button(frm_pre, text='Add', command=self.do_add_preset)
        self.cbx_track_preset.pack(side=LEFT)
        btn_new.pack(side=LEFT)
        return frm_pre

    def init_drum_name_editor(self, parent):
        frm_name = LabelFrame(parent, text='Drum Names', padding=PAD_LF)
        # frm_name.pack(fill=X, anchor=W)  # , padx=8, pady=8)
        #Label(frm_name, text='Name').pack(side=LEFT)
        for d in range(16):
            ent_name = Entry(frm_name,
                             width=5,
                             textvariable=self.svar['name'],
                             # font='TkFixedFont',
                             )
            ent_name.pack(side=LEFT)
            ent_name.bind(
                '<FocusOut>', lambda e: self.update_track_attr('name'))
        Button(frm_name, text='Save As Preset').pack(side=RIGHT)
        Button(frm_name, text='Load Preset').pack(side=RIGHT)
        return frm_name


    def set_name_editor_state(self):
        # if hasattr(self, 'frm_name_editor') and hasattr(self, 'track'):
        if hasattr(self, 'track'):
            if self.track.event_mode == 'Drum':
                enable_children(self.drum_name_editor)
            else:
                disable_children(self.drum_name_editor)

    # Commands

    def copy_track(self):
        logger.info('copy_track')

    def paste_track(self):
        logger.info('paste_track')

    def reset_track(self):
        logger.info('reset_track')
        yes = askokcancel(
            'Reset Track',
            f'Reset everything in track to defaults?'
        )
        if yes:
            self.track.reset()
            self.track.modified()
            self.set_track(self.track)

    def dump_track(self):
        logger.info('dump_track')
        d = self.track.dump()
        print(d)

    def do_load_preset(self):
        preset = self.cbx_track_preset.get()
        if not preset:
            return
        askokcancel('Load Preset', f'Really load preset {preset}?')
        logging.info('load_preset')
        self.do_cmd('load_preset', preset)

    def do_add_preset(self):
        preset = self.cbx_track_preset.get()
        if not preset:
            return
        fn = asksaveasfilename(
            title=f'Save Track as Track Preset {preset}?',
            defaultextension='.v4t', initialfile=preset, initialdir=os.getcwd())
        # if os.path.exists(fn):
        #   askokcancel('Preset Exists',f'Really overwrite preset {preset}?')
        logging.info('save_preset')
        self.do_cmd('save_preset', preset)

    def do_configure_track(self, var=None):
        if isinstance(var, str):
            self.update_track_attr(var)
        # elif isinstance( var, tuple):
        if not var:
            var = self.svar['layer_config'].get()
            print(var)
        #askokcancel('Configure Track',f'Really configure track? {var}')
        logging.info(f'configure_track {var}')
        #self.do_cmd('configure_track', var)

    def do_cmd(self, cmd, *args):
        self.controller.do(cmd, args)
