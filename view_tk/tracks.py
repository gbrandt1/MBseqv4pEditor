
import logging
import os
from tkinter import *
from tkinter.messagebox import askokcancel
from tkinter.ttk import *

from helpers import *
from track_cc import TRACK_LAYER_CONFIG
from view_tk.scrolledtreeview import ScrolledTreeview

logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


class TracksView(ScrolledTreeview):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.pack(fill=BOTH, expand=TRUE)
        self.controller = controller

        # State

        # Widgets
        self.populate_roots(16, 'track', lambda x: f'Track {x+1:2}')

#        for item in self.tv.get_children():
#            self.populate_node(item)
#            print(item)

        columns = (
            'cat', 'label', 'layers', 'steps',
            'length', 'midi_port', 'midi_channel', 'mute',
        )

        self.colidx = {c: n for (n, c) in enumerate(columns)}
        # print(self.cols)

        self.tv.configure(columns=list(columns))

        for col in columns:
            self.tv.heading(col, text=col.capitalize())
            self.tv.column(col, stretch=1, width=60)

        enable_children(self)

        #self.tv.pack(fill=BOTH, expand=TRUE)

    def set_from_phrase(self):
        # self.phrase = self.controller.phrase
        # logger.info(f'set_from_phrase {self.controller.tracks}')
        for n, track in enumerate(self.controller.tracks):
            if not track:
                continue
            drum = (track.event_mode == 'Drum')
            values = [
                track.cat if not drum else '',
                track.label if not drum else '',
                f'{track.layer_config_repr()}',
                f'{track.num_par_steps} / {track.num_trg_steps}',
                f'{track.length}',
                f'{track.midi_port_}',
                f'{track.midi_channel:2}',
                ''
            ]
            item = f'track{n:03}'
            m = track.modified_symbol()
            text = f'Track {n:3}{m}'
            self.tv.item(item, text=text, values=values, tag='')
            #logger.info(f'{item}: {text} {values}')
        self.autosize_columns()
        self.deselect_all()  # tv.selection() #_clear()

    def set_track(self, nt):
        '''Select current track.'''
        item = f'track{nt:03}'
        if (item in self.tv.selection() and
                len(self.tv.selection()) == 1):
            return
        logger.info(f'set_track: {nt}')
        self.deselect_all()  # tv.selection_clear()
        self.tv.selection_add(item)
        self.tv.focus(item)
        self.controller.show_status()

    # Callbacks
    def on_copy(self):
        trksel = []
        for item in self.tv.selection():
            if 'track' in item:
                trksel.append(int(item[5:8]))
        logger.info(f'on_copy {trksel}')
        self.controller.do('copy_track', trksel)

    def on_paste(self):
        trksel = []
        for item in self.tv.selection():
            if 'track' in item:
                trksel.append(int(item[5:8]))
        # self.deselect_all()
        logger.info(f'on_paste {trksel}')
        self.event_generate('<FocusOut>')
        self.controller.do('paste_track', trksel)

    def on_clear(self):
        for item in self.tv.selection():
            if 'track' in item:
                trksel.append(int(item[5:8]))
        logger.info(f'on_clear {trksel}')
        self.controller.do('clear_track', trksel)

    # Callbacks from Treeview
    def on_row_selected(self, event):
        # self.controller.show_status()
        pass
        # if not self.tv.selection():
        #    return
        #logger.info(f'on_row_selected {event.widget.selection()}')
        # for item in self.tv.selection():
        #    for item2 in self.tv.get_children(item):
        #        if item2 not in self.tv.selection():
        #            self.tv.selection_add(item2)
        #item = self.tv.selection()[0]
        #logger.info(f'on_row_selected first {item}')
        #n = int(item[5:8])
        #track = self.controller.tracks[n]
        # self.controller.set_track(n)  # = track

    # Callbacks from EditableTreeview
    def on_cell_changed(self, event):
        (col, item) = self.tv.get_event_info()
        logger.info(f'Column {col} of item {item} was changed')
        values = self.tv.item(item, 'values')
        logger.info(f'{item} {values}')

        n = int(item[5:8])
        track = self.controller.tracks[n]
        if col == 'cat':
            track.cat = values[0]
        if col == 'label':
            track.label = values[1]
        if col == 'layers':
            if track.layer_config != values[2]:
                # askokcancel(
                #     f'Reconfigure track {track.layer_config_repr()}',
                #     f'Really reconfigure track to\n\n{values[2]}?'
                # )
                track.configure(values[2])
                #self.controller.set_track(n)  # = track
        if col == 'length':
            track.length = values[4]
        if col == 'midi_port':
            track.midi_port_ = values[5]
        if col == 'midi_channel':
            track.midi_channel = int(values[6].strip())
        if col == 'mute':
            pass
        # track.set_attr_from
        track.modified()
        self.set_from_phrase()

    def on_row_edit(self, event):
        col, item = self.tv.get_event_info()
        logger.debug(f'on_row_edit {col} {item}')
        #self.tv.inplace_entry(col, item)
        #self.tv.inplace_spinbox(col, item, 0, 127, 1)
        if not self.controller.sdcard:
            return
        vcat = self.controller.sdcard.trkcat.data
        vlabel = self.controller.sdcard.trklabel.data
        config_list = list(TRACK_LAYER_CONFIG.keys())
        midi_out_ports = list(MIDI_OUT_PORTS_LIST)

        # print(midi_out_ports)
        n = int(item[5:8])
        track = self.controller.tracks[n]
        drum = (track.event_mode == 'Drum')

        if col == 'cat' and not drum:
            self.tv.inplace_combobox(col, item, values=vcat, readonly=False)
        if col == 'label' and not drum:
            self.tv.inplace_combobox(col, item, values=vlabel, readonly=False)
        if col == 'layers':
            self.tv.inplace_combobox(col, item, values=config_list)
        if col == 'length':
            self.tv.inplace_spinbox(col, item, 1, 256, 1)
        if col == 'midi_port':
            self.tv.inplace_combobox(col, item, values=midi_out_ports)
        if col == 'midi_channel':
            self.tv.inplace_spinbox(col, item, 1, 16, 1)
        if col == 'mute':
            self.tv.inplace_checkbutton(col, item)
