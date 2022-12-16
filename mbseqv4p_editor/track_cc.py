# Various track related constants copied from around the seq_v4 code

from collections import OrderedDict


# Trigger Layer Constants + Tools
# --> trg.py eventually
TRG_NAMES = {
    "asg_gate": "Gate ",  # 0
    "asg_accent": "Acc. ",  # 1
    "asg_roll": "Roll ",  # 2
    "asg_glide": "Glide",  # 3
    "asg_skip": " Skip",  # 4
    "asg_random_gate": " R.G ",  # 5
    "asg_random_value": " R.V ",  # 6
    "asg_no_fx": "NoFx ",  # 7
    "asg_roll_gate": "RollG",  # 8
}

EVENT_MODES = (
    "Note",
    "Chord",
    "CC",
    "Drum",
    "Combined",
)

PLAY_MODES = (
    "Off",
    "Normal",
    "Transpose",
    "Arpeggiator",
)

DIR_MODES = (
    "Forward",
    "Backward",
    "PingPong",
    "Pendulum",
    "Random_Dir",
    "Random_Step",
    "Random_D_S",
)

# From seq_ui_trkevent.c
TRACK_LAYER_CONFIG = OrderedDict()
# mode    par_layers  par_steps  trg_layers  trg_steps  instruments
TRACK_LAYER_CONFIG["Note  (16*64)/(8*64) 1"] = (
    "Note",
    16,
    64,
    8,
    64,
    1,
)
TRACK_LAYER_CONFIG["Note  (8*128)/(8*128) 1"] = (
    "Note",
    8,
    128,
    8,
    128,
    1,
)
TRACK_LAYER_CONFIG["Note  (4*256)/(8*256) 1"] = (
    "Note",
    4,
    256,
    8,
    256,
    1,
)
TRACK_LAYER_CONFIG["Chord (16*64)/(8*64) 1"] = (
    "Chord",
    16,
    64,
    8,
    64,
    1,
)
TRACK_LAYER_CONFIG["Chord (8*128)/(8*128) 1"] = (
    "Chord",
    8,
    128,
    8,
    128,
    1,
)
TRACK_LAYER_CONFIG["Chord (4*256)/(8*256) 1"] = (
    "Chord",
    4,
    256,
    8,
    256,
    1,
)
TRACK_LAYER_CONFIG["CC    (16*64)/(8*64) 1"] = (
    "CC",
    16,
    64,
    8,
    64,
    1,
)
TRACK_LAYER_CONFIG["CC    (8*128)/(8*128) 1"] = (
    "CC",
    8,
    128,
    8,
    128,
    1,
)
TRACK_LAYER_CONFIG["CC    (4*256)/(8*256) 1"] = (
    "CC",
    4,
    256,
    8,
    256,
    1,
)
TRACK_LAYER_CONFIG["Drum  (4*16)/(2*64) 16"] = (
    "Drum",
    4,
    16,
    2,
    64,
    16,
)
#!
TRACK_LAYER_CONFIG["Drum  (4*16)/(2*128) 8"] = (
    "Drum",
    4,
    16,
    2,
    128,
    8,
)
TRACK_LAYER_CONFIG["Drum  (4*16)/(1*256) 8"] = (
    "Drum",
    4,
    16,
    1,
    256,
    8,
)
TRACK_LAYER_CONFIG["Drum  (1*64)/(2*64) 16"] = (
    "Drum",
    1,
    64,
    2,
    64,
    16,
)
TRACK_LAYER_CONFIG["Drum  (2*32)/(1*128) 16"] = (
    "Drum",
    2,
    32,
    1,
    128,
    16,
)
TRACK_LAYER_CONFIG["Drum  (1*128)/(2*128) 8"] = (
    "Drum",
    1,
    128,
    2,
    128,
    8,
)
TRACK_LAYER_CONFIG["Drum  (2*64)/(2*128) 8"] = (
    "Drum",
    2,
    64,
    2,
    128,
    8,
)
TRACK_LAYER_CONFIG["Drum  (2*64)/(1*256) 8"] = (
    "Drum",
    2,
    64,
    1,
    256,
    8,
)
TRACK_LAYER_CONFIG["Drum  (1*64)/(1*64) 16"] = (
    "Drum",
    1,
    64,
    1,
    64,
    16,
)
TRACK_LAYER_CONFIG["Drum  (1*128)/(1*128) 8"] = (
    "Drum",
    1,
    128,
    1,
    128,
    8,
)
TRACK_LAYER_CONFIG["Drum  (1*256)/(1*256) 4"] = (
    "Drum",
    1,
    256,
    1,
    256,
    4,
)

