
""" Constants and Helpers
"""

import logging
import os
from collections import OrderedDict
from pprint import pprint
from tkinter import font

LOGW_LEVEL = 10
LOGW_NAME = 16
logging.basicConfig(
    level=logging.INFO,
    format=f'{"%(levelname)s":10}: %(name)s: %(message)s',
)

logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


PAR_MAX_BYTES = 1024
TRG_MAX_BYTES = 256

MAX_NUM_BANKS = 4
MAX_NUM_PATTERN = 64
MAX_NUM_TRACKS = 4
MAX_NUM_MAPS = 127
MAX_NUM_SONGS = 64
MAX_NUM_SONG_STEPS = 128
MAX_NUM_PHRASE = 16
NUM_STEP_PER_PHRASE = 8  # MAX_NUM_SONG_STEPS // MAX_NUM_PHRASE

# move to midi_port.py?

# from mios32_midi.h

MIDI_PORTS = (
    #   mios32                 in   out     clk
    ('DEFAULT', 0x00, 'Def.', 'Def.', 'Def.', ),
    ('MIDI_DEBUG', 0x01, '----', '----', '----', ),
    ('USB0', 0x10, 'USB1', 'USB1', 'USB1', ),
    ('USB1', 0x11, 'USB2', 'USB2', 'USB2', ),
    ('USB2', 0x12, 'USB3', 'USB3', 'USB3', ),
    ('USB3', 0x13, 'USB4', 'USB4', 'USB4', ),
    ('USB4', 0x14, 'USB5', 'USB5', 'USB5', ),
    ('USB5', 0x15, 'USB6', 'USB6', 'USB6', ),
    ('USB6', 0x16, 'USB7', 'USB7', 'USB7', ),
    ('USB7', 0x17, 'USB8', 'USB8', 'USB8', ),
    ('UART0', 0x20, 'IN1 ', 'OUT1', 'MID1', ),
    ('UART1', 0x21, 'IN2 ', 'OUT2', 'MID2', ),
    ('UART2', 0x22, 'IN3 ', 'OUT3', 'MID3', ),
    ('UART3', 0x23, 'IN4 ', 'OUT4', 'MID4', ),
    ('IIC0', 0x30, 'IIC1', 'IIC1', 'IIC1', ),
    ('IIC1', 0x31, 'IIC2', 'IIC2', 'IIC2', ),
    ('IIC2', 0x32, 'IIC3', 'IIC3', 'IIC3', ),
    ('IIC3', 0x33, 'IIC4', 'IIC4', 'IIC4', ),
    ('IIC4', 0x34, 'IIC5', 'IIC5', 'IIC5', ),
    ('IIC5', 0x35, 'IIC6', 'IIC6', 'IIC6', ),
    ('IIC6', 0x36, 'IIC7', 'IIC7', 'IIC7', ),
    ('IIC7', 0x37, 'IIC8', 'IIC8', 'IIC8', ),
    ('OSC0', 0x40, 'OSC1', 'OSC1', 'OSC1', ),
    ('OSC1', 0x41, 'OSC2', 'OSC2', 'OSC2', ),
    ('OSC2', 0x42, 'OSC3', 'OSC3', 'OSC3', ),
    ('OSC3', 0x43, 'OSC4', 'OSC4', 'OSC4', ),
    ('OSC4', 0x44, 'OSC5', 'OSC5', 'OSC5', ),
    ('OSC5', 0x45, 'OSC6', 'OSC6', 'OSC6', ),
    ('OSC6', 0x46, 'OSC7', 'OSC7', 'OSC7', ),
    ('OSC7', 0x47, 'OSC8', 'OSC8', 'OSC8', ),
    #  ( 'SPIM0'     , 0x50, '----', '----', '----', ),
    #  ( 'SPIM1'     , 0x51, '----', '----', '----', ),
    #  ( 'SPIM2'     , 0x52, '----', '----', '----', ),
    #  ( 'SPIM3'     , 0x53, '----', '----', '----', ),
    #  ( 'SPIM4'     , 0x54, '----', '----', '----', ),
    #  ( 'SPIM5'     , 0x55, '----', '----', '----', ),
    #  ( 'SPIM6'     , 0x56, '----', '----', '----', ),
    #  ( 'SPIM7'     , 0x57, '----', '----', '----', ),
    ('', 0x80, 'CV1 ', 'CV1 ', '----', ),
    ('', 0x81, 'CV2 ', 'CV2 ', '----', ),
    ('', 0x82, 'CV3 ', 'CV3 ', '----', ),
    ('', 0x83, 'CV4 ', 'CV4 ', '----', ),
    ('', 0xf0, 'Bus1', 'Bus1', '----', ),
    ('', 0xf1, 'Bus2', 'Bus2', '----', ),
    ('', 0xf2, 'Bus3', 'Bus3', '----', ),
    ('', 0xf3, 'Bus4', 'Bus4', '----', ),
)

