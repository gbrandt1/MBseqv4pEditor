

import os
import logging
from struct import pack, unpack

from helpers import *
from observer import Observable

logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


SONG_PARS = [
    'Actn', 'AVal',
    'G1', 'G2', 'G3', 'G4',
    'BG1', 'BG2', 'BG3', 'BG4',
]

SONG_ACTIONS = [
    'End',
    'x1',
    'x2',
    'x3',
    'x4',
    'x5',
    'x6',
    'x7',
    'x8',
    'x9',
    'x10',
    'x11',
    'x12',
    'x13',
    'x14',
    'x15',
    'x16',
    'JmpPos',
    'JmpSong',
    'Mixer',
    'Tempo',
    'Mutes',
    'G.T.',
    'Unmte',
]


class SongStep():  # Observable):

    def __init__(self, parent, content=None):
        # super().__init__() #parent)
        #self.parent = parent
        if content:
            (
                self.action,
                self.action_value,
                self.pattern_g1,
                self.pattern_g2,
                self.pattern_g3,
                self.pattern_g4,
                bank_g
            ) = unpack('BBBBBBH', content[:8])
        else:
            self.clear()
        self.bank_g1 = (bank_g) & 0x0f
        self.bank_g2 = (bank_g >> 4) & 0x0f
        self.bank_g3 = (bank_g >> 8) & 0x0f
        self.bank_g4 = (bank_g >> 12) & 0x0f
        # self.unmodified()

    def clear(self):
        self.action = 0
        self.action_value = 0
        self.pattern_g1 = 0x80
        self.pattern_g2 = 0x80
        self.pattern_g3 = 0x80
        self.pattern_g4 = 0x80
        self.bank_g1 = 0
        self.bank_g2 = 1
        self.bank_g3 = 2
        self.bank_g4 = 3

    def write(self):
        bank_g  = (self.bank_g1)& 0x0f
        bank_g |= (self.bank_g2 << 4)
        bank_g |= (self.bank_g2 << 8)
        bank_g |= (self.bank_g2 << 12)
        bank_g &= 0xFFFF
        content = pack(
            'BBBBBBH',
            self.action,
            self.action_value,
            self.pattern_g1,
            self.pattern_g2,
            self.pattern_g3,
            self.pattern_g4,
            bank_g
        )
        return content

    def _set(
        self, action=0, value=0,
        npn1='-:--', npn2='-:--', npn3='-:--', npn4='-:--'
    ):
        self.action = action
        self.action_value = value

#    self.groups_str(self)
        self.bank_g1, self.pattern_g1 = npn2idx(npn1)
        self.bank_g2, self.pattern_g2 = npn2idx(npn2)
        self.bank_g3, self.pattern_g3 = npn2idx(npn3)
        self.bank_g4, self.pattern_g4 = npn2idx(npn4)

    def mutes(self, value):
        m = f'{value:>016b}'
        m = m.replace('0', '\u25CF')
        m = m.replace('1', '\u25CB')
        return f'{m[0:4]:8}{m[4:8]:8}{m[8:12]:8}{m[12:16]:8}'

    def str_groups(self):
        g1 = idx2npn(self.bank_g1, self.pattern_g1)
        g2 = idx2npn(self.bank_g2, self.pattern_g2)
        g3 = idx2npn(self.bank_g3, self.pattern_g3)
        g4 = idx2npn(self.bank_g4, self.pattern_g4)

        return (f'{g1:8}', f'{g2:8}', f'{g3:8}', f'{g4:8}')

    def str_action(self):
        action = SONG_ACTIONS[self.action]
        return f'{action:8}'

    def str_action_value(self):
        action = SONG_ACTIONS[self.action]
        value = self.action_value

        result = f'<{value}>'
        if action in (
            'x1', 'x2', 'x3', 'x4', 'x5', 'x6''x7', 'x8',
            'x9', 'x10', 'x11', 'x12', 'x13', 'x14', 'x15', 'x16',
        ):
            # default: x1 ... x16
            result = ''  # f"{action:8}"
        else:
            result = {
                'End': '',
                'JmpPos': f'{songpos2str(value):8}',
                'JmpSong': f'Song {value+1:<3}',
                'Mixer': f'Map {value+1:<4}',
                'Tempo': f'BPM {value:<4}Ramp {self.pattern_g1:<4}',
                'Mutes': f'{self.mutes(value)}',
                'G.T.': f'Guide {ntrack2gt(value)}',
                'Unmte': '',
            }[action]

        return result

    def __repr__(self):
        step = self.str_action() +\
            self.str_action_value() +\
            ''.join(self.str_groups())
        return step