TRACK_PROP_IDX = {
    "attr": 0,
    "index": 1,
    "name": 2,
}
# track_properties_enum = ( ATTRNAME, CCMUM, )
TRACK_PROPERTIES = (
    # Properties not in Track CC Array
    ("pattern_name", -1, "", "PatternName"),
    ("num_p_instruments", -1, 1, "ParInstruments"),
    ("num_p_layers", -1, 16, "ParLayers"),
    ("p_layer_steps", -1, 64, "ParSteps"),
    ("num_t_instruments", -1, 1, "TrgInstruments"),
    ("num_t_layers", -1, 8, "TrgLayers"),
    ("t_layer_steps", -1, 256, "TrgSteps"),
    ("name", -1, "", "Name"),
    # Track CC Array                    Index Default
    ("lay_const_a1", 0x00, 1, "ConstArrayA1"),  # LAY_CONST_A1
    ("lay_const_a2", 0x01, 3, "ConstArrayA2"),  # LAY_CONST_A2
    ("lay_const_a3", 0x02, 4, "ConstArrayA3"),  # LAY_CONST_A3
    ("lay_const_a4", 0x03, 9, "ConstArrayA4"),  # LAY_CONST_A4
    ("lay_const_a5", 0x04, 1, "ConstArrayA5"),  # LAY_CONST_A5
    ("lay_const_a6", 0x05, 1, "ConstArrayA6"),  # LAY_CONST_A6
    ("lay_const_a7", 0x06, 1, "ConstArrayA7"),  # LAY_CONST_A7
    ("lay_const_a8", 0x07, 1, "ConstArrayA8"),  # LAY_CONST_A8
    ("lay_const_a9", 0x08, 1, "ConstArrayA9"),  # LAY_CONST_A9
    ("lay_const_a10", 0x09, 1, "ConstArrayA10"),  # LAY_CONST_A10
    ("lay_const_a11", 0x0A, 1, "ConstArrayA11"),  # LAY_CONST_A11
    ("lay_const_a12", 0x0B, 1, "ConstArrayA12"),  # LAY_CONST_A12
    ("lay_const_a13", 0x0C, 1, "ConstArrayA13"),  # LAY_CONST_A13
    ("lay_const_a14", 0x0D, 1, "ConstArrayA14"),  # LAY_CONST_A14
    ("lay_const_a15", 0x0E, 1, "ConstArrayA15"),  # LAY_CONST_A15
    ("lay_const_a16", 0x0F, 1, "ConstArrayA16"),  # LAY_CONST_A16
    ("lay_const_b1", 0x10, 0x80, "ConstArrayB1"),  # LAY_CONST_B1
    ("lay_const_b2", 0x11, 0x80, "ConstArrayB2"),  # LAY_CONST_B2
    ("lay_const_b3", 0x12, 0x80, "ConstArrayB3"),  # LAY_CONST_B3
    ("lay_const_b4", 0x13, 0x80, "ConstArrayB4"),  # LAY_CONST_B4
    ("lay_const_b5", 0x14, 0x80, "ConstArrayB5"),  # LAY_CONST_B5
    ("lay_const_b6", 0x15, 0x80, "ConstArrayB6"),  # LAY_CONST_B6
    ("lay_const_b7", 0x16, 0x80, "ConstArrayB7"),  # LAY_CONST_B7
    ("lay_const_b8", 0x17, 0x80, "ConstArrayB8"),  # LAY_CONST_B8
    ("lay_const_b9", 0x18, 0x80, "ConstArrayB9"),  # LAY_CONST_B9
    ("lay_const_b10", 0x19, 0x80, "ConstArrayB10"),  # LAY_CONST_B10
    ("lay_const_b11", 0x1A, 0x80, "ConstArrayB11"),  # LAY_CONST_B11
    ("lay_const_b12", 0x1B, 0x80, "ConstArrayB12"),  # LAY_CONST_B12
    ("lay_const_b13", 0x1C, 0x80, "ConstArrayB13"),  # LAY_CONST_B13
    ("lay_const_b14", 0x1D, 0x80, "ConstArrayB14"),  # LAY_CONST_B14
    ("lay_const_b15", 0x1E, 0x80, "ConstArrayB15"),  # LAY_CONST_B15
    ("lay_const_b16", 0x1F, 0x80, "ConstArrayB16"),  # LAY_CONST_B16
    ("lay_const_c1", 0x20, 0, "ConstArrayC1"),  # LAY_CONST_C1
    ("lay_const_c2", 0x21, 0, "ConstArrayC2"),  # LAY_CONST_C2
    ("lay_const_c3", 0x22, 0, "ConstArrayC3"),  # LAY_CONST_C3
    ("lay_const_c4", 0x23, 0, "ConstArrayC4"),  # LAY_CONST_C4
    ("lay_const_c5", 0x24, 0, "ConstArrayC5"),  # LAY_CONST_C5
    ("lay_const_c6", 0x25, 0, "ConstArrayC6"),  # LAY_CONST_C6
    ("lay_const_c7", 0x26, 0, "ConstArrayC7"),  # LAY_CONST_C7
    ("lay_const_c8", 0x27, 0, "ConstArrayC8"),  # LAY_CONST_C8
    ("lay_const_c9", 0x28, 0, "ConstArrayC9"),  # LAY_CONST_C9
    ("lay_const_c10", 0x29, 0, "ConstArrayC10"),  # LAY_CONST_C10
    ("lay_const_c11", 0x2A, 0, "ConstArrayC11"),  # LAY_CONST_C11
    ("lay_const_c12", 0x2B, 0, "ConstArrayC12"),  # LAY_CONST_C12
    ("lay_const_c13", 0x2C, 0, "ConstArrayC13"),  # LAY_CONST_C13
    ("lay_const_c14", 0x2D, 0, "ConstArrayC14"),  # LAY_CONST_C14
    ("lay_const_c15", 0x2E, 0, "ConstArrayC15"),  # LAY_CONST_C15
    ("lay_const_c16", 0x2F, 0, "ConstArrayC16"),  # LAY_CONST_C16
    ("lfo_waveform", 0x30, 0, "LFO_Waveform"),  # LFO_WAVEFORM
    ("lfo_amplitude", 0x31, 128 + 64, "LFO_Amplitude"),  # LFO_AMPLITUDE
    ("lfo_phase", 0x32, 0, "LFO_Phase"),  # LFO_PHASE
    ("lfo_steps", 0x33, 15, "LFO_Interval"),  # LFO_STEPS
    ("lfo_steps_rst", 0x34, 15, "LFO_Reset_Interval"),  # LFO_STEPS_RST
    ("lfo_enable_flags", 0x35, 0, "LFO_Flags"),  # LFO_ENABLE_FLAGS
    ("lfo_cc", 0x36, 0, "LFO_ExtraCC"),  # LFO_CC
    ("lfo_cc_offset", 0x37, 64, "LFO_ExtraCC_Offset"),  # LFO_CC_OFFSET
    ("lfo_cc_ppqn", 0x38, 6, "LFO_ExtraCC_PPQN"),  # LFO_CC_PPQN
    #   ( 'reserved'                        , 0x39,    0, '',),                      # RESERVED
    #   ( 'reserved'                        , 0x3a,    0, '',),                      # RESERVED
    #   ( 'reserved'                        , 0x3b,    0, '',),                      # RESERVED
    #   ( 'reserved'                        , 0x3c,    0, '',),                      # RESERVED
    ("midi_bank_l", 0x3D, 0, "MIDI_BankL"),  # MIDI_BANK_L
    ("midi_bank_h", 0x3E, 0, "MIDI_BankH"),  # MIDI_BANK_H
    ("midi_pc", 0x3F, 0, "MIDI_ProgramChange"),  # MIDI_PC
    ("mode", 0x40, 1, "TrackMode"),  # MODE
    ("mode_flags", 0x41, 0x03, "TrackModeFlags"),  # MODE_FLAGS
    ("midi_event_mode", 0x42, 0, "EventMode"),  # MIDI_EVENT_MODE
    ("limit_lower", 0x43, 0, "NoteLimitLower"),  # LIMIT_LOWER
    ("limit_upper", 0x44, 0, "NoteLimitUpper"),  # LIMIT_UPPER
    #   ( 'busasg'                          , 0x45,    0, ''),                         # BUSASG
    ("midi_channel", 0x46, 0, "MIDI_Channel"),  # MIDI_CHANNEL
    ("midi_port", 0x47, 0, "MIDI_Port"),  # MIDI_PORT
    ("direction", 0x48, 0, "DirectionMode"),  # DIRECTION
    ("steps_replay", 0x49, 0, "StepsReplay"),  # STEPS_REPLAY
    ("steps_forward", 0x4A, 0, "StepsForward"),  # STEPS_FORWARD
    ("steps_jmpbck", 0x4B, 0, "StepsJumpBack"),  # STEPS_JMPBCK
    ("clk_divider", 0x4C, 0x0F, "Clockdivider"),  # CLK_DIVIDER
    ("length", 0x4D, 0x0F, "Length"),  # LENGTH
    ("loop", 0x4E, 0, "Loop"),  # LOOP
    ("clkdiv_flags", 0x4F, 0, "Clockdivider"),  # CLKDIV_FLAGS
    ("transpose_semi", 0x50, 0, "TransposeSemitones"),  # TRANSPOSE_SEMI
    ("transpose_oct", 0x51, 0, "TransposeOctaves"),  # TRANSPOSE_OCT
    ("groove_value", 0x52, 0, "GrooveIntensity"),  # GROOVE_VALUE
    ("groove_style", 0x53, 0, "GrooveStyle"),  # GROOVE_STYLE
    ("morph_mode", 0x54, 0, "MorphMode"),  # MORPH_MODE
    ("morph_dst", 0x55, 0, "MorphDestinationRange"),  # MORPH_DST
    ("humanize_value", 0x56, 0, "HumanizeIntensity"),  # HUMANIZE_VALUE
    ("humanize_mode", 0x57, 0, "HumanizeMode"),  # HUMANIZE_MODE
    ("par_asg_drum_layer_a", 0x58, 0, "DrumParAsgnA"),  # PAR_ASG_DRUM_LAYER_A
    ("par_asg_drum_layer_b", 0x59, 0, "DrumParAsgnB"),  # PAR_ASG_DRUM_LAYER_B
    ("par_asg_drum_layer_c", 0x5A, 0, "DrumParAsgnC"),  # PAR_ASG_DRUM_LAYER_C
    ("par_asg_drum_layer_d", 0x5B, 0, "DrumParAsgnD"),  # PAR_ASG_DRUM_LAYER_D
    ("steps_repeat", 0x5C, 0, "StepsRepeat"),  # STEPS_REPEAT
    ("steps_skip", 0x5D, 0, "StepsSkip"),  # STEPS_SKIP
    ("steps_rs_interval", 0x5E, 0x03, "StepsRepeatSkipInterval"),  # STEPS_RS_INTERVAL
    ("asg_gate", 0x60, 1, "TriggerAsngGate"),  # ASG_GATE
    ("asg_accent", 0x61, 2, "TriggerAsngAccent"),  # ASG_ACCENT
    ("asg_roll", 0x62, 3, "TriggerAsngRoll"),  # ASG_ROLL
    ("asg_glide", 0x63, 4, "TriggerAsngGlide"),  # ASG_GLIDE
    ("asg_skip", 0x64, 5, "TriggerAsgnSkip"),  # ASG_SKIP
    ("asg_random_gate", 0x65, 6, "TriggerAsgnRandomGate"),  # ASG_RANDOM_GATE
    ("asg_random_value", 0x66, 7, "TriggerAsgnRandomValue"),  # ASG_RANDOM_VALUE
    ("asg_no_fx", 0x67, 8, "TriggerAsgnNoFx"),  # ASG_NO_FX
    ("asg_roll_gate", 0x68, 0, "TriggerAsngRollGate"),  # ASG_ROLL_GATE
    ("echo_repeats", 0x70, 0, "EchoRepeats"),  # ECHO_REPEATS
    ("echo_delay", 0x71, 0x07, "EchoDelay"),  # ECHO_DELAY
    ("echo_velocity", 0x72, 15, "EchoVelocity"),  # ECHO_VELOCITY
    ("echo_fb_velocity", 0x73, 15, "EchoFeedbackVelocity"),  # ECHO_FB_VELOCITY
    ("echo_fb_note", 0x74, 24, "EchoFeedbackNote"),  # ECHO_FB_NOTE
    ("echo_fb_gatelength", 0x75, 20, "EchoFeedbackGatelength"),  # ECHO_FB_GATELENGTH
    ("echo_fb_ticks", 0x76, 20, "EchoFeedbackTicks"),  # ECHO_FB_TICKS
    ("fx_midi_mode", 0x78, 0, "FxMIDI_Mode"),  # FX_MIDI_MODE
    ("fx_midi_port", 0x79, 0, "FxMIDI_Port"),  # FX_MIDI_PORT
    ("fx_midi_channel", 0x7A, 0, "FxMIDI_Channel"),  # FX_MIDI_CHANNEL
    ("fx_midi_num_channels", 0x7B, 0, "FxMIDI_NumChannels"),  # FX_MIDI_NUM_CHANNELS
    ################################### not yet saved ################################################
    (
        "robotize_mask1",
        0x80,
        0,
        "",
    ),  # ROBOTIZE_MASK1
    (
        "robotize_mask2",
        0x81,
        0,
        "",
    ),  # ROBOTIZE_MASK2
    (
        "robotize_active",
        0x82,
        0,
        "",
    ),  # ROBOTIZE_ACTIVE
    (
        "robotize_probability",
        0x83,
        0,
        "",
    ),  # ROBOTIZE_PROBABILITY
    (
        "robotize_skip_probability",
        0x84,
        0,
        "",
    ),  # ROBOTIZE_SKIP_PROBABILITY
    (
        "robotize_note",
        0x85,
        0,
        "",
    ),  # ROBOTIZE_NOTE
    (
        "robotize_note_probability",
        0x86,
        0,
        "",
    ),  # ROBOTIZE_NOTE_PROBABILITY
    (
        "robotize_vel",
        0x87,
        0,
        "",
    ),  # ROBOTIZE_VEL
    (
        "robotize_vel_probability",
        0x88,
        0,
        "",
    ),  # ROBOTIZE_VEL_PROBABILITY
    (
        "robotize_len",
        0x89,
        0,
        "",
    ),  # ROBOTIZE_LEN
    (
        "robotize_len_probability",
        0x8A,
        0,
        "",
    ),  # ROBOTIZE_LEN_PROBABILITY
    (
        "robotize_oct",
        0x8B,
        0,
        "",
    ),  # ROBOTIZE_OCT
    (
        "robotize_oct_probability",
        0x8C,
        0,
        "",
    ),  # ROBOTIZE_OCT_PROBABILITY
    (
        "robotize_sustain_probability",
        0x8D,
        0,
        "",
    ),  # ROBOTIZE_SUSTAIN_PROBABILITY
    (
        "robotize_nofx_probability",
        0x8E,
        0,
        "",
    ),  # ROBOTIZE_NOFX_PROBABILITY
    (
        "robotize_echo_probability",
        0x8F,
        0,
        "",
    ),  # ROBOTIZE_ECHO_PROBABILITY
    (
        "robotize_duplicate_probability",
        0x90,
        0,
        "",
    ),  # ROBOTIZE_DUPLICATE_PROBABILITY
    # triplets                        0xA0 Triplets           TRIPLETS
    # manual_clock                    0xA1 ManualClock        MANUALCLOCK
    # synch_to_measure                0xA2 SynchToMeasure     SYNCHTOMEASURE
    # FxMIDI_FwdNonNotes              0xA3 FxMIDI_FwdNonNotes FxMIDI_FwdNonNotes
    # GrooveSyncToTrack               0xA4 GrooveSyncToTrack  GrooveSyncToTrack
    # EchoDisabled                    0xA5 EchoDisabled       EchoDisabled
)

