

import logging

from helpers import *

logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


def item2ilp(item):
    # item format: instXX_parYY_pageZZ
    #              01234567890123456789
    i = l = p = False
    if 'inst' in item:
        i = int(item[4:6])
    if 'par' in item or 'trg' in item:
        l = int(item[10:12])
    if 'page' in item:
        p = int(item[17:19])
    # print(f'{item} --> {i} {l} {p}')
    return i, l, p


def item2blk(item):
    try:
        blk = item[7:10]
        return blk
    except:
        return False


class StepBuffer():
    '''Mediator class between track model and GUI.
    Keep track blocks (parameters and triggers) in values dictionary.
    (no Tk dependence but keys correspond to treeview item names)
    keep numerical values separate from representation
    '''

    def __init__(self):
        self.page_size = 16
        self.num_steps = self.page_size
        self.track = None
        self.values = {}
        # buffer for updated values
        self.values_ = {}

    # item loops

    def for_all_pars(self, func, **kwargs):
        # if not self.par_visible.get():
        #    return
        for pi in range(self.track.num_p_instruments):
            for pl in range(self.track.num_p_layers):
                item = f'inst{pi:02}_par{pl:02}'
                func(item, **kwargs)

    def for_all_trgs(self, func, **kwargs):
        # if not self.trg_visible.get():
        #    return
        for ti in range(self.track.num_t_instruments):
            for tl in range(self.track.num_t_layers):
                item = f'inst{ti:02}_trg{tl:02}'
                func(item, **kwargs)

    def for_all_pages(self, item, row_func=None, **kwargs):
        if 'par' in item:
            nump = self.track.num_par_steps//self.page_size
        else:
            nump = self.num_pages
        for pg in range(nump):
            row_func(item+f'_page{pg:02}', offset=pg*self.page_size, **kwargs)

    # Methods to copy from track

    def set_track(self, track):
        if not track:
            return
        self.track = track
        self.num_steps = self.track.num_trg_steps
        self.num_pages = self.num_steps//self.page_size
        self.num_par_pages = self.track.num_par_steps//self.page_size
        self.par_layer_types = self.track.get_par_layer_types()
        self.trg_layer_names = self.track.get_trg_layer_names()
        # self.populate_items()
        self.set_all_pages_from_track()
        # print(self.values)

    def set_all_pages_from_track(self):
        self.for_all_pars(
            self.for_all_pages, row_func=self.set_row_from_track)
        self.for_all_trgs(
            self.for_all_pages, row_func=self.set_row_from_track)

    def set_row_from_track(self, item, offset=0):
        '''Update row of numerical values from track'''
        #logger.info(f'set_row_from_track {item} offset={offset}')
        i, l, p = item2ilp(item)
        blk = item2blk(item)
        func_get = {
            'par': self.track.par_get,
            'trg': self.track.trg_get,
        }
        self.values[item] = [
            func_get[blk](step+offset, l, i)
            for step in range(self.page_size)
        ]
        # if not self.wrap.get():
        # vitem = item+f'_page{self.xv//self.page_size:02}'
        #   self.values[vitem] = self.values[item]

    def update_changed_values(self):
        '''Update numerical values with changed values_.
        '''
        for item in self.values_:
            values = [int(v) for v in self.values_[item]]
            i, l, p = item2ilp(item)
            blk = item2blk(item)
            s0 = p
            s1 = p+16
            #logger.info(f'update_track: {item:20}: {values} {s0} {s1}')
            for s in range(s0, s1):
                if blk == 'trg':
                    self.track.trg_set(s, l, i, values[s-s0])
                if blk == 'par':
                    self.track.par_set(s, l, i, values[s-s0])
            # Copy to numerical array
            self.values[item] = values
            #logger.info(f'update_changed_values: {item} = {self.values[item]}')
        self.values_ = {}
        # print(self)
        self.track.modified()

    def __repr__(self):
        buf = ''
        keys = list(self.values.keys())
        keys.sort()
        for item in keys:
            valstr = ' '.join([f'{v:4}' for v in self.values[item]])
            buf += f'{item:20}: {valstr}\n'
        return buf
