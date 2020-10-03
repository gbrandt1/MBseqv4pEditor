
from tkinter import *
from tkinter.ttk import *

from helpers import *
from .scrolledtreeview import ScrolledTreeview
from model.song import SONG_ACTIONS

logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


class SongBankTreeview(Frame):
    '''Song Bank Editor and Song Editor Container'''

    def __init__(self, parent, controller):
        super().__init__(parent)  # , controller, 16)
        self.pack(fill=BOTH, expand=TRUE)
        self.controller = controller

        self.sbe = SongBankEditor(self, controller)
        self.phr = SongEditor(self, controller)

        btn = Button(self.phr.tb, text='Save', command=self.on_save)
        btn.pack(side=RIGHT)

        # LAYOUT
        self.sbe.tb.grid(column=0, row=0, sticky=EW)
        self.phr.tb.grid(column=1, row=0, sticky=EW)
        self.sbe.grid(column=0, row=1, sticky='nswe')
        self.phr.grid(column=1, row=1, sticky='nswe')
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def update_from_session(self):
        self.sbe.update_from_session()

    def update_from_song(self):
        self.phr.song = self.sbe.song
        self.phr.update_from_song()
        self.phr.open_all()

    def on_save(self):
        logger.info('Save Song Bank')
        self.sbe.song_bank.write()


class SongEditor(ScrolledTreeview):
    '''Song Editor'''

    def __init__(self, parent, controller):
        super().__init__(parent)  # , controller, 16)
        self.controller = controller
        self.parent = parent

        self.tb = self.init_phrase_toolbar(parent)

        SONGSTEP_COLS = {
            'Action': 60, 'Value': 200, 'G1': 60, 'G2': 60, 'G3': 60, 'G4': 60,
        }

        # self = self = ScrolledTreeview(self)
        self.tv['columns'] = list(SONGSTEP_COLS.keys())
        self.tv.column('#0', stretch=0, width=100)
        for col, width in SONGSTEP_COLS.items():
            self.tv.heading(col, text=col)
            self.tv.column(col, stretch=1, width=width)  # , anchor=W)

        self.populate_roots(
            MAX_NUM_PHRASE, 'phrase', lambda s: f"Phrase {chr(ord('A')+s)}"
        )
        for p in range(MAX_NUM_PHRASE):
            self.populate_node(
                f'phrase{p:03}',
                NUM_STEP_PER_PHRASE,
                'step',
                lambda x: f'{songpos2str(8*p+x)}',
            )

        #self.tv.bind('<<TreeviewSelect>>', self.on_row_selected, add=True)
        #self.tv.bind('<<TreeviewInplaceEdit>>', self.on_row_edit  )
        # self.tv.bind('<<TreeviewCellEdited>>',self.on_cell_changed)

    def update_from_song(self):
        '''Update treeview items from song.'''
        if not self.song:
            return
        for p in range(MAX_NUM_PHRASE):
            self.update_phrase_from_song(p)
        self.autosize_columns()

    def update_phrase_from_song(self, p):
        logger.debug(f'update_phrase_from_song {p}')
        empty = True
        last_action = ''
        for s in range(NUM_STEP_PER_PHRASE):
            sp = songpos2str(8*p+s)
            step = self.song.get_step(8*p+s)
            step = [v.strip() for v in step]
            item = f'phrase{p:03}_step{s:03}'
            # print(sp,item,step)
            tag = 'empty' if last_action == 'End' else ''
            self.tv.item(
                item,
                values=step,
                tag=tag,
            )
            last_action = step[0]
            if last_action != 'End':
                empty = False

        tag = 'empty' if empty else ''
        self.tv.item(f'phrase{p:03}', tag=tag)

    # PHRASE METHODS
    def init_phrase_toolbar(self, parent):
        bf = Frame(parent)
        buttons = [
            (Button, 'Collapse All', lambda: self.open_all(False), None, 2),
            (Button, 'Expand All', self.open_all, None, 2),
            # (Checkbutton, 'Show End', lambda: None, self.end_visible),
            # (Checkbutton, 'Allow Edit', lambda: None, self.allow_edit),
            (Button, 'Clear', self.clear_phrase, None, -1),
            (Button, 'Preset', self.on_preset_phrase, None, -1),
        ]
        for widget, name, cmd, var, ul in buttons:
            btn = widget(bf, text=name, command=cmd,
                         variable=var, underline=ul)
            btn.pack(side=LEFT)
        return bf

    # def open_all(self, o=True):
    #    for i in self.tv.get_children():
    #        self.tv.item(i, open=o)
    #
    # def collapse_all(self):
    #     self.open_all(False)

    def on_preset_phrase(self):
        sel = self.tv.selection()
        sel_phr = [s for s in sel if not '_' in s]
        print(sel_phr)
        for phr in sel_phr:
            np = int(phr[-3:])
            self.preset_phrase(np)
        self.update_phrase_from_song(np)

    def on_cell_changed(self, event):
        (col, item) = self.tv.get_event_info()
        logger.info(f'Column {col} of item {item} was changed')
        values = self.tv.item(item, 'values')
        logger.debug(f'{item} {values}')

    def on_row_edit(self, event):
        col, item = self.tv.get_event_info()
        logger.debug(f'on_row_edit phrase {col} {item}')
        if not 'step' in item:
            return
        if col == 'Action':
            self.tv.inplace_combobox(col, item, values=SONG_ACTIONS)
        if col == 'Value':
            self.tv.inplace_entry(col, item)
        if 'G' in col:
            self.tv.inplace_entry(col, item)

    # --> move to controller

    def preset_phrase(self, np):
        '''My variation of Save & Take over Patterns.'''
        if not self.song:
            return
        self.song.steps[8*np]._set(21, 0xF)
        self.song.steps[8*np+1]._set(19, np)
        for p in range(4):
            npn1 = idx2npn(0, (8*np+p) % 64)
            npn2 = idx2npn(1, (8*np+p) % 64)
            npn3 = idx2npn(2, (8*np+p) % 64)
            npn4 = idx2npn(3, (8*np+p) % 64)
            self.song.steps[8*np+2+p]._set(1, np, npn1, npn2, npn3, npn4)
        self.song.steps[8*np+6]._set(0, 0)
        self.song.modified()

    def clear_phrase(self):
        '''Clear phrase.'''
        if not self.song:
            return
        sel = self.tv.selection()
        sel_phr = [s for s in sel if not '_' in s]
        print(sel_phr)
        for phr in sel_phr:
            np = int(phr[-3:])
            for step in range(NUM_STEP_PER_PHRASE):
                self.song.steps[8*np+step].clear()
            logger.info(f'Clear phrase {phr}.')
            self.update_phrase_from_song(np)
        self.song.modified()


