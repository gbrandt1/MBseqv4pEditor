
import logging
from collections import OrderedDict
from tkinter import *
from tkinter.ttk import *

from helpers import *
from view_tk.editabletreeview import EditableTreeview

logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


class PatternEditor(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        #   State
        self.npn_var = StringVar()
        self.mixer_map_var = StringVar()
        self.sysex_setup_var = StringVar()
        self.track_var = [StringVar() for i in range(4)]
        self.pattern = None

        #   Widgets
        # self.cne = CatNameEditor(self, self.controller)
        trl = self.init_track_links()
        msl = self.init_m_s_links()

        # self.cne.pack(fill=X, expand=TRUE)
        trl.pack(fill=X, expand=TRUE)
        msl.pack(fill=X, expand=TRUE)

    def init_track_links(self):
        frm_tracks = Frame(self, padding=3)
        for i in range(4):
            btn_trk = Button(
                frm_tracks,
                style='fixed.TButton',
                textvariable=self.track_var[i],
                command=lambda i=i: self.edit_track(i),
            )
            btn_trk.pack(fill=X, expand=TRUE, anchor=W)
        return frm_tracks

    def init_m_s_links(self):
        frm_links = Frame(self, padding=3)
        spx_mmp = Spinbox(
            frm_links,
            width=3,
            textvariable=self.mixer_map_var,
            from_=0, to=MAX_NUM_MAPS,
        )
        btn_mmp = Button(
            frm_links,
            text='Mixer Map',
            command=self.select_mixer_map,
        )
        spx_syx = Spinbox(
            frm_links,
            width=3,
            textvariable=self.sysex_setup_var,
            from_=0, to=63,
        )
        btn_syx = Button(
            frm_links,
            text='SysEx Setup',
            command=self.select_sysex_setup,
        )

        spx_mmp.bind('<FocusOut>', lambda e: self.update_pattern())
        spx_syx.bind('<FocusOut>', lambda e: self.update_pattern())

        btn_mmp.grid(row=0, column=1)
        spx_mmp.grid(row=0, column=0)
        btn_syx.grid(row=1, column=1)
        spx_syx.grid(row=1, column=0)

        return frm_links

    #   npn, cat, name, tracks, mmap, sysex):
    def set_pattern(self, npn, pattern):
        logger.debug('set_pattern {npn} {pattern}')
        if not pattern:
            return
        self.pattern = pattern
        self.npn_var.set(value=npn)
      # self.cne.set_pattern(pattern)
        for i in range(4):
            self.track_var[i].set(value=f'T{i+1} {pattern.tracks[i]}')
        self.mixer_map_var.set(value=f'{pattern.mixer_map}')
        self.sysex_setup_var.set(value=f'{pattern.sysex_setup}')

    def update_pattern(self):
        #   self.pattern.cat = self.cne.cat_var.get()
        #   self.pattern.name = self.cne.name_var.get()
        self.pattern.mixer_map = self.mixer_map_var.get()
        self.pattern.sysex_setup = self.sysex_setup_var.get()
        #  npn = self.npn_var.get()
        self.pattern.modified()
        #   self.controller.do('update_pattern',npn=npn)
        logger.info(f'update_pattern {vars(self.pattern)}')

    def select_mixer_map(self):
        self.controller.do('select_mixer_map', self.mixer_map_var.get())

    def select_sysex_setup(self):
        self.controller.do('select_sysex_setup', self.sysex_setup_var.get())

    def edit_track(self, idx):
        npn = self.npn_var.get()
        sel = [npn]
        self.controller.do('set_pattern_selection', sel)
        self.controller.do('show_editor', 'step_editor')

    # def set_cat_name(self):
    #    self.controller.do(
    #        'set_cat_name_pattern',
    #        self.npn_var.get(), self.cat_var.get(), self.name_var.get()
    #    )


class PatternBanksEditor(Frame):

    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent)
        self.pack(fill=BOTH, expand=1)

        #   State
        self.tvidx = 0

        #   Widgets
        ftb = self.init_toolbar()
        ftv = self.init_treeviews()

        ftb.pack(fill=X)
        ftv.pack(fill=BOTH, expand=TRUE)

    def init_treeviews(self):
        lb_frame = Frame(self)

        vsb = Scrollbar(lb_frame, orient=VERTICAL)
        vsb.config(command=self.yview)
        vsb.pack(side=RIGHT, fill=Y)

        self.tv = tv = []
        pe = []
        self.head_var = []
        for i in range(MAX_NUM_BANKS):
            frm_tv = Frame(lb_frame)
            frm_tv.pack(side=LEFT, fill=BOTH, expand=TRUE)

            self.head_var.append(StringVar())
            header = Label(frm_tv, textvariable=self.head_var[i])

            tv.append(
                EditableTreeview(
                    frm_tv,
                    selectmode=EXTENDED,
                    columns=('cat', 'label'),
                )
            )

            tv[i].column('#  0', width=60, stretch=1)
            tv[i].column('cat', width=60, stretch=1)
            tv[i].column('label', width=100, stretch=1)

            tv[i].heading('#  0', text=f'Bank {i+1}')
            tv[i].heading('cat', text='Category')
            tv[i].heading('label', text='Label')

            tv[i].tag_configure('empty', foreground='gray60')

            self.populate_roots(i)

            tv[i].configure(yscrollcommand=vsb.set)

            tv[i].bind("<Command-c>", self.on_copy)
            tv[i].bind("<Command-v>", self.on_paste)
            tv[i].bind("<BackSpace>", self.on_clear)
            tv[i].bind("<MouseWheel>", self.on_mouse_wheel)
            tv[i].bind('<Left>', self.on_lr_key, add=True)
            tv[i].bind('<Right>', self.on_lr_key, add=True)
            tv[i].bind(
                '<<TreeviewSelect>>',
                lambda event, i=i: self.on_select(event, i),
                add=True,
            )
            tv[i].bind(
                '<<TreeviewCellEdited>>',
                lambda event, i=i: self.on_cell_changed(event, i)
            )
            tv[i].bind(
                '<<TreeviewInplaceEdit>>',
                lambda event, i=i: self.on_row_edit(event, i)
            )

            pe.append(
                PatternEditor(frm_tv, self.controller)
            )

            header.pack(fill=X)
            tv[i].pack(fill=BOTH, expand=TRUE)
            #   pe[i].pack(fill=X)  #   , expand=TRUE)

        self.pattern_editor = self.pe = pe
        return lb_frame

    def init_toolbar(self):
        bf = Frame(self)
        buttons = [
            ('Copy', self.on_copy),
            ('Paste', self.on_paste),
            ('Clear', self.on_clear),
            ('Save', self.on_save),
            # ('Dump', self.on_dump),
        ]
        for name, cmd in buttons:
            btn = Button(bf, text=name, command=cmd)
            btn.pack(side=LEFT)
        return bf

    def populate_roots(self, nb):
        self.tv[nb].delete(*self.tv[nb].get_children())
        for np in range(MAX_NUM_PATTERN):
            npn = idx2npn(nb, np)
            #   , values=values)
            self.tv[nb].insert('', 'end', npn, text=f' {npn}', tag='empty')

    def update_from_bank(self, nb=None, force=False):
        if not nb:
            nb = self.tvidx
        if not self.controller.session:
            logger.warn('update_from_bank: No session open!')
            return
        bank = self.controller.session.banks[nb]
        if bank.has_modifications() or force:
            bankname = bank.name
            self.head_var[nb].set(f'{bankname}')
            for np in range(MAX_NUM_PATTERN):
                npn = idx2npn(nb, np)
                self.update_from_pattern(npn)

    def update_from_pattern(self, npn):
        nb, np = npn2idx(npn)
        pattern = self.controller.session.get_pattern(npn)
        if not pattern:
            return
        m = pattern.modified_symbol()
        values = (pattern.cat, pattern.label, m)
        tag = ''
        if pattern.name.isspace():
            values = ('', f'<Pattern {npn[2:]}>', '',)
            tag = 'empty'
        self.tv[nb].item(npn, text=f'{npn}{m}', values=values, tag=tag)

    def yview(self, *args):
        [self.tv[i].yview(*args) for i in range(MAX_NUM_BANKS)]

    def on_mouse_wheel(self, event):
        [self.tv[i].yview("scroll", -event.delta, "units")
         for i in range(MAX_NUM_BANKS)]
        #   this prevents default bindings from firing, which
        #   would end up scrolling the widget twice
        return "break"

    def on_lr_key(self, event):
        #   print(event)
        if event.keysym == 'Left':
            if self.tvidx > 0:
                self.tvidx -= 1
        if event.keysym == 'Right':
            if self.tvidx < 3:
                self.tvidx += 1

        npn = self.tv[self.tvidx].selection()[0]
        self.tv[self.tvidx].focus_set()
        self.tv[self.tvidx].selection_set((npn,))
        self.tv[self.tvidx].focus(npn)
        return "break"

    def on_select(self, event, i):
        self.tvidx = i

        #   build pattern selection in controller format
        #ctrlsel = OrderedDict()
        # for npn in self.tv[i].selection():
        #    ctrlsel[npn] = (0, 1, 2, 3,)
        ctrlsel = list(self.tv[i].selection())

        self.controller.do('set_pattern_selection', selection=ctrlsel)

    def on_cell_changed(self, event, i):
        self.tvidx = i
        (col, item) = self.tv[i].get_event_info()
        logger.info(f'Column {col} of item {item} was changed')

        pattern = self.controller.session.get_pattern(item)
        values = self.tv[i].item(item)['values']

        pattern.set_cat_label(values[0], values[1])
        pattern.modified()
        # self.controller.update_pattern_bank_editors()
        self.update_from_pattern(item)

    def on_row_edit(self, event, i):
        self.tvidx = i
        col, item = self.tv[i].get_event_info()
        logger.debug(f'on_row_edit {col} {item} {i}')
        if not self.controller.sdcard:
            return

        vcat = self.controller.sdcard.trkcat.data
        vlabel = self.controller.sdcard.trklabel.data

        #  self.tv[i].inplace_entry(col, item)
        if col == 'cat':
            self.tv[i].inplace_combobox(col, item, values=vcat, readonly=False)
        if col == 'label':
            self.tv[i].inplace_combobox(
                col, item, values=vlabel, readonly=False)

    def on_copy(self, event=None):
        self.controller.do('copy_pattern')

    def on_paste(self, event=None):
        #i = self.tvidx
        # self.tv[i].__clear_inplace_widgets()
        self.controller.do('paste_pattern')
        #(col, item) = self.tv[i].get_event_info()
        # self.update_from_pattern(item)
        #self.__event_info = (col, item)
        # self.event_generate('<<TreeviewCellEdited>>')
        self.update_from_bank()

    def on_clear(self, event=None):
        self.controller.do('clear_pattern')

    def on_save(self, event=None):
        self.controller.do('save_pattern_banks')

    def on_dump(self, event=None):
        self.controller.do('dump_selection')

    #   def update_pattern_bank_editors(self):
    #      for nb in range(MAX_NUM_BANKS):
    #          self.update_pattern_bank_editor(nb)

    #   def update_pattern_bank_editor(self, nb):
    #      bankname = self.session.banks[nb].name
    #      pbe = self.main_app.pattern_banks_editor
    #      ptv = pbe.tv[nb]
    #      #  ptv.heading('#  0', text=f'Bank {nb+1}: {bankname}')
    #      pbe.head_var[nb].set(
    #          #  f'Bank {nb+1}:'
    #          f' {bankname}'
    #      )
    #      sel = ptv.selection()
    #      if not sel:
    #          npn = f'{nb+1}:A1'
    #          sel = (npn,)