class Song(Observable):

    def __init__(self, parent, content=None):
        super().__init__(parent)
        if content:
            (
                self.name,
                self.guide,
                dummy
            ) = unpack('18sBB', content[:20])
        else:
            self.clear()
        # .replace(' ','\uFE4D') #'\u00B7')
        self.name = self.name.decode("utf-8").replace('\x00', ' ').strip()
        self.steps = []
        #self.nsteps = M
        for ps in range(MAX_NUM_SONG_STEPS):
            if content:
                step = SongStep(self, content[20+ps*8:20+(ps+1)*8])
            else:
                step = SongStep(self)
            self.steps.append(step)
        logger.debug(self)

    def write(self):
        #logger.info(f'Write song {self}')
        content = pack(
            '18sBB',
            bytes(f'{self.name:18}', 'utf-8'),
            #self.name,
            self.guide,
            0x00
        )
        for s in self.steps:
            content += s.write()
        return content

    def get_step(self, sp):
        step = self.steps[sp]
        return (step.str_action(), step.str_action_value()) + step.str_groups()

    def clear(self):
        self.name = ''
        self.guide = 32
        [step.clear() for step in self.steps]

    #def modified(self, obj=None):
    #    if self.name.isspace():
    #        self.name = 'Unnamed'
    #    super().modified(obj)

    def debug(self):
        r = (
            f'{self}'
            f' Guide Track: {self.guide}'
            f"\n{'Pos':>8}{'Action':>8}{'G1':^8}{'G2':^8}{'G3':^8}{'G4':^8}"
        )
        for slot in range(MAX_NUM_PHRASE):
            # r += f"\n" #Slot {chr(ord('A')+slot)}"
            if self.steps[8*slot].action == 0:
                continue
            for step in range(8):
                ns = 8*slot + step
                # print(ns)
                r += f'\n {ns+1:3}: {songpos2str(ns):4}{self.steps[ns]}'
            r += f"\n"
        return r

    def __repr__(self):
        m = self.modified_symbol()
        return f'<Song: "{self.name}"{m}>'


class SongBank(Observable):

    def __init__(self, parent, filename):
        super().__init__(parent)
        self.filename = filename
        self.fullname = os.path.join(self.parent.path, self.filename)
        content = open(self.fullname, "rb").read()
        (
            self.header,
            self.name,
            self.num_songs,
            self.song_size
        ) = unpack('10s20sHH', content[:10+24])
        self.name = self.name.decode("utf-8")
        self.songs = []
        logger.info(self)
        for m in range(self.num_songs):
            song = Song(self, content[10+24+m*self.song_size:])
            self.songs.append(song)

    def write(self):
        logger.info(f'Write {self.fullname}')
        content = pack(
            '10s20sHH',
            self.header,
            bytes(f'{self.name:20}', 'utf-8'),
            self.num_songs,
            self.song_size
        )
        for s in self.songs:
            content += s.write()
        with open(self.fullname, "wb") as f:
            f.write(content)

    def __getitem__(self, key):
        return self.songs[key]

    def __repr__(self):
        m = self.modified_symbol()
        return (
            f'<{__class__.__name__}: "{self.name}">'
            f'{m}'
            # return (
            #    f'<Song Bank: {self.name} {m}> {self.filename}'
            #    f' Songs: {len(self.songs)}/{self.num_songs} ({self.song_size}b)'
        )