class SongBankEditor(ScrolledTreeview):
    '''Song Bank Editor / Selector + Toolbar'''

    def __init__(self, parent, controller):
        super().__init__(parent)
        # self.pack(fill=BOTH, expand=TRUE)
        self.parent = parent
        self.controller = controller

        self.tb = self.init_song_toolbar(parent)

        self.tv['columns'] = ('name',)
        self.tv.column('#0', width=60, stretch=0)
        self.tv.column('name', width=200, stretch=1)
        self.tv.heading('#0', text=f'Nr.')
        self.tv.heading('name', text=f'Name')
        self.populate_roots(MAX_NUM_SONGS, 'song')

        self.tv.bind('<<TreeviewSelect>>', self.select_song, add=True)
        #self.tv.bind('<<TreeviewCellEdited>>', self.on_cell_changed)
        # self.tv.bind('<<TreeviewInplaceEdit>>', self.on_row_edit
        # self.tv.focus('song000')
        # self.tv.selection_set('song000')

    # CALLBACKS
    def on_cell_changed(self, event):
        (col, item) = self.tv.get_event_info()
        logger.info(f'Column {col} of item {item} was changed')
        item = self.tv.item(item)
        #dump(item)
        self.song.name = item['values'][0][:18]
        self.song.modified()

    def on_row_edit(self, event):
        (col, item) = self.tv.get_event_info()
        logger.debug(f'on_row_edit song {col} {item}')
        if col == 'name':
            self.tv.inplace_entry(col, item)
        # self.tv.inplace_spinbox(col, item, 0, 127, 1)

    # SONG+PHRASE METHODS
    def select_song(self, event):
        tv = self.tv
        item = tv.focus()
        logger.debug(f'select_song {item} {tv.selection()}')
        song = int(item[-2:])+1
        if 0 < song < MAX_NUM_SONGS:
            self.controller.do('set_song', song)
            self.song = self.controller.song
            # logger.debug(f'select_song {song} {self.song}')
            self.parent.update_from_song()
        # return event

    def update_from_session(self):
        self.song_bank = self.controller.session.song_bank
        self.song_bank.has_modifications()
        for s in range(MAX_NUM_SONGS):
            item = f'song{s:03}'
            song = self.song_bank.songs[s]
            m = song.modified_symbol()
            if not song.name or song.name.isspace():
                name = f'<Song {s:3} >'
                tag = 'empty'
            else:
                logger.debug(f'update_from_session Song {s} "{song.name}"')
                name = song.name
                tag = ''
            self.tv.item(item, text=f'{m}{s:3}', values=[name], tag=tag)
        #self.autosize_columns()

    # SONG METHODS
    def init_song_toolbar(self, parent):
        bf = Frame(parent)
        buttons = [
            (Button, 'Clear', self.clear_song, None),
            (Button, 'Preset', self.preset_song, None),
        ]
        for widget, name, cmd, var in buttons:
            btn = widget(bf, text=name, command=cmd, variable=var)
            btn.pack(side=LEFT)
        return bf

    def clear_song(self):
        for item in self.tv.selection():
            nsong = int(item[-2:])+1
            self.song = self.controller.do('clear_song',nsong)
            logger.info(f'Clear song {nsong} {self.song}.')
        self.update_from_session()

    def preset_song(self):
        for item in self.tv.selection():
            nsong = int(item[-2:])+1
            self.song = self.controller.set_song(nsong)
            self.parent.phr.song = self.song
            logger.info(f'Set preset to {nsong} {self.song}.')
            for p in range(MAX_NUM_PHRASE):
                self.parent.phr.preset_phrase(p)
            if self.song.name.isspace():
                self.song.name = 'Song Preset'
            self.song.modified()
        self.select_song()
        self.update_from_session()
