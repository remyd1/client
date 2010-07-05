#!/usr/bin/env python

import os
import sys
from optparse import OptionParser

from stratuslab.CommandBase import CommandBase   
from stratuslab.Configurator import Configurator

# TODO: Display some information when modify config?
class MainProgram(CommandBase):
    '''A command-line program to configure StrtusLab.'''

    def __init__(self):
        self.dirPath =  os.path.abspath(os.path.dirname(__file__))
        usage = 'usage: %prog [options] key value'
        self.parser = OptionParser(usage=usage)

        self.parser.add_option('-c', '--config', dest='configFile',
                help='default configuration file', metavar='FILE',
                default='%s/stratuslab.cfg' % self.dirPath)
        self.parser.add_option('-q', '--quiet', action='store_false', 
                dest='verbose', default=True,
                help='don\'t print status messages to stdout')
        self.parser.add_option('-v', action='store_true', dest='verbose', 
                default=False, help='display more informations')

        (self.options, self.args) = self.parser.parse_args()

        super(MainProgram,self).__init__()

    def doWork(self):
        if len(self.args) < 2:
            raise self.usageExitTooFewArguments()
        elif len(self.args) > 2:
            raise self.usageExitTooManyArguments()

        configurator = Configurator(self.options.configFile)
        self.logMessage('User config file: %s' % configurator.userConfigFile)
        configurator.setOption(key=self.args[0], value=self.args[1])

        self.logMessage('Done!')


if __name__ == '__main__':
    try:
        MainProgram()
    except KeyboardInterrupt:
        print '\n\nExecution interrupted by the user... goodbye!'

