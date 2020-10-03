# MidiBox SEQ V4+ Editor

[screenshot step editor]: https://github.com/gbrandt1/MBseqv4pEditor/blob/main/screenshot-2020-10-03.png "MidiBox SEQ V4+ Editor"


Version: 00.00.01 -under development-

by southpole (Gerhard Brandt)

Disclaimer:
* This is still alpha software!!!
* Only run the editor on a backup copy of your SD card!!!
* Discussion thread on the forum:
http://midibox.org/forums/topic/21501-new-editor-for-mb-seq-v4-under-development/

This is an editor to modify the SD card contents of a MIDIbox SEQ V4+ hardware MIDI sequencer by Torsten Klose et al.
Find more about the MIDIbox project and SEQ V4+ here:

* Homepage: <http://www.ucapps.de/midibox_seq.html>
* Forum: <http://midibox.org/forums/>
* Hardware Shop: <https://www.midiphy.com/>

The goal of this editor is not to duplicate the detailed and powerful editing capabilites
of the SEQ v4+, but to facilitate batch processes (such as quickly duplicating a sequence of patterns to
an entire bank) and provide a better overview of the complex configuration data than the "double letterbox" interface of the SEQ v4+.

The program assumes you are familiar with the SEQ v4+ sequencer.
If not you should study the documentation:

* Beginners guide <http://wiki.midibox.org/doku.php?id=mididocs:seq:beginners_guide:start>
* Full manual <http://ucapps.de/midibox_seq_manual_m.html>
* MIOS32 Software: <https://github.com/midibox/mios32/tree/master/apps/sequencers/midibox_seq_v4>

The editor was built bottom-up from the various file formats written to the SD card rather than from user perspective like the SEQ v4+ interface on the actual hardware.
That's why some items seem to be in different places or are presented slightly different.


## System requirements

The editor is written in Python 3 and features a TkInter GUI but also a Python Cmd based shell interface.

If you do not have a compatible system installation of Python you can use a
virtual environment and install required packages using  requirements.txt

Since Python and TkInter are quite slow a fast computer is of advantage.


## Cmd command line interface

Run it using

    python3 mbs4edit_sh.py

* Type '?' to see available commands.
* Tab completion for certain options and paths
* Command history. Saved in .seqv4p_history

Example Session:

    open_sdcard path/to/your/sdard
    show_status
    dump session
    dump track
    x

## TKinter GUI

Run it using

    python3 mbs4edit.py

### Main window

The main window shows editor tabs, phrase bar and the status bar

### Status Bar

Shows from left to right: Active SD Card, session, track and pattern.

Modifications are indicated by a black circle.

### Phrase Bar

* Show the edited pattern in each bank, and edited track in the bank.
* Use the track buttons G1T1 etc. to go to the last editor view of the respective track.

### Pattern Banks

* Inline editing of names supported. Default categories and labels from the TRKCAT and TRKLABELS files are supported.
* Last selected pattern of each bank is set at the phrase bar below.
* Pasting supports two modes
  * Paste once if target selection is single pattern
  * Fill if target selection is larger than copied pattern block

    --> Enables to quickly fill entire bank with a few identical patterns

### Step Editor

* Inplace edit of parameter values via spin boxes
* Double-click to edit triggers
* Select rows to edit using the tree view, 'Select All' button and 'Show Pars', 'Show Trgs' checkboxes.
* Wrap: Toggle main view mode
  * unwrapped: show all steps (in pages of 16) by scrolling left/right
        (parameter layers are repeated if they have fewer steps than trigger layers)
  * wrapped: show all steps in pages of 16 steps underneath each other
* Raw: Show numerical parameter value or SEQ V4+ like representation depending on parameter layer type.
* Clear: set selected rows to default values.
* Random: randomize selected rows scaled between default and max. values by slider

### Track Configuration

* Edit track configuration values.

### FX Configuration

* Edit FX configuration values.

### Songs

* Select song to edit in song bank on the left.
* Song is structured following phrases of 8 steps according to
  the SEQ V4+ 'Save&Take Over Ptns.' function.
* Preset: sets selected entire songs or selected phrases to default phrase actions.

### Mixer Maps

* Mixer maps editor

TO DO

* Undo functionality
* All the greyed out items: Global and Session Configurations, Bookmarks, Grooves,


## License

* Like everything in MidiBox, this project is beerware. You can buy me a beer via PayPal if you like:

    gerhard.brandt76@gmail.com

* Free for non-commercial private use.
* Commercial use not allowed.

