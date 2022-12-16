import re


from ..helpers import *
from ..observer import Observable

logger = logging.getLogger(f"{__name__:{LOGW_NAME}}")


class SeqConfig(Observable):
    """Config Files
    one class to parse them all - handle special cases in here
    """

    def __init__(self, parent, name):
        super().__init__(parent)
        self.name = name
        self.set_path(parent.path)
        logger.debug(f"Read config file {self}")
        self.data = []
        with open(self.fullpath) as f:
            fc = f.readlines()
            for l in fc:
                l.strip(" \n\t")
                if not l or l.isspace() or l.startswith("//") or l.startswith("#"):
                    continue
                ls = self.parse_line(l)
                self.data.append(ls)
        if self.basename not in (
            "TRKLABEL.V4P",
            "TRKCATS.V4P",
        ):
            d = OrderedDict()
            for x in self.data:
                d[x[0]] = x[1:]
            self.data = d
        # logger.info(f'{self}')

    def set_path(self, path):
        self.fullpath = os.path.join(path, self.name)
        self.basename = os.path.basename(self.name)
        # logger.info(f'set_path {self.basename} {self.fullpath}')

    def parse_line(self, l):
        if "TRKLABEL" in self.name or "TRKCATS" in self.name:
            ls = l.strip()
        else:
            ls = re.findall("\[[^\]]*\]|\([^\)]*\)|'[^']*'|\S+", l)
            ls = [x[1:] if x.startswith(",") else x for x in ls]
            ls = [x for x in ls if not x.startswith("(")]
            ls = [x[1:-1] if x.startswith("'") else x for x in ls]
            lss = []
            for lsss in ls:
                lss += lsss.split(",")
            ls = lss
            if ls[0] in (
                "Par",
                "Trg",
            ):
                ls[0] = ls[0] + " " + ls[1]
                ls[1] = " ".join([x[2:] for x in ls[2:]])
                # ls[1] = bytes.fromhex(ls[1])
                ls = ls[0:2]
            if "ConstArray" in ls[0]:
                ls[1] = " ".join([x[2:] for x in ls[2:]])
                ls = ls[0:2]
            if ls[0] in (
                "TpdLogoLine",
                "DrumCC",
                "MIDI_RouterNode",
                "BLM_Fader",
                "MIDI_OUT_MClock_Delay",
                "LivePattern",
                "LastPattern",
                "BPMx10_P",
            ):
                ls = [ls[0] + " " + ls[1]] + ls[2:]
        # print(ls)
        return ls

    def write(self):
        logger.info(f"Write {self} to {self.fullpath}")
        with open(self.fullpath, "w") as f:
            if isinstance(self.data, list):
                for l in self.data:
                    print(l, file=f)
            elif isinstance(self.data, OrderedDict):
                for k, v in self.data.items():
                    print(k, *v, file=f)
        dump(self)

    def __repr__(self):
        m = self.modified_symbol()
        return f'<{self.__class__.__name__}: "{self.name}">{m}'