# Properties in the order they appear in the V4T file
# (Important not to change order)
V4TFILE = """PatternName
ParInstruments
ParLayers
ParSteps
TrgInstruments
TrgLayers
TrgSteps
EventMode
Name
TrackMode
TrackModeFlags
MIDI_Port
MIDI_Channel
MIDI_ProgramChange
MIDI_BankH
MIDI_BankL
FxMIDI_Port
FxMIDI_Channel
FxMIDI_NumChannels
FxMIDI_Mode
FxMIDI_FwdNonNotes
DirectionMode
StepsForward
StepsJumpBack
StepsReplay
StepsRepeat
StepsSkip
StepsRepeatSkipInterval
Clockdivider
Triplets
ManualClock
SynchToMeasure
Length
Loop
TransposeSemitones
TransposeOctaves
MorphMode
MorphDestinationRange
HumanizeMode
HumanizeIntensity
GrooveStyle
GrooveIntensity
GrooveSyncToTrack
TriggerAsngGate
TriggerAsngAccent
TriggerAsngRoll
TriggerAsngGlide
TriggerAsgnSkip
TriggerAsgnRandomGate
TriggerAsgnRandomValue
TriggerAsgnNoFx
TriggerAsngRollGate
DrumParAsgnA
DrumParAsgnB
DrumParAsgnC
DrumParAsgnD
EchoDisabled
EchoRepeats
EchoDelay
EchoVelocity
EchoFeedbackVelocity
EchoFeedbackNote
EchoFeedbackGatelength
EchoFeedbackTicks
LFO_Waveform
LFO_Amplitude
LFO_Phase
LFO_Interval
LFO_Reset_Interval
LFO_Flags
LFO_ExtraCC
LFO_ExtraCC_Offset
LFO_ExtraCC_PPQN
NoteLimitLower
NoteLimitUpper
ConstArrayA
ConstArrayB
ConstArrayC
Par
Trg
"""

