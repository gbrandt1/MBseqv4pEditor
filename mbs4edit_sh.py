# !/usr/bin/env python3

import logging
from controller import Controller
from helpers import dump, LOGW_NAME
import glob
import os
from cmd import Cmd
import readline
import rlcompleter
# readline.parse_and_bind("tab: complete")
readline.parse_and_bind("bind ^I rl_complete")

cwd = os.getcwd()

histfile = os.path.join(cwd,'.seqv4p_history')
histfile_size = 1000


logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


#  for autocompletion
_DUMP_OBJECTS = [
    'all', 'sdcard', 'session', 'bank',
    'pattern', 'pattern_selection',
    'track', 'track_selection',
    'phrase',
    'song', 'song_bank',
    'mixer_map', 'mixer_map_bank',
]


class SeqV4PShell(Controller, Cmd):

    ruler='\u2015'
    horizontal_bar = "\u2015"*80
    intro = (
        f'{horizontal_bar}'
        f'\nMidiBox SEQ V4+ File Editor - Interactive Shell\n'
        f'{horizontal_bar}'
        f'\n\nType help or ? to list commands.\n\n'
    )
    prompt = 'seqv4p: '

    def __init__(self, path=None):
        Controller.__init__(self, path)
        Cmd.__init__(self)

    def preloop(self):
        logger.info(f'preloop: Use history file {histfile}')
        if readline and os.path.exists(histfile):
            readline.read_history_file(histfile)

    def postloop(self):
        if readline:
            readline.set_history_length(histfile_size)
            readline.write_history_file(histfile)

    def default(self, arg=None):
        if arg == 'x' or arg == 'q':
            return self.do_exit(arg)

        logger.info(f'Default {arg}')

    def emptyline(self):
        self.onecmd('show_status')

    def precmd(self, line):
        logger.debug(f'precmd "{line}"')
        if any(s in line for s in [ 'exit', 'x', 'q', '?', 'help', 'open_sdcard' ]):
            return line
        if not self.sdcard:
            logger.warning('No SD card open.')
            return ''
        return line

    #  Commands prefixed with do_* for interactive shell (Cmd)
    def do_exit(self, arg=None):
        '''Exit application. Shorthand: Ctrl-D x q.'''
        logger.info('Bye!')
        return True

    def do_EOF(self, arg):
        return True #do_exit

    __hiden_methods = ('do_EOF',)

    def get_names(self):
        return [n for n in dir(self.__class__) if n not in self.__hiden_methods]

    # Commands wrappers from Controller

    do_show_status = Controller.show_status

    def do_open_sdcard(self, arg):
        '''Open SD Card.'''
        Controller.open_sdcard(self, arg)

    do_save_sdcard = Controller.save_sdcard
    do_save_as_sdcard = Controller.save_as_sdcard
    do_set_session = Controller.set_session
    do_set_bank = Controller.set_bank
    do_save_pattern_banks = Controller.save_pattern_banks
    do_set_pattern = Controller.set_pattern
    do_set_pattern_selection = Controller.set_pattern_selection
    do_select_all = Controller.select_all
    do_set_track = Controller.set_track
    do_set_song = Controller.set_song
    do_set_mixer_map = Controller.set_mixer_map
    do_set_sysex_setup = Controller.set_sysex_setup
    do_copy_pattern = Controller.copy_pattern
    do_paste_pattern = Controller.paste_pattern
    do_clear_pattern = Controller.clear_pattern
    do_dump_selection = Controller.dump_selection

    def do_dump(self, arg=None):
        '''Dump object.'''
        if arg == 'all':
            for obj in _DUMP_OBJECTS[1:]:
                print(f'ACTIVE {obj.upper()}:')
                self.do_dump(obj)
            return
        if arg == 'selection':
            self.do_dump_selection()

        if hasattr(self, arg):
            dump(getattr(self, arg))
        elif hasattr(self.sdcard, arg):
            dump(getattr(self.sdcard, arg))
        elif hasattr(self.session, arg):
            dump(getattr(self.session, arg))
        else:
            logger.warning(f'Object {arg} unknown.')

    # Some commands from the MIOS Studio shell
    def do_system(self, arg=None):
        '''print system info'''
        print(intro)

    def do_sdcard(self, arg=None):
        '''print SD card info'''
        print(self.sdcard)

    def do_global(self, arg=None):
        '''print global configuration'''
        print(self.sdcard.global_config)

    def do_config(self, arg=None):
        '''print local session configuration'''
        print(self.session.config)

    def do_tracks(self, arg=None):
        '''print overview of all tracks'''
        print(self.track)

    def do_track(self, arg=None):
        '''print info about specific track'''
        print(self.track)

    def do_mixer(self, arg=None):
        '''print current mixer map'''
        print(self.mixer_map)

    def do_song(self, arg=None):
        '''print current song info'''
        print(self.song)

    def do_grooves(self, arg=None):
        '''print groove templates'''
        pass #print(self.grooves)

    def do_bookmarks(self, arg=None):
        '''print bookmarks'''
        pass #print(self.bookmarks)

    # def do_save(self, arg=None):
    # def do_restore(self, arg=None):
    # def do_saveas(self, arg=None):
    # def do_new(self, arg=None):
    # def do_delete(self, arg=None):
    # def do_backup(self, arg=None):

    def do_session(self, arg=None):
        '''print current session name'''
        print(self.session.name)

    def do_sessions(self, arg=None):
        '''print all available sessions'''
        for s in self.sdcard.sessions:
            print(s)




    #  Cmd autocompletions

    def complete_dump(self, text, line, begidx, endidx):
        return [i for i in _DUMP_OBJECTS if i.startswith(text)]

    def complete_set_session(self, text, line, begidx, endidx):
        s = list(self.sdcard.sessions.keys())
        return [i for i in s if i.startswith(text)]

    def complete_open_sdcard(self, text, line, begidx, endidx):
        return autocomplete_file_path(self, text, line, begidx, endidx)

#  methods copied from GIST
#  https://gist.github.com/mingyuan-xia/e8cac85ec8cd3f8ae21760580a529846


def _append_slash_if_dir(p):
    if p and os.path.isdir(p) and p[-1] != os.sep:
        return p + os.sep
    else:
        return p


def autocomplete_file_path(self, text, line, begidx, endidx):
    """ File path autocompletion, used with the cmd module
    complete_* series functions
    """
# http://stackoverflow.com/questions/16826172/filename-tab-completion-in-cmd-cmd-of-python
    before_arg = line.rfind(" ", 0, begidx)
    if before_arg == -1:
        return  # arg not found

    fixed = line[before_arg+1:begidx]  # fixed portion of the arg
    arg = line[before_arg+1:endidx]
    pattern = arg + '*'

    completions = []
    for path in glob.glob(pattern):
        path = _append_slash_if_dir(path)
        completions.append(path.replace(fixed, "", 1))
    return completions


if __name__ == '__main__':
    logger.info(f'Starting from {cwd}')
    seqsh = SeqV4PShell()
    seqsh.cmdloop()
