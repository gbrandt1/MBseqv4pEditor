"""Data Model for a MIDIbox SEQ V4 Session SD Card

MIDIbox: http://www.ucapps.de

Original code: https://github.com/midibox/mios32/tree/master/apps/sequencers/midibox_seq_v4
"""

import glob
import logging
import os
import sys
from collections import OrderedDict
from pprint import pprint
from struct import unpack

from ..helpers import *
from ..observer import Observable

from .configfile import SeqConfig
from .session import Session

logger = logging.getLogger(f"{__name__:{LOGW_NAME}}")


class SDCardContent(Observable):
    def __init__(self, parent, path):
        super().__init__(parent)
        self.path = os.path.normpath(path)
        self.name = os.path.basename(self.path)
        logger.debug(f"Read SD Card content at: {self.path}")
        try:
            self.global_config = SeqConfig(self, "MBSEQ_GC.V4")
        except FileNotFoundError as e:
            logger.error(f"{e}")
            return
        self.sessions = {}
        spath = os.path.join(self.path, "SESSIONS")
        sessions = next(os.walk(spath))[1]
        for s in sessions:
            logger.info(f"Read session {s}")
            self.sessions[s] = Session(self, s)
        logger.debug(f"Available Sessions: {self.sessions}")
        with open(os.path.join(spath, "LAST_ONE.V4")) as ls:
            self.last_session_name = ls.readline().strip().upper()
            logger.info(f"Last Session: {self.last_session_name}")
        self.track_presets = {}
        for pfile in glob.glob(os.path.join(self.path, "PRESETS/*.v4t")):
            sc = SeqConfig(self, "PRESETS/" + os.path.basename(pfile))
            prn = os.path.basename(pfile)[:-4]
            self.track_presets[prn] = sc
            logger.debug(f"Track preset {pfile}")
        logger.debug(f"Read track presets: {list(self.track_presets.keys())}")
        self.trkdrums = SeqConfig(self, "PRESETS/TRKDRUMS.V4P")
        self.trkcat = SeqConfig(self, "PRESETS/TRKCATS.V4P")
        self.trklabel = SeqConfig(self, "PRESETS/TRKLABEL.V4P")
        logger.info(f"{self}")

    def contents(self):
        return (
            list(self.sessions.values())
            + list(self.track_presets.values())
            + [
                self.global_config,
                self.trkdrums,
                self.trkcat,
                self.trklabel,
            ]
        )

    def set_path(self, path):
        self.path = os.path.normpath(path)
        for content in self.contents():
            content.set_path(self.path)
        logger.info(f"set_path {self} {self.path}")

    def write(self):
        logger.info(f"Write SD Card content to: {self.path}")
        for content in self.contents():
            if content.has_modifications():
                content.write()
                content.unmodified()
        logger.info(f"Wrote SD Card contents")

    def __repr__(self):
        m = self.modified_symbol()
        return f'<{self.__class__.__name__}: "{self.name}">{m}'