# SEQ_LAYER_CopyPreset
# static const u8 seq_layer_preset_table_static[][2] = {
#   // parameter             value
#   { SEQ_CC_MODE,           SEQ_CORE_TRKMODE_Normal },
#   { SEQ_CC_MODE_FLAGS,     0x03 },
#   { SEQ_CC_BUSASG,         0x00 },
#   { SEQ_CC_DIRECTION,	   0x00 },
#   { SEQ_CC_STEPS_REPLAY,   0x00 },
#   { SEQ_CC_STEPS_FORWARD,  0x00 },
#   { SEQ_CC_STEPS_JMPBCK,   0x00 },
#   { SEQ_CC_STEPS_REPEAT,   0x00 },
#   { SEQ_CC_STEPS_SKIP,     0x00 },
#   { SEQ_CC_STEPS_RS_INTERVAL,0x03 },
#   { SEQ_CC_CLK_DIVIDER,    0x0f },
#   { SEQ_CC_CLKDIV_FLAGS,   0x00 },
#   { SEQ_CC_LENGTH,         0x0f },
#   { SEQ_CC_LOOP,           0x00 },
#   { SEQ_CC_TRANSPOSE_SEMI, 0x00 },
#   { SEQ_CC_TRANSPOSE_OCT,  0x00 },
#   { SEQ_CC_GROOVE_VALUE,   0x00 },
#   { SEQ_CC_GROOVE_STYLE,   0x00 },
#   { SEQ_CC_MORPH_MODE,     0x00 },
#   { SEQ_CC_MORPH_DST,      0x00 },
#   { SEQ_CC_HUMANIZE_VALUE, 0x00 },
#   { SEQ_CC_HUMANIZE_MODE,  0x00 },
#   { SEQ_CC_ECHO_REPEATS,   0x00 },
#   { SEQ_CC_ECHO_DELAY,     0x07 }, // 1/8
#   { SEQ_CC_ECHO_VELOCITY,  15 }, // 75%
#   { SEQ_CC_ECHO_FB_VELOCITY, 15 }, // 75%
#   { SEQ_CC_ECHO_FB_NOTE,   24 }, // +0
#   { SEQ_CC_ECHO_FB_GATELENGTH, 20 }, // 100%
#   { SEQ_CC_ECHO_FB_TICKS,  20 }, // 100%
#   { SEQ_CC_LFO_WAVEFORM,   0x00 }, // off
#   { SEQ_CC_LFO_AMPLITUDE,  128 + 64 },
#   { SEQ_CC_LFO_PHASE,      0 },
#   { SEQ_CC_LFO_STEPS,      15 },
#   { SEQ_CC_LFO_STEPS_RST,  15 },
#   { SEQ_CC_LFO_ENABLE_FLAGS, 0 },
#   { SEQ_CC_LFO_CC,         0 },
#   { SEQ_CC_LFO_CC_OFFSET,  64 },
#   { SEQ_CC_LFO_CC_PPQN,    6 }, // 96 ppqn
#   { SEQ_CC_LIMIT_LOWER,    0 },
#   { SEQ_CC_LIMIT_UPPER,    0 },
#   { 0xff,                  0xff } // end marker
# };


if __name__ == "__main__":
    """Test Track configurations"""
    from model.track import Track

    class Parent:
        def __init__(self):
            self.name = ""

    for k, v in TRACK_LAYER_CONFIG.items():
        t = Track(Parent(), None)
        t.configure(k)
        tlr = t.layer_config_repr()
        print(
            f'"{k:24}"\n"{tlr:24}" {k == tlr:8}' f" {t.p_tot_size:8} {t.t_tot_size:8}"
        )
