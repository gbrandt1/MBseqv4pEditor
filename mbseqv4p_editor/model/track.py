import logging
import os
from pprint import pprint, pformat
from struct import pack, unpack

from ..helpers import *
from ..layers import *
from ..observer import Observable
from ..track_cc import *

logger = logging.getLogger(f"{__name__:{LOGW_NAME}}")


class Clkdiv:
    def __init__(self):
        self.value = 0
        self.triplets = False
        self.manual = False
        self.sync_to_measure = True


class GrooveStyle:
    def __init__(self):
        self.style = 0
        self.sync_to_track = True


class FxMidiMode:
    def __init__(self):
        self.beh = 0
        self.fwd_non_notes = 0


class Track(Observable):
    """Class to contain SEQV4P Track data with different aspects
    - track data unpacked from binary file
    - track data read from v4t ascii file
    - derived cc variables and bit flags converted to strings
    """

    def __init__(self, parent, content):  # =None, pattern_name=None):
        super().__init__(parent)
        self.pattern_name = parent.name
        # self.track_configuration_index = 0
        # self.reset()
        if not content:
            self.configure()
            return
        (
            self.name,
            self.num_p_instruments,
            self.num_t_instruments,
            self.num_p_layers,
            self.num_t_layers,
            self.p_layer_size,
            self.t_layer_size,
            self.cc,
        ) = unpack("80sBBBBHH128s", content[:216])
        self.name = self.name.decode("utf-8")
        self.event_mode = EVENT_MODES[self.cc[0x42]]
        # self.set_sizes_names()
        self.set_attr_from_cc()
        (self.par,) = unpack(
            f"{self.p_tot_size}s", content[216 : 216 + self.p_tot_size]
        )
        (self.trg,) = unpack(
            f"{self.t_tot_size}s",
            content[216 + self.p_tot_size : 216 + self.p_tot_size + self.t_tot_size],
        )
        # make content assignable
        self.cc = bytearray(self.cc)
        self.par = bytearray(self.par)
        self.trg = bytearray(self.trg)

    def configure(self, tlc="Note  (16*64)/(8*64) 1"):
        # in original call partitioning / trackinit
        # self.track_configuration_index = tcidx
        #  0     1           2          3           4          5
        #  mode, par_layers, par_steps, trg_layers, trg_steps, instruments
        # if tlc == :
        #     logger.info(f'Configuring track to default')
        #     self.num_p_instruments = 1
        #     self.num_t_instruments = 1
        #     self.num_p_layers = 16
        #     self.num_t_layers = 8
        #     self.p_layer_size = 64
        #     self.t_layer_size = 256//8
        # else:
        #     tc = list(TRACK_LAYER_CONFIG.items())[tcidx][1]
        tc = TRACK_LAYER_CONFIG[tlc]
        self.layer_config = tlc
        self.num_p_instruments = tc[5]
        self.num_t_instruments = tc[5]
        self.num_p_layers = tc[1]
        self.num_t_layers = tc[3]
        self.p_layer_size = tc[2]
        self.t_layer_size = tc[4] >> 3
        # self.midi_event_mode = EVENT_MODES.index(tc[0])
        self.event_mode = tc[0]  # tlc[0:6].strip() #EVENT_MODES[tc[0]]

        # logger.info(f'configure {tlc}: {tc} {self.event_mode}')

        # self.num_par_steps = tc[2]
        # self.num_trg_steps = tc[4]
        # self.cc[track_properties.midi_event_mode]
        # self.recalc_sizes()
        self.clear()
        # dump(self)

    def clear(self):
        """Fill all values with defaults.
        Don't reconfigure.
        """
        self.cc = bytearray(128)
        self.par = bytearray(PAR_MAX_BYTES)
        self.trg = bytearray(TRG_MAX_BYTES)

        self.name = " " * 80
        if self.event_mode == "Drum":
            self.name = "BD   SD   CH   PH   OH   MA   CP   CY   LT   MT   HT   RS   CB  Smp1 Smp2 Smp3 "

        # logger.info(f'clear {self}')

        # Copy default preset - need to handle different event mode cases
        for attr, idx, default, name in TRACK_PROPERTIES:
            if 0x00 <= idx < 0x80:
                self.cc[idx] = default
        self.set_attr_from_cc()
        self.cc[0x42] = self.midi_event_mode = EVENT_MODES.index(self.event_mode)

        self.par_layer_types = self.get_par_layer_types()

        for pi in range(self.num_p_instruments):
            for pl in range(self.num_p_layers):
                pldef = self.par_layer_types[pl]["default"]
                for ps in range(self.num_par_steps):
                    self.par_set(ps, pl, pi, pldef)

        # print(self.info())

        # self.trg = bytearray
        for ti in range(self.num_t_instruments):
            # for tl in range(self.num_t_layers):
            for ts in range(0, self.num_trg_steps, 4):
                # print(ti, ts)
                self.trg_set(ts, 0, ti, 1)
        # print(self.trg)
        # logger.info(f'clear {self}')

    def set_attr_from_cc(self):
        """Interpret unpacked CC and name data
        (original code, mostly in seq_cc)
        Convert to string where possible.
        Store in subclasses where done in original code.
        Trailing underscore means converted version
        """

        self.p_layer_steps = self.p_layer_size
        self.t_layer_steps = self.t_layer_size * 8
        self.p_inst_size = self.num_p_layers * self.p_layer_size
        self.t_inst_size = self.num_t_layers * self.t_layer_size
        self.p_tot_size = self.num_p_instruments * self.p_inst_size
        self.t_tot_size = self.num_t_instruments * self.t_inst_size
        self.size = 216 + self.p_tot_size + self.t_tot_size
        # alternative names
        self.num_par_steps = self.p_layer_steps
        self.num_trg_steps = self.t_layer_steps

        # self.event_mode = EVENT_MODES[self.cc[0x42]]

        self.layer_config = self.layer_config_repr()

        self.cat = self.name[:5]
        self.label = self.name[5:20]
        self.drumlabels = [self.name[i : i + 5] for i in range(0, 80, 5)]

        for attr, idx, default, name in TRACK_PROPERTIES:
            if 0x00 <= idx < 0x80:
                setattr(self, attr, self.cc[idx])

        # self.event_mode = EVENT_MODES[self.midi_event_mode]
        self.playmode = PLAY_MODES[self.mode]
        self.dir_mode = DIR_MODES[self.direction]
        self.midi_port_ = MIDI_OUT_PORT[self.midi_port]
        self.fx_midi_port_ = MIDI_OUT_PORT[self.fx_midi_port]

        self.fx_midi_mode_ = FxMidiMode()
        self.fx_midi_mode_.beh = self.fx_midi_mode
        self.fx_midi_mode_.fwd_non_notes = True  # FxMIDI_FwdNonNotes

        self.clkdiv_ = Clkdiv()
        self.clkdiv_.triplets = 0  # Triplets
        self.clkdiv_.manual = 0  # ManualClock
        self.clkdiv_.sync_to_measure = 0  # SynchToMeasure

        self.groove_style_ = GrooveStyle()
        self.groove_style_.style = self.groove_style
        self.groove_style_.sync_to_track = True  # GrooveSyncToTrack

        # EchoDisabled
        # self.echo_repeats

    def set_cc_from_attr(self):
        """Convert CC back into CC attributes and array."""

        # self.cat = self.name[:5]
        # self.label = self.name[5:20]
        # self.drumlabels = [self.name[i:i+5] for i in range(0, 80, 5)]

        if self.event_mode == "Drum":
            self.name = "".join(self.drumlabels)
        else:
            self.name = f"{self.cat:5}{self.label:15}"

        self.midi_event_mode = EVENT_MODES.index(self.event_mode)
        self.mode = PLAY_MODES.index(self.playmode)
        self.direction = DIR_MODES.index(self.dir_mode)
        self.midi_port = MIDI_OUT_PORT[self.midi_port_]
        self.fx_midi_port = MIDI_OUT_PORT[self.fx_midi_port_]

        self.fx_midi_mode = self.fx_midi_mode_.beh

        self.groove_style = self.groove_style_.style

        for attr, idx, default, name in TRACK_PROPERTIES:
            if 0x00 <= idx < 0x80:
                val = getattr(self, attr)
                print(idx, attr, val)
                self.cc[idx] = val

    def write(self):
        """Serialize to content buffer."""
        self.set_cc_from_attr()
        content = pack(
            "80sBBBBHH128s",
            bytes(f"{self.name:80}", "utf-8"),
            self.num_p_instruments,
            self.num_t_instruments,
            self.num_p_layers,
            self.num_t_layers,
            self.p_layer_size,
            self.t_layer_size,
            self.cc,
        )
        content += pack(f"{self.p_tot_size}s", self.par)
        content += pack(f"{self.t_tot_size}s", self.trg)
        return content

    def par_set(self, step, par_layer, par_instrument, value):
        """Set parameter value."""
        # modulo of num_p_steps to allow mirroring of parameter layer in drum mode
        step %= self.num_par_steps
        step_ix = (
            (par_instrument * self.num_p_layers * self.num_par_steps)
            + (par_layer * self.num_par_steps)
            + step
        )
        # logger.info(f'par_set {step_ix} "{value}"')
        self.par[step_ix] = int(value)

    def par_get(self, step, par_layer, par_instrument):
        """Get parameter value."""
        # modulo of num_p_steps to allow mirroring of parameter layer in drum mode
        step %= self.num_par_steps
        step_ix = (
            (par_instrument * self.num_p_layers * self.num_par_steps)
            + (par_layer * self.num_par_steps)
            + step
        )
        value = int(self.par[step_ix])
        return value

    def trg_set(self, step, trg_layer, trg_instrument, value):
        """Set trigger value."""
        step_ix = (
            (trg_instrument * self.num_t_layers * self.num_trg_steps // 8)
            + (trg_layer * self.num_trg_steps // 8)
            + step // 8
        )
        if step_ix >= 256:
            logger.info(
                #    f'{self.num_t_layers} {self.num_trg_steps} '
                f"trg_set {step:3} {trg_layer:2} {trg_instrument:2} {value:3}"
                f" --> {step_ix}"  # ' {step_mask:>08b}'
            )
        step_mask = 1 << (step & 0x7)
        if value:
            self.trg[step_ix] |= step_mask
        else:
            self.trg[step_ix] &= ~step_mask

    def trg_get(self, step, trg_layer, trg_instrument):
        """Get trigger value."""
        # step %= self.num_par_steps
        step_ix = (
            (trg_instrument * self.num_t_layers * self.num_trg_steps // 8)
            + (trg_layer * self.num_trg_steps // 8)
            + step // 8
        )
        step_mask = 1 << (step & 0x7)
        # return Bool and deal with symbols in view
        # '\u25CB'
        # value = '\u25CF' if self.trg[step_ix] & step_mask else '\u00B7'
        value = 1 if (self.trg[step_ix] & step_mask) else 0
        return value

    def get_par_layer_types(self):
        """Return parameter layer dictionary."""
        if self.event_mode == "Drum":
            par_layer_types = [
                self.par_asg_drum_layer_a,
                self.par_asg_drum_layer_b,
                self.par_asg_drum_layer_c,
                self.par_asg_drum_layer_d,
            ]
        else:
            par_layer_types = [
                getattr(self, f"lay_const_a{l+1}") for l in range(self.num_p_layers)
            ]
        par_layer_types = [PAR_TYPES[l] for l in par_layer_types]
        logger.debug(f"get_par_layer_types {pformat(par_layer_types)}")
        return par_layer_types

    def get_trg_layer_type(self, tl):
        layer = getattr(self, f"lay_const_a{tl+1}")
        return layer

    def get_trg_layer_asgn(self, trg_layer):
        """Find trigger layer name"""
        for asg in TRG_NAMES:
            if getattr(self, asg) == trg_layer + 1:
                return TRG_NAMES[asg]
        return "-----"

    def get_trg_layer_names(self):
        """Return tuple of trigger layer names"""
        trg_layer_txt = ["------"] * self.num_t_layers
        for tl in range(self.num_t_layers):
            layer = self.get_trg_layer_type(tl)
            # getattr(self, f'lay_const_a{tl+1}')
            trg_layer_txt[tl] = self.get_trg_layer_asgn(tl)  # TRG_NAMES[layer]
        return trg_layer_txt

    def info(self):
        """Nicer presentation"""
        m = self.modified_symbol()
        return (
            # size {self.size}\n'
            f'{m}Track "{self.name}" in "{self.pattern_name}"'
            f" Type: {self.event_mode:5}"
            f" P:{self.num_p_layers:>2}/T:{self.num_t_layers:>2}"
            f" I:{self.num_p_instruments:>2}"
            f" Steps P:{self.p_layer_steps:>3}/T:{self.t_layer_steps:>3}"
            f" Length:{self.length+1:>3}"
            f" Port:{self.midi_port:>8} Chn.:{self.midi_channel:>2}"
        )

    def bytes2hexstr(self, prefix, ba):
        buf = ""
        nrows = len(ba) // 16
        for row in range(nrows):
            br = bytes(ba[row * 16 : (row + 1) * 16]).hex(" ")
            br = (" " + br).replace(" ", " 0x")
            buf += f"{prefix} 0x{row*16:03x}" + br + "\n"
        return buf

    def lay_const2hexstr(self, abc):
        # print(abc)
        buf = ""
        for c in range(16):
            attr = getattr(self, f"lay_const_{abc}{c+1}")
            buf += f" 0x{attr:02x}"
        return buf

    def write_special_cc(self, cc_name):
        """Dump special CC cases"""
        attr = {
            "PatternName": f"'{self.pattern_name:20}'",
            "Name": f"'{self.name:80}'",
            "Par": self.bytes2hexstr(cc_name, self.par),
            "Trg": self.bytes2hexstr(cc_name, self.trg),
            "ConstArrayA": f'{self.lay_const2hexstr("a")}',
            "ConstArrayB": f'{self.lay_const2hexstr("b")}',
            "ConstArrayC": f'{self.lay_const2hexstr("c")}',
            "Triplets": f"{self.clkdiv.triplets}",
            "ManualClock": f"{self.clkdiv.manual}",
            "SynchToMeasure": f"{self.clkdiv.sync_to_measure}",
            "GrooveStyle": f"{self.groove_style.style}",
            "GrooveSyncToTrack": f"{self.groove_style.sync_to_track}",
            "FxMIDI_Mode": f"{self.fx_midi_mode.beh}",
            "FxMIDI_FwdNonNotes": f"{self.fx_midi_mode.fwd_non_notes}",
            "EchoDisabled": f"{self.echo_repeats & 0x40}",
        }.get(cc_name)
        if not attr:
            return None
        if cc_name in ("Par", "Trg"):
            return attr
        else:
            return f"{cc_name} {attr}\n"

    def write_helper(self):
        """corresponds to write helper in original code
        create text buffer to write data into file or send to debug terminal
        """
        buf = ""
        for cc_name in V4TFILE.splitlines():
            for tp in TRACK_PROPERTIES:
                # if 0 <= tp[1] < 0x80 and
                if cc_name == tp[2]:
                    break
            sbuf = self.write_special_cc(cc_name)
            if not sbuf:
                try:
                    attr = getattr(self, tp[0])
                    buf += f"{cc_name} {attr}\n"
                except AttributeError:
                    print(f"Not handled: {cc_name}")
            else:
                buf += sbuf
        return buf

    def __repr__(self):
        m = self.modified_symbol()
        return f"{m}<Track: {self.layer_config_repr()} {self.name}>"

    def layer_config_repr(self):
        """Representation in layer config syntax"""
        # m = '\u25CF' if self.modified else ' '  # \u00B7'
        # if self.event_mode == 'Drum':
        return (
            f"{self.event_mode:6}"
            f"({self.num_p_layers}*{self.p_layer_steps})/"
            f"({self.num_t_layers}*{self.t_layer_steps})"
            f" {self.num_p_instruments}"
        )
        # else:
        #    return (
        #        f'{self.event_mode:6}'
        #        f' ({self.p_layer_steps}*{self.num_p_layers})'
        #        f'({self.num_t_layers})'
        #    )


if __name__ == "__main__":

    class Dummy:
        name = " " * 20

    t = Track(Dummy(), None)

    # content = t.write()
    # print(t)
    buf = dump(t)
    print(buf)
