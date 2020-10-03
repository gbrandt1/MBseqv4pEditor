
# Various GUI related constants

PAD_FRM = 5
PAD_LF = 5

NOTE_CONST_LABELS = {
    'a': 'Parameter Layer Assignments:',
    'b': 'CC Assignments:',
    'c': 'Constant Array C:',
}

DRUM_CONST_LABELS = {
    'a': 'MIDI Notes for Drum Instruments:',
    'b': 'MIDI Velocity:',
    'c': 'MIDI Accent Velocity:',
}

TRACK_CONST_LABELS = {
    "Note": NOTE_CONST_LABELS,
    "Chord": NOTE_CONST_LABELS,
    "CC": NOTE_CONST_LABELS,
    "Drum": DRUM_CONST_LABELS,
    "Combined": NOTE_CONST_LABELS,
}

TRACK_GUI_PAGES = {
    'MIDI': (
        ('Mode', 'playmode'),  # 'mode'
        ('Port', 'midi_port'),
        ('Chn.', 'midi_channel'),
        ('Trk.', None),
        ('PC', 'midi_pc'),
        ('BnkH', 'midi_bank_h'),
        ('BnkL', 'midi_bank_l'),
        #('Name', None),
    ),
    'Length': (
        ('Length', 'length'),
        ('Loop', 'loop'),
    ),
    'Direction': (
        ('Mode', 'dir_mode'),  # 'direction'),
        ('Forward.', 'steps_forward'),
        ('Back', 'steps_jmpbck'),
        ('Replay', 'steps_replay'),
        ('Repeat', 'steps_repeat'),
        ('Skip', 'steps_skip'),
        ('Interval', 'steps_rs_interval'),
        ('SyncM', None),
    ),
    'Clock Divider': (
        #('', None),
        ('SyncM', None),
        ('Manual', None),
        ('Timebase', None),
        # u8 value_dummy;          // clock divider value
        # u8 SYNCH_TO_MEASURE:1;   // synch to globally selectable measure
        # u8 TRIPLETS:1;           // play triplets
        # u8 MANUAL:1;
    ),
    'Transpose': (
        ('Octave', 'transpose_oct'),
        ('Semitone', 'transpose_semi'),
    ),
    'Groove': (
        ('Style', 'groove_style'),
        ('Intensity', 'groove_value'),
        ('Sync', None),
    ),
    'Morphing': (
        ('Mode', 'morph_mode'),
        ('Destination Range', 'morph_dst'),
    ),
    # 'ConstArrays': (
    #    ('A', None),
    #    ('B', None),
    #    ('C', None),
    # ),
    'Trigger Layers': (
        ('Gate', 'asg_gate'),
        ('Accent', 'asg_accent'),
        ('Roll', 'asg_roll'),
        ('Glide', 'asg_glide'),
        ('Skip', 'asg_skip'),
        ('Random Gate', 'asg_random_gate'),
        ('Random Value', 'asg_random_value'),
        ('NoFX', 'asg_no_fx'),
        ('Roll Gate', 'asg_roll_gate'),
    ),
    'Drum Parameters': (
        ('A', 'par_asg_drum_layer_a'),
        ('B', 'par_asg_drum_layer_b'),
        ('C', 'par_asg_drum_layer_c'),
        ('D', 'par_asg_drum_layer_d'),
    ),
    'FX: Echo': (
        #('Enabled', None),
        ('Repeats', 'echo_repeats'),
        ('Delay', 'echo_delay'),
        ('Velocity', 'echo_velocity'),
        ('FB Velocity', 'echo_fb_velocity'),
        ('FB Note', 'echo_fb_note'),
        ('FB Gatelength', 'echo_fb_gatelength'),
        ('FB Ticks', 'echo_fb_ticks'),
    ),
    'FX: Humanize': (
        ('Mode', 'humanize_mode'),
        ('Intensity', 'humanize_value'),
    ),
    # not yet saved
    # ('FX: Robotize', (
    #    ('Prob', None), ('Skip', None),
    #    ('Octv', None), ('Note', None),
    #    ('VelCC', None), ('Len ', None),
    #    ('Sust', None), ('NoFX', None),
    #    ('+Echo', None), ('+Dup ', None),
    # ), ),
    'FX: Limit': (
        ('Lower', 'limit_lower'),
        ('Upper', 'limit_upper'),
    ),
    'FX: LFO': (
        ('Waveform', 'lfo_waveform'),
        ('Amplitude', 'lfo_amplitude'),
        ('Phase', 'lfo_phase'),
        ('Interval', 'lfo_steps'),
        ('Reset Interval', 'lfo_steps_rst'),
        ('Extra CC', 'lfo_cc'),
        ('Offset', 'lfo_cc_offset'),
        ('PPQN', 'lfo_cc_ppqn'),
    ),
    'FX: LFO Flags': (
        ('Oneshot', None),
        ('Note', None),
        ('Velocity', None),
        ('Length', None),
        ('CC', None),
    ),
    'FX: Duplicate': (
        ('Port', 'fx_midi_port'),
        ('Channel', 'fx_midi_channel'),
        ('NumChannels', 'fx_midi_num_channels'),
        ('Mode', 'fx_midi_mode'),
        ('FwdNonNotes', None),
    ),
}
