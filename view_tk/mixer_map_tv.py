

import logging
import os
from tkinter import *
from tkinter.ttk import *

from view_tk.editabletreeview import *

MMAP_PAGE_NAME = (
   "MIDI Port   ", "MIDI Channel", "Prog.Change ", "Volume      ",
   "Panorama    ", "Reverb      ", "Chorus      ", "ModWheel    ",
   "CC1         ", "CC2         ", "CC3         ", "CC4         ",
   "CC1 Assign  ", "CC2 Assign  ", "CC3 Assign  ", "CC4 Assign  ",
)

#MMAP_PAGE_NAME = (
#    "Port  ", "Chan  ", "ProgCh", "Volume",
#    "Pano  ", "Reverb", "Chorus", "ModWhe",
#    "CC1   ", "CC2   ", "CC3   ", "CC4   ",
#    "Asgn1 ", "Asgn2 ", "Asgn3 ", "Asgn4 ",
#)

#logger = logging.getLogger(os.path.basename(__file__))
logger = logging.getLogger(f'{__name__:20}')


class MMapTreeview(Frame):

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # State
        self.allow_edit = BooleanVar(value=False)

        # Widgets
        frm_tb = self.init_toolbar()
        frm_tv = self.init_treeview()

        frm_tb.pack(fill=X)
        frm_tv.pack(fill=BOTH, expand=TRUE)

        self.connect_callbacks()
        self.open_all(False)

    def init_toolbar(self):
        bf = Frame(self)
        buttons = (
            (Button, 'Collapse All', lambda: self.open_all(False), None),
            (Button, 'Expand All', lambda: self.open_all(), None),
            (Checkbutton, 'Allow Edit', lambda: None, self.allow_edit),
            (Button, 'Clear', self.clear, None),
        )
        for widget, name, cmd, var in buttons:
            btn = widget(bf, text=name, command=cmd, variable=var)
            btn.pack(side=LEFT)
        return bf

    def init_treeview(self):
        frm_tv = Frame(self)

        self.tv = EditableTreeview(frm_tv, selectmode=EXTENDED)
        self.tv["columns"] = (
            [f'#{i+1}' for i in range(16)]  # len(MMAP_PAGE_NAME))]
        )
        for i in range(16):  # len(MMAP_PAGE_NAME)):
            self.tv.column(
                f'#{i+1}',
                # stretch=False,
                width=3,
                anchor=E
            )
            self.tv.heading(
                f'#{i+1}',
                text=f'{i+1}',  # { MMAP_PAGE_NAME[i]}'
            )

        self.vsb = Scrollbar(frm_tv, orient=VERTICAL, command=self.tv.yview)
        self.tv.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side=RIGHT, fill=Y)
        self.tv.pack(side=LEFT, fill=BOTH, expand=TRUE)
        return frm_tv

    def connect_callbacks(self):
        self.tv.bind(
            "<MouseWheel>", lambda event: self.tv.yview(
                "scroll", -event.delta, "units"))
        # Treeview bindings
        self.tv.bind('<<TreeviewSelect>>', self.on_row_selected, add=True)
        # <<TreeviewOpen>>
        # <<TreeviewClose>>
        # EditableTreeview bindings
        self.tv.bind('<<TreeviewCellEdited>>', self.on_cell_changed)
        self.tv.bind('<<TreeviewInplaceEdit>>', self.on_row_edit)

    def set_mixer_map_bank(self, mmb):
        self.mixer_map_bank = mmb
        self.mixer_map = 0
        self.init_items()
        self.open_all()
        self.tv.focus('mmap00')
        self.tv.selection_set('mmap00')

    def init_items(self):
        # logger.info(f'init_items')
        tv = self.tv
        # Save open state
        open_state = {}
        for i in tv.get_children():
            open_state[i] = tv.item(i)['open']

        tv.delete(*tv.get_children())
        #  Mixer Map Names
        num_maps = self.mixer_map_bank.num_maps
        for mm in range(num_maps):
            self.mixer_map = self.mixer_map_bank.mixer_maps[mm]
            mmn = self.mixer_map.name
            tv.insert(
                '', 'end', f'mmap{mm:02}',
                text=f'MixerMap {mm+1:02} {mmn:20}',
            )
            for par in range(16):
                chn = [int]*16
                for c in range(16):
                    chn[c] = self.mixer_map.slots[c][par]
                self.tv.insert(
                    f'mmap{mm:02}', 'end', f'mmap{mm:02}_{par:02}',
                    text=f'{MMAP_PAGE_NAME[par]}',
                    #f'{s+1:02}',
                    values=chn  # self.mixer_map.slots[s]
                )

        # Restore open state
        for i in tv.get_children():
            if i in open_state:
                tv.item(i, open=open_state[i])

    def on_cell_changed(self, event):
        (col, item) = self.tv.get_event_info()
        logger.info(f'Column {col} of item {item} was changed')

        values = self.tv.item(item, 'values')
        print(item, values)

        #if self.mixer_map.name.isspace():
        #    self.mixer_map.name = "Unnamed             "

        self.mixer_map.modified()

    def on_row_selected(self, event):
        logger.info(f'MMap rows selected {event.widget.selection()}')
        #mn = int(item[4:5])
        #print(mn)
        #self.mixer_map = self.mixer_map_bank.mixer_maps[mn]


    def on_row_edit(self, event):
        # Get the column id and item id of the cell
        # that is going to be edited
        col, item = self.tv.get_event_info()
        cn = int(str(col).replace('#', ''))
        #print(f'MMap row edit {col} {cn} {item}')
        if cn > 0 and self.allow_edit.get():
            #self.tv.inplace_entry(col, item)
            self.tv.inplace_spinbox(col, item, 0, 127, 1)

    def clear(self):
        """Clear selected rows to default value"""
        for item in self.tv.selection():
            logger.info(f'Clear {item}')

    def open_all(self, o=True):
        for i in self.tv.get_children():
            self.tv.item(i, open=o)

    def collapse_all(self):
        self.open_all(False)
