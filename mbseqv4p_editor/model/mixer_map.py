import os
import logging
from struct import unpack

from ..helpers import *
from ..observer import Observable

# logger = logging.getLogger(os.path.basename(__file__))
logger = logging.getLogger(f"{__name__:{LOGW_NAME}}")

# mixer_pars = [ 'Port','Chan','Prg','Vol','Pano','Rev','Chor','Modw',
#               'CC1v','CC2v','CC3v','CC4v','nCC1','nCC2','nCC3','nCC4' ]
MIXER_PARS = (
    "MIDI Port",
    "MIDI Channel",
    "Prog.Change",
    "Volume",
    "Panorama",
    "Reverb",
    "Chorus",
    "ModWheel",
    "CC1",
    "CC2",
    "CC3",
    "CC4",
    "Ass.#CC1",
    "Ass.#CC2",
    "Ass.#CC3",
    "Ass.#CC4",
)


class MixerMap(Observable):
    def __init__(self, parent, content):
        super().__init__(parent)
        (self.name, self.num_chn, self.num_par) = unpack("20sBB", content[:22])
        # i=22
        self.name = self.name.decode("utf-8")
        self.slots = []
        for c in range(self.num_chn):
            # print 'Slot {:2d}:'.format(c),
            # print ''.join('{:4d} '.format(ord(x)) for x in self.content[i+22+c*16:i+22+(c+1)*16])
            slot = [x for x in content[22 + c * 16 : 22 + (c + 1) * 16]]
            self.slots.append(slot)
        # if self.name.strip():
        # logging.info(self)

    def write(self):
        logger.info(f"Write mixer map {self}")

    def reset(self):
        # clear
        for chn in range(self.num_chn):
            for par in range(self.num_par):
                self.slots[chn][par] = 0
                self.slots[chn][1] = chn & 0x0F
            self.slots[chn][8] = 16
            self.slots[chn][9] = 17
            self.slots[chn][10] = 18
            self.slots[chn][11] = 19

    def __getitem__(self, nslot):
        if 0 <= nslots < self.num_chn:
            return self.slots[nslot]
        else:
            logger.warn("Wrong mixer map number.")

    def __repr__(self):
        m = self.modified_symbol()
        return (
            f'<Mixer Map: "{self.name}">{m}'  # {len(self.name.strip())}'
            #   f' Channels: {self.num_chn} Parameters: {self.num_par}'
        )
        # '        '+''.join('{:4s} '.format(p)
        #                         for p in mixer_pars[:self.num_par]))
        # for c in range(self.num_chn):
        #    print('Slot {:2d}:'.format(c),)
        #    print(''.join('{:4d} '.format(ord(x)) for x in self.slots[c]))
        # return cr


class MixerMapBank(Observable):
    def __init__(self, parent, filename):
        super().__init__(parent)
        self.filename = filename
        fullname = os.path.join(self.parent.path, self.filename)
        content = open(fullname, "rb").read()
        # header = unpack('10s', self.content[:10])
        # print 'Header:',repr(header)
        (self.header, self.name, self.num_maps, self.map_size) = unpack(
            "10s20sHH", content[: 10 + 24]
        )
        if self.header != b"MBSEQV4_M\x00":
            raise SeqV4PError(f"Corrupt header in Mixer Map!")
        self.name = self.name.decode("utf-8")
        logger.info(self)
        self.mixer_maps = []
        for m in range(self.num_maps):
            mixer_map = MixerMap(self, content[10 + 24 + m * self.map_size :])
            self.mixer_maps.append(mixer_map)

    def write(self):
        if self.has_modifications():
            logger.info(f"Write {self}")
            for m in self.mixer_maps:
                m.write()

    def __getitem__(self, nmap):
        if 0 < nmap < self.num_maps:
            return self.mixer_maps[nmap]
        else:
            logger.warn("Wrong mixer map number.")

    def __repr__(self):
        m = self.modified_symbol()
        return (
            f"<{__class__.__name__}: {self.name}>"
            f"{m}"
            # f' File: {self.filename}'
            # f' Maps: {self.num_maps} Reserved: {self.map_size}b'
        )
