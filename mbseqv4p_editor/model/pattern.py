import logging
import os
from pprint import pprint
from struct import pack, unpack

from ..helpers import *
from ..observer import Observable

from .track import Track

# logger = logging.getLogger(os.path.basename(__file__))
logger = logging.getLogger(f"{__name__:{LOGW_NAME}}")


class Pattern(Observable):
    def __init__(self, parent, content):
        super().__init__(parent)
        (
            self.name,
            self.num_tracks,
            self.mixer_map,
            self.sysex_setup,
            self.reserved1,
        ) = unpack("20sBBBB", content[:24])
        if self.num_tracks != MAX_NUM_TRACKS:
            raise SeqV4PError(
                f"Pattern does not have {MAX_NUM_TRACKS} tracks:" f" {self.num_tracks}"
            )
        i = 24
        self.name = self.name.decode("utf-8").replace("\x00", " ")
        self.cat = self.name[:5].strip()
        self.label = self.name[5:20].strip()
        # if len(self.cat+self.name) != 20:
        #    raise SeqV4PError(f'Pattern name "{self.cat}"-"{self.name}" wrong size {len(self.name)}')
        self.tracks = []
        for t in range(self.num_tracks):
            track = Track(self, content[i:])  # , self.name)
            i += track.size
            self.tracks.append(track)
        # logger.info(f'{self}')

    def clear(self):
        self.name = " " * 20
        self.num_tracks = 4
        self.mixer_map = 0
        self.sysex_setup = 0
        self.reserved1 = 0
        for t in range(self.num_tracks):
            self.tracks[t].clear()
            self.tracks[t].modified()

    def set_cat_label(self, cat, label):
        self.cat = f"{cat[:5]:5}"
        self.label = f"{label[:15]:15}"
        self.name = self.cat + self.label

    # def __deepcopy__(self, memo):
    #    content = bytes(self.write())
    #    pattern = Pattern(None, content)
    #    pattern.unmodified()
    #    return pattern

    def write(self):
        content = pack(
            "20sBBBB",
            bytes(f"{self.name:20}", "utf-8"),
            self.num_tracks,
            self.mixer_map,
            self.sysex_setup,
            self.reserved1,
        )
        for t in range(self.num_tracks):
            content += self.tracks[t].write()
            self.tracks[t].unmodified()
        return content

    def cat_label(self):
        m = self.modified_symbol()
        return f"{self.cat:5} {self.label:15}"

    def dump(self):
        r = f"{self}"
        if self.tracks:
            for nt, tr in enumerate(self.tracks):
                r += f"\n T{nt+1}: {tr}"
        return r

    def __repr__(self):
        m = self.modified_symbol()
        r = (
            f'<{self.__class__.__name__}: "{self.cat_label()}">'
            f"{m}"
            # f' Mixer Map: {self.mixer_map:3}'
            # f' SysEx Config: {self.sysex_setup:3}'
            # f' Tracks: {self.num_tracks}'
        )
        return r


class PatternBank(Observable):
    def __init__(self, parent, filename):
        super().__init__(parent)
        self.filename = filename
        self.fullname = os.path.join(self.parent.path, self.filename)
        logger.debug(f"Read PatternBank {self.fullname}")
        content = open(self.fullname, "rb").read()
        (self.header, self.name, self.num_patterns, self.pattern_size) = unpack(
            "10s20sHH", content[: 10 + 24]
        )
        if self.header != b"MBSEQV4_B\x00":
            raise SeqV4PError(f"Corrupt header {self.header} in {self.fullname}")
        if self.pattern_size != 6008:
            raise SeqV4PError(f"Pattern reserved size {self.pattern_size} not 6008b")
        # if self.name[19] != :
        #    raise SeqV4PError(f'Pattern name wrong size {len(self.name)}')
        self.name = self.name.decode("utf-8")
        if len(self.name) != 20:
            raise SeqV4PError(f'Pattern name "{self.name}" wrong size {len(self.name)}')
        self.patterns = []
        for p in range(self.num_patterns):
            pattern = Pattern(self, content[10 + 24 + p * self.pattern_size :])
            self.patterns.append(pattern)
        logger.info(f"{self}")

    def write(self):
        # if not self.has_modifications():
        #    return
        logger.info(f"Write PatternBank {self.fullname}")
        content = pack(
            "10s20sHH",
            self.header,
            bytes(f"{self.name:20}", "utf-8"),
            self.num_patterns,
            self.pattern_size,
        )
        for p in self.patterns:
            pattern_content = p.write()
            content += pattern_content
            nfill = self.pattern_size - len(pattern_content)
            content += bytes(nfill)
            # print(len(pattern_content), nfill)
        with open(self.fullname, "wb") as f:
            f.write(content)
        for p in self.patterns:
            p.unmodified()
        logger.info(f"Wrote PatternBank {self}")

    def debug(self):
        buf = f"{self}"
        buf += "".join([p.dump() for p in self.patterns])
        return buf

    def __repr__(self):
        m = self.modified_symbol()
        return (
            f'<{self.__class__.__name__}: "{self.name:20}">'
            f"{m}"
            # f' Patterns: {self.num_patterns:2}'
            # f' (Reserved: {self.pattern_size:4}b)'
            # f' File: {self.filename}'
            # Bank {self.nbank} '
        )
