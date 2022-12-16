import logging
import os
import sys
from collections import OrderedDict
from copy import deepcopy
from itertools import cycle

from .helpers import *
from .model.sdcard import SDCardContent
from .observer import Observable
from .model.track import Track

logger = logging.getLogger(f"{__name__:{LOGW_NAME}}")


class PatternBuffer(list):
    def __repr__(self):
        return pformat(self)


class SongBuffer(list):
    def __repr__(self):
        return pformat(self)


class PatternSelection(OrderedDict):
    def __repr__(self):
        return pformat(self)


class Controller(Observable):
    """View independent controller
    - Only knows about model and view interface
    - Keeps headless versions of commands
    """

    def __init__(self, path=None):
        super().__init__()
        logger.debug(f"Controller: Starting from {path}")
        self.path = path

        # active objects
        self.sdcard = None
        self.session = None
        self.bank = None
        self.pattern = None
        self.track = None
        self.tracks = [None] * 16

        # phrase: last npn per group
        self.phrase = [None] * 4
        # group: last bank
        self.group = None

        self.song = None
        self.song_bank = None
        self.mixer_map = None
        self.mixer_map_bank = None

        self.pattern_selection = PatternSelection()
        self.track_selection = []
        self.track_buffer = []
        self.pattern_buffer = PatternBuffer()
        self.song_buffer = SongBuffer()

    def notify(self, child):
        # logger.info(f'controlller notified by {child}')
        pass

    def do(self, cmd, *args, **kwargs):
        logger.info(f'Command do "{cmd} ({args}, {kwargs})"')
        #  try:
        attr = getattr(self, cmd)
        # logger.info(f'{attr} {}')
        attr(*args, **kwargs)
        #  except Exception as e:
        #     logger.warning('Command failed! {e}')

    #  General Methods
    def show_status(self, arg=None):
        """Show status."""
        if not self.sdcard:
            logger.warning("No SDCard open.")
            return
        print(
            f"{self.sdcard}\n",
            f"{self.session}\n",
            f"{self.bank}\n",
            f"{self.pattern}\n",
            f"Pattern Selection: {self.pattern_selection}\n",
            f"{self.track}\n",
            f"Phrase: {self.phrase}\n",
            f"Tracks: {self.tracks}\n",
            f"{self.song_bank}\n",
            f"{self.song}\n",
            f"{self.mixer_map_bank}\n",
            f"{self.mixer_map}\n",
        )

    #  SDCard methods
    def open_sdcard(self, arg=None):
        """Open SD Card."""
        if self.sdcard and self.sdcard.has_modifications():
            logger.warning(f"SDCard {self.sdcard} has modifications!")
            return
        if not arg:
            print(self.open_sdcard.__doc__)
            return
        self.path = os.path.normpath(arg)
        logger.info(f"Opening sdcard at {self.path}.")
        self.sdcard = SDCardContent(self, self.path)
        self.set_session()

    def save_sdcard(self, arg=None):
        """Save SD Card."""
        if not self.sdcard:
            logger.warning("No SDCard open.")
            return
        logger.info(f"Save {self.sdcard}")
        self.sdcard.write()

    def save_as_sdcard(self, path2):
        """Save SD Card at new path."""
        if not self.sdcard:
            logger.warning("No SDCard open.")
            return
        logger.info(f"Save {self.sdcard} As {path2}")
        # self.copytree(self.sdcard.path, path2)
        self.sdcard.set_path(path2)
        # self.sdcard.write()

    #  Session methods
    def set_session(self, name=None):
        """Set active session."""
        s = self.sdcard.sessions
        logger.debug(f"Available sessions {list(s.keys())}")
        if not name:
            name = self.sdcard.last_session_name
            logger.info(f"Set last session {name}")
        else:
            logger.info(f"Set session {name}")
        self.session = self.sdcard.sessions[name]
        # self.phrase = ['1:A1', '2:A1', '3:A1', '4:A1', ]
        for npn in ("1:A1", "2:A1", "3:A1", "4:A1"):
            print(npn)
            self.set_pattern(npn)
        self.set_pattern_selection(["1:A1"])
        self.set_song(1)
        self.set_mixer_map(1)

    def save_session(self, arg=None):
        if not self.session:
            logger.warn("No active session.")
            return
        self.session.write()
        self.session.unmodified()
        # self.sdcard.has_modifications()
        self.show_status()

    def save_session_as(self, new_path):
        if not self.session:
            logger.warn("No active session.")
            return
        self.session.set_path(new_path)
        # self.session.write(force=True)
        # self.session.unmodified()
        # self.sdcard.has_modifications()
        self.show_status()

    #  PatternBank methods
    def set_bank(self, nb):
        """Set active pattern bank."""
        if not self.session:
            logger.warn("No active session.")
            return
        self.bank = self.session.banks[nb - 1]
        self.group = nb
        logger.info(f"Set active pattern bank {nb}: {self.bank}")

    def save_pattern_banks(self, arg=None):
        """Save all pattern banks."""
        logger.debug("save_pattern_banks")
        # print(Observable._modified_objects)
        if not self.session:
            logger.warn("No active session.")
            return
        for bank in self.session.banks:
            if bank.has_modifications():
                logger.info(f"Writing {bank}")
                bank.write()
                bank.unmodified()
        self.show_status()
        #  for np in range(MAX_NUM_PATTERN):
        #  self.session.banks[nb].patterns[np].notify()

    #  Phrase methods

    def set_phrase(self, npn):
        """Phrase keeps active pattern/track per group (bank)."""
        logger.info(f"set_phrase {npn} {npn[0]}")
        nb, np = npn2idx(npn)
        self.phrase[nb] = npn
        self.group = nb
        pattern = self.session.get_pattern(npn)
        if not pattern:
            return
        for nt, trk in enumerate(pattern.tracks):
            self.tracks[4 * nb + nt] = trk

    #  Pattern methods

    def set_pattern(self, npn):
        """Set active pattern."""
        if not self.session:
            logger.warn("No active session.")
            return
        pattern = self.session.get_pattern(npn)
        self.pattern = pattern
        logger.info(f"Set active pattern {npn}: {self.pattern}")
        nb, np = npn2idx(npn)
        self.set_bank(nb)
        self.set_phrase(npn)
        self.set_track()

    def set_pattern_selection(self, selection):
        """Set pattern selection
        Format: list of NPNs
        """
        if not selection:
            logger.warning("set_pattern_selection: No selection.")
            return
        if isinstance(selection, str):
            # DANGEROUS & EVIL !!!
            selection = eval(selection)
        if not isinstance(selection, list):
            logger.error(f"set_pattern_selection: Selection is not list: {selection}")
        self.pattern_selection = selection
        #  for npn in selection:
        #     self.pattern_selection[npn] = selection[npn]
        logger.debug(f"set_pattern_selection: Set selection: {self.pattern_selection}")

        #  set first pattern, track
        npn = self.pattern_selection[0]
        logger.debug(f"Set first {npn}")
        self.set_pattern(npn)

    def select_all(self, arg):
        pass

    #  Track Methods
    def set_track(self, nt=0):
        """Set active track from tracks array."""
        # if not self.pattern:
        #    logger.warn('set_track: No active pattern.')
        #    return
        #  self.track = self.pattern.tracks[nt]
        if self.track != self.tracks[nt]:
            self.track = self.tracks[nt]
            self.group = nt // 4
            # npn = self.pattern_selection[0]
            # nb, np = npn2idx(npn)
            # if nb != nt//4:
            logger.info(
                f"Set active track {nt} ({self.group}, {nt%4}): " f"{self.track}"
            )
            # self.show_status()

    def copy_track(self, arg=None):
        """Copy selected track(s) to buffer"""
        if not arg:
            logger.warn("copy_track: Nothing selected.")
            return
        self.track_selection = arg
        logger.info(f"copy_track: {self.track_selection}")
        self.track_buffer = []
        for nt in self.track_selection:
            self.track_buffer.append(self.tracks[nt])
        logger.info(
            f"Copied {self.track_selection} to buffer:\n" f" {self.track_buffer}"
        )

    def paste_track(self, arg=None):
        """Paste pattern buffer to selection."""
        if not arg:
            logger.warn("paste_track: Nothing selected.")
            return
        self.track_selection = arg
        if not self.track_buffer:
            logger.info("Nothing to paste.")
            return
        logger.info(
            f"paste_track: Pasting {self.track_buffer}"
            f" to {arg}."  # {self.pattern_selection}.'
        )
        if len(self.track_selection) <= len(self.track_buffer):
            # Buffer larger or equal selection: paste once
            nt = self.track_selection[0]
            logger.info(f"paste_track: Paste block once to {nt}.")
            for track in self.track_buffer:
                self._paste_one_track(nt, track)
                nt += 1
                if nt == 16:
                    break
        else:
            # Selection larger than buffer: paste repeatedly
            logger.info("paste_track: Fill block.")
            cps = cycle(self.track_buffer)
            for nt in self.track_selection:
                track = next(cps)
                self._paste_one_track(nt, track)
                # self.tracks[nt] = track

    def _paste_one_track(self, nt, track):
        g = nt // 4
        npn = self.phrase[g]
        pattern = self.session.get_pattern(npn)
        new_track = Track(pattern, track.write())
        pattern.tracks[nt % 4] = new_track
        self.tracks[nt] = new_track
        self.track = track
        new_track.modified()
        # dump(new_track)
        logger.info(f"_paste_one_track to {nt} {new_track} {npn} {pattern}")

    #  Song Methods
    def set_song(self, nsong):
        """Set active song."""
        if not self.session:
            logger.warn("set_song: No active session.")
            return
        # if not self.session.song_bank:
        #    logger.warn('set_song: No active song bank.')
        #    return
        self.song_bank = self.session.song_bank
        nsong = int(nsong)
        if 0 < nsong < MAX_NUM_SONGS:
            self.song = self.session.song_bank[nsong - 1]
            logger.debug(f"Set active song {nsong}: {self.song}")
        else:
            logger.error("Wrong song number.")
        # return self.song

    def clear_song(self, nsong):
        """Clear song."""
        if not self.session:
            logger.warn("set_song: No active session.")
            return
        song = self.session.song_bank[nsong - 1]
        song.clear()
        song.modified()

    #  Mixer Map Methods
    def set_mixer_map(self, nmap):
        """Set active mixer map."""
        if not self.session.mixer_map_bank:
            logger.warn("No mixer map bank.")
            return
        self.mixer_map_bank = self.session.mixer_map_bank
        self.mixer_map = self.session.mixer_map_bank[nmap]
        logger.debug(f"Set active mixer map {nmap}: {self.mixer_map}")

    #  SysEx Setup Methods
    def set_sysex_setup(self, sysx):
        """set active mixer map."""
        self.sysx = sysx

    def copy_pattern(self, arg=None):
        """Copy selected pattern(s) to buffer"""
        logger.debug("copy_pattern")
        self.pattern_buffer = []
        if not self.pattern_selection:
            logger.warn("Nothing selected.")
            return
        for npn in self.pattern_selection:
            # npn = self.sel['npn']
            p = self.session.get_pattern(npn)
            self.pattern_buffer.append(p)
        logger.info(
            f"Copied {self.pattern_selection} to buffer:\n" f" {self.pattern_buffer}"
        )

    def paste_pattern(self, arg=None):
        """Paste pattern buffer to selection."""
        logger.debug("paste_pattern")
        if not self.pattern_buffer:
            logger.info("Nothing to paste.")
            return
        logger.info(
            f"Pasting pattern buffer {self.pattern_buffer}"
            f" to {self.pattern_selection}."
        )
        if len(self.pattern_selection) <= len(self.pattern_buffer):
            #  buffer larger or equal selection: paste once
            logger.info("Paste block once.")
            npn = self.pattern_selection[0]
            for pbuf in self.pattern_buffer:
                self._paste_one_pattern(npn, pbuf)
                nb, np = npn2idx(npn)
                npn = idx2npn(nb, np + 1)
        else:
            #  selection larger than buffer: paste repeatedly
            logger.info("Fill block.")
            cps = cycle(self.pattern_buffer)
            for npn in self.pattern_selection:
                # npn = sel['npn']
                pbuf = next(cps)
                self._paste_one_pattern(npn, pbuf)

    def _paste_one_pattern(self, npn, pbuf):
        nb, np = npn2idx(npn)
        p = self.session.banks[nb].patterns[np]
        p = deepcopy(pbuf)
        p.parent = self.session.banks[nb]
        p.modified()
        self.session.banks[nb].patterns[np] = p
        logger.debug(f'Pasted buffer "{pbuf.name}" to {npn}')

    def clear_pattern(self, arg=None):
        """Reset selection with default pattern."""
        for npn in self.pattern_selection:
            # npn = sel['npn']
            nb, np = npn2idx(npn)
            pattern = self.session.get_pattern(npn)
            pattern.clear()
            pattern.modified()
            logger.info(f"clear_pattern {npn}")

    def dump_selection(self, arg=None):
        """Dump selected patterns."""
        logger.info("dump_selection: {self.pattern_selection}")
        for npn in self.pattern_selection:
            logger.info(f"dump_pattern {npn}")
            nb, np = npn2idx(npn)
            buf = dump(self.session.banks[nb].patterns[np])
            print(buf)


if __name__ == "__main__":
    homedir = os.getcwd()
    logger.info(f"Starting from {homedir}")
    if len(sys.argv) < 2:
        print("\nSyntax:\n\tpython3 controller.py relative/path/to/SD/card\n")
        sys.exit()

    ctrl = Controller(homedir + "/" + sys.argv[1])

    ctrl.open_sdcard(homedir + "/" + sys.argv[1])
    ctrl.set_session()
    ctrl.show_status()
