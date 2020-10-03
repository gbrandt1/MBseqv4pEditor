
from collections import OrderedDict
import string

# Trigger Layer Constants + Tools

def trg_layer_str(v):
    return '\u25CF' if v else '\u25CB'


# Parameter Layer Constants + Tools

vblocks = (
    '\u2581', '\u2582', '\u2583', '\u2584',
    '\u2585', '\u2586', '\u2587', '\u2588',
)
hblocks = (
    '\u258F', '\u258E', '\u258D', '\u258C',
    '\u258B', '\u258A', '\u2589', '\u2588',
)


def none_str(value):
    return '----'


def note_str(value):
    n = value
    notes = (
        'C-', 'C#', 'D-', 'D#', 'E-', 'F-',
        'F#', 'G-', 'G#', 'A-', 'A#', 'B-',
    )
    buf = notes[n % 12]+str(n//12 - 2)
    if n < 24:
        buf = buf[:2].lower()+buf[3]
    return buf


def chord_str(value):
    abc = string.ascii_lowercase
    ABC = string.ascii_uppercase
    ABCabc = ABC[:16]+abc[:16]
    # if 32 <= value < 96:
    return f'{ABCabc[n%32]}/{n>>5}'
    # return '----'


def vel_str(value):
    if not (0 <= value < 128):
        return '----'
    if value == 0:
        return '    '
    nv = 128//len(vblocks)
    idx = value//nv
    return f'{vblocks[idx]}'*4


def len_str(value):
    width = value//(101//4)
    remainder = value % (101//4)//4
    bar = '\u2588'*width
    return f'{bar}{hblocks[remainder]}'


def cc_str(value):
    if value >= 0x80:
        return '----'
    return f'{value:3}{vblocks[value//17]}'


def pitch_str(value):
    return cc_str(value)


def prob_str(value):
    prob = int(100*value/127)
    return f'{prob:3}%'
    return '----'


def delay_str(value):
    return '----'


def roll_str(value):
    if not value:
        return '----'
    v = int(value)
    rm = f'{((v&0x30)>>4)+2}'
    rm += 'U' if (v & 0x40) else 'D'
    rm += f'{v&0x0F:02}'
    return rm


def roll2_str(value):
    return '----'


def prgch_str(value):
    return '----'


def nth1_str(value):
    nth = ('--', 'Mu', 'Pl', 'Ac', 'Ro', 'Fx', 'Nx', '??')
    bars = value % 16 + 1
    mode = value >> 4 & 0x7
    buf = f'{nth[mode]}{bars:2}'
    return f'{buf:4}'


def nth2_str(value):
    return nth1_str(value)


def chrd2_str(value):
    return chord_str(value)


def aftch_str(value):
    return cc_str(value)


def root_str(value):
    keys = ("Glb ", " C  ", " C# ", " D  ", " D# ", " E  ",
            " F  ", " F# ", " G  ", " G# ", " A  ", " A# ", " B  ")

    return keys[value % 13]


def scale_str(value):
    if value == 0:
        return '----'
    return f'{value-1}'


def chrd3_str(value):
    return chord_str(value)


def ctrl_str(value):
    return cc_str(value)


PAR_TYPES = [
    # Name     Default Max  Map    Str
    ("None ", 0x00, 0x7f,  0, none_str),    # 0 None
    ("Note ", 0x3c, 0x7f,  1, note_str),    # 1 Note: C-3
    ("Chord", 0x40, 0x7f,  2, chord_str),   # 2 Chord1: A/2
    ("Vel. ", 100,  0x7f,  5, vel_str),     # 3 Velocity
    ("Len. ", 71,   101,   6, len_str),     # 4 Length
    # CC // NEW: overruled via seq_core_options.INIT_CC !!!
    (" CC  ", 0x80, 0x80,  7, cc_str),      # 5
    ("Pitch", 64,   0x80,  8, pitch_str),   # 6 PitchBender
    ("Prob.", 0,    0x7f, 11, prob_str),    # 7 Probability (reversed: 100%)
    ("Delay", 0,    0x7f, 12, delay_str),   # 8 Delay
    ("Roll ", 0,    0x7f, 13, roll_str),    # 9 Roll
    ("Roll2", 0,    0x7f, 14, roll2_str),   # 0 Roll2
    # 1 PrgCh // NEW: disabled by default
    ("PrgCh", 0x80, 0x80, 10, prgch_str),
    ("Nth1 ", 0,    0x7f, 15, nth1_str),    # 2 Nth1
    ("Nth2 ", 0,    0x7f, 16, nth2_str),    # 3 Nth2
    ("Chrd2", 0x40, 0x7f,  3, chrd2_str),   # 4 Chord2: A/2
    ("AfTch", 0,    0x80,  9, aftch_str),   # 5 Aftertouch: 0
    ("Root ", 0,    0x7f, 17, root_str),    # 6 Root: C
    ("Scale", 0,    0x7f, 18, scale_str),   # 7 Scale: 0
    ("Chrd3", 0x01, 0x7f,  4, chrd3_str),   # 8 Chord3: 1
    ("Ctrl ", 0x00, 0x80, 19, ctrl_str),    # 9 Ctrl
]

PAR_TYPES_LIST = []
for p in PAR_TYPES:
    PAR_TYPES_LIST.append({
        'name': p[0],
        'default': p[1],
        'max': p[2],
        'map': p[3],
        'str': p[4],
    })

PAR_TYPES = PAR_TYPES_LIST

PAR_TYPES_MAP = ['']*len(PAR_TYPES)
for p in PAR_TYPES:
    n = p['map']
    PAR_TYPES_MAP[n] = p


if __name__ == "__main__":

    p = PAR_TYPES[4]
    for n in range(0, p['max']+1):
        print(f"{n:3} {p['str'](n)}")

    from pprint import pprint

    # pprint(PAR_TYPES)
    # pprint(PAR_TYPES_MAP)
