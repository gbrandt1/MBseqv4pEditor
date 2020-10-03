

from helpers import *
from observer import Observable

from .configfile import SeqConfig
from .pattern import Pattern, PatternBank
from .mixer_map import MixerMapBank
from .song import SongBank
from .track import Track

logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


class Session(Observable):

    def __init__(self, parent, name):
        super().__init__(parent)
        self.contents = []
        self.name = name
        self.set_path(parent.path)
        logger.debug(f'Read Session at {self.path}')
        self.config = SeqConfig(self, 'MBSEQ_C.V4')
        self.banks = []
        for i in range(MAX_NUM_BANKS):
            try:
                bank = PatternBank(self, 'MBSEQ_B'+str(i+1)+'.V4')
            except SeqV4PError as err:
                logger.error(f'{err}')
                raise
            self.banks.append(bank)
        self.mixer_map_bank = MixerMapBank(self, 'MBSEQ_M.V4')
        self.song_bank = SongBank(self, 'MBSEQ_S.V4')
        self.grooves = SeqConfig(self, 'MBSEQ_G.V4')
        self.bookmarks = SeqConfig(self, 'MBSEQ_BM.V4')
        logger.info(f'{self}')

        self.contents = [
            self.config,
            self.banks[0],
            self.banks[1],
            self.banks[2],
            self.banks[3],
            self.mixer_map_bank,
            self.song_bank,
            self.grooves,
            self.bookmarks,
        ]

    def set_path(self, path):
        self.path = os.path.join(
            os.path.join(self.parent.path, 'SESSIONS'),
            self.name
        )
        for content in self.contents:
            content.set_path(path)
        logger.info(f'set_path {self} {self.path}')

    def write(self):
        logger.info(f'Writing session to {self.path}')
        for content in self.contents:
            if content.has_modifications():
                content.write()
                content.unmodified()
        logger.info(f'Wrote session {self.name}')

    def get_pattern(self, npn):
        nb, np = npn2idx(npn)
        if not(0 <= nb < MAX_NUM_BANKS):
            logger.error(f'get_pattern: Wrong NPN {npn} --> no bank {nb}')
            return None
        if not(0 <= np < MAX_NUM_PATTERN):
            logger.error(f'get_pattern: Wrong NPN {npn} --> no pattern {np}')
            return None
        bank = self.banks[nb]
        if not bank:
            logger.error(f'get_pattern: No pattern {npn}')
            dump(self)
            return None
        pattern = bank.patterns[np]
        if not pattern:
            logger.error(f'get_pattern: No pattern {npn}')
            dump(self)
            return None
        return pattern

    def set_pattern(self, npn, pattern):
        nb, np = npn2idx(npn)
        self.banks[nb].patterns[np] = pattern

    def get_track(self, npn, ntrack):
        pattern = self.get_pattern(npn)
        #td = p.tracks[ntrack].notify()
        if not pattern:
            return None
        return pattern.tracks[ntrack]

    def set_track(self, npn, ntrack, track):
        nb, np = npn2idx(npn)
        self.banks[nb].patterns[np].tracks[ntrack] = track

    def copy_pattern(self, npn_from, npn_to):
        p = self.get_pattern(npn_from).copy()
        nb, np = npn2idx(npn_to)
        self.banks[nb].patterns[np] = p

    def __repr__(self):
        m = self.modified_symbol()
        return (
            f'<{self.__class__.__name__}: "{self.name}">'
            f'{m}'
        )