MIDI_OUT_PORT = {}
MIDI_OUT_PORTS_LIST = []
for m32, idx, midi_in, midi_out, midi_clk in MIDI_PORTS:
    MIDI_OUT_PORTS_LIST.append(midi_out)
    MIDI_OUT_PORT[idx] = midi_out
    MIDI_OUT_PORT[midi_out] = idx

#def midi_out_port(port):
#    for m32, idx, midi_in, midi_out, midi_clk in MIDI_PORTS:
#        if idx == port:
#            return midi_out
#    return 0xff


class SeqV4PError(Exception):
    pass


def is_builtin(obj):
    return obj.__class__.__module__ == '__builtin__'


def dump(obj, depth=1):
    print(f'{" ":20}  {obj}')
    if depth == 0:
        return
    try:
        vars_obj = vars(obj)
    except TypeError:
        #logging.error(f'{obj}: {e}')
        return
    for k, v in vars_obj.items():
        if k == 'parent':
            # only interesting for modification notifications
            print(f'{k:>20}: {v}')
            continue
        t = type(v).__name__
        #t = str(type(v)).split("'")[1]
        if isinstance(v, bytes):
            print(f"{k:>20}: {len(v)} bytes")
        elif isinstance(v, bytearray):
            print(f"{k:>20}: {len(v)} bytearray")
        elif isinstance(v, OrderedDict):
            print(f"{k:>20}: {t} {list(v.keys())}")
            # if depth == 1:
            #    print(f"{k:>20}: {v.keys()}")
            if depth > 1:
                w = len(max(v.keys(), key=len))
                for key, obj in v.items():
                    print(f"{key:>{w}}: {obj}")
        elif isinstance(v, dict):
            # if depth == 1:
            print(f"{k:>20}: {v.keys()}")
            if depth > 1:
                print(f"{k:>20}: {v}")
                for key, obj in v.items():
                    if hasattr(obj, '__dict__'):
                        #print(f"KEY {key:16}:")
                        dump(obj, depth-1)
                print()
        elif isinstance(v, list):
            #print(f"{k:>20}: {*v,}")
            sep_v = f'\n{" ":20}  '.join(repr(x) for x in v)
            print(f"{k:>20}: {sep_v}")
            # if depth == 1:
            #    print(f"{k:>20}: [...] list {len(v)} items")
            if depth > 1:
                #print(f"{k:>20}: {v}")
                for obj in v:
                    if hasattr(obj, '__dict__'):
                        #print(f"ITEM {obj}:")
                        dump(obj, depth-1)
                print()
        elif isinstance(v, str):
            print(f"{k:>20}: '{v}'")
        elif isinstance(v, (int, set)):
            print(f'{k:>20}: {v}')
        else:
            print(f'{k:>20}: {v}')
            if depth > 1:
                dump(v, depth-1)
                print()
            # print(k,v)
        #pprint(v, depth=1)


def songpos2str(n):
    return f"{chr(n//8+ord('A'))}{n%8+1}"


def ntrack2gt(ntrack):
    g = int(ntrack)//4
    t = int(ntrack) % 4
    return f'G{g+1}T{t+1}'


def idx2npn(nbank, npattern):
    """Numerical pattern name from bank, pattern index"""
    #nbank = int(npn[0])-1
    #npattern = (ord(npn[2])-ord('A'))*8 +int(npn[3])-1
    if nbank > 3 or npattern > 64:
        return f'-:--'
    return f"{nbank+1}:{chr(npattern//8+ord('A'))}{npattern%8+1}"


def npn2idx(npn):
    """Bank, pattern index from numerical pattern name"""
    # print(npn)
    if npn == '-:--':
        return -1, 0x80
    try:
        nb = int(npn[0])-1
        # if not 0 <= nb < 4:
        #    logger.error('Wrong NPN {npn}.')
        # return -1, 0x80
        np = (ord(npn[2])-ord('A'))*8 + int(npn[3])-1
    except Exception as e:
        logger.error(f'{e}: {npn}')
        return -1, 0x80
    return nb, np


def entitify(text):
    return ''.join('&#%d;' % ord(c) for c in text)


def first(iterable, default=None, condition=lambda x: True):
    try:
        return next(x for x in iterable if condition(x))
    except StopIteration:
        if default is not None and condition(default):
            return default
        else:
            raise


def measure_str(v):
    return font.Font(font='TkDefaultFont').measure(str(v))


def disable_children(parent):
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        if wtype not in ('TFrame', 'TLabelframe', 'Scrollbar'):
            #print (wtype)
            child.configure(state='disable')
        else:
            disable_children(child)


def enable_children(parent):
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        # print (wtype)
        if wtype not in ('Treeview', 'TFrame', 'TLabelframe', 'Scrollbar'):
            # if child['state'] != 'readonly':
            child.configure(state='normal')
        else:
            enable_children(child)
