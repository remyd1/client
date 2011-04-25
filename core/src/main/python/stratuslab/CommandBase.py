#
# Created as part of the StratusLab project (http://stratuslab.eu),
# co-funded by the European Commission under the Grant Agreement
# INFSO-RI-261552."
#
# Copyright (c) 2011, SixSq Sarl
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import socket
import sys
import os
from optparse import OptionParser
import xmlrpclib

import stratuslab.Util as Util
from stratuslab.VersionChecker import VersionChecker
import stratuslab.Exceptions as Exceptions
from stratuslab.ConfigHolder import ConfigHolder

class CommandBase(object):
    
    def __init__(self):
        self.options = None
        self.config  = None
        self._configKeysClassAttrsTwoWayMap = {}

        self.verboseLevel = 0
        self.parser = None
        self._setParserAndParse()
        self._loadConfigFileAndUpdateOptions()
        self.checkOptions()
        self._callAndHandleErrors(self, self.doWork.__name__)

    def _setParserAndParse(self):
        self.parser = OptionParser()
        self.parser.add_option('-v', '--verbose', dest='verboseLevel',
                help='verbose level. Add more to get more details',
                action='count', default=self.verboseLevel)

        self._addConfigFileOption()

        self.parse()
        self.verboseLevel = self.options.verboseLevel
        
        self._loadConfigFileAndUpdateOptions()

    def _addConfigFileOption(self):
        pass

    def _loadConfigFileAndUpdateOptions(self):
        pass

    def _callAndHandleErrors(self, methodName, *args, **kw):
        
        try:
            Util.runMethodByName(methodName, *args, **kw)
        except ValueError, ex:
            sys.stderr.writelines('\nError: %s\n' % str(ex))
            sys.exit(3)
        except xmlrpclib.ProtocolError, ex:
            self.raiseOrDisplayError('Error: %s' % ex.errmsg)
        except socket.sslerror, ex:
            self._checkPythonVersionAndRaise()
            self.raiseOrDisplayError('Network error: %s' % ex)
        except socket.error, ex:
            self.raiseOrDisplayError('Network error: %s' % ex)
        except socket.gaierror, ex:
            self.raiseOrDisplayError('Network error: %s' % ex)
        except Exception, ex:
            self.raiseOrDisplayError(ex)

    def _checkPythonVersionAndRaise(self):
        try:
            VersionChecker().check()
        except Exceptions.ValidationException, ex:
            self.raiseOrDisplayError(ex)
        
    def parse(self):
        pass

    def checkOptions(self):
        pass

    def checkArgumentsLength(self):
        pass

    def usageExitTooFewArguments(self):
        return self.parser.error('Too few arguments')

    def usageExitTooManyArguments(self):
        return self.parser.error('Too many arguments')

    def usageExitWrongNumberOfArguments(self):
        return self.parser.error('Wrong number of arguments')
    
    def raiseOrDisplayError(self, errorMsg):
        if self.verboseLevel > 0:
            raise
        else:
            Util.printError(errorMsg, exit=False)
        sys.exit(-1)

    def printDetail(self, message):
        Util.printDetail(message, self)

class CommandBaseUser(CommandBase):
    def __init__(self):
        super(CommandBaseUser, self).__init__()

    def _addConfigFileOption(self):
        ConfigHolder.addConfigFileUserOption(self.parser)

    def _loadConfigFileAndUpdateOptions(self):
        self._loadConfigFile()
        self._updateOptionsFromConfigFile()

    def _loadConfigFile(self):
        if not hasattr(self.options, 'configFile'):
            return

        configFile = self.options.configFile
        try:
            self.config, self._configKeysClassAttrsTwoWayMap = \
                ConfigHolder.configFileToDictWithFormattedKeys(configFile, withMap=True)
        except Exceptions.ConfigurationException:
            if configFile == Util.defaultConfigFileClient:
                Util.printWarning('Default configuration file does not exists: %s' % 
                                  configFile)
                return
            else:
                raise

    def _updateOptionsFromConfigFile(self):
        """Order of precedence:
        * command line option
        * environment variable
        * configuration file
        * default value

        Update of the corresponding options object key/value pairs can only be 
        done if neither corresponding command line option nor environment
        variable was given/set.

        The following key/attribute/env.var. naming is assumed:

         configuraion file | class attribute | environment variable
         ----------------- + --------------- + --------------------
         p12_certificate   | p12Certificate  | STRATUSLAB_P12_CERTIFICATE
        """

        if not self.config:
            return

        for k in self.config:
            if k in self.options.__dict__:
                valueFromOptions = getattr(self.options, k)
                # Set the value from configuration file: 
                # * if attribute is empty
                if not valueFromOptions:
                    setattr(self.options, k, self.config[k])
                # * if default is equal to "provided" value, we may assume that 
                #   the option wasn't given on command line; but we are going 
                #   to double check this in each Option object of the parser as 
                #   the same value might have been provided via environment var.
                elif valueFromOptions == self.parser.defaults[k]:
                    for optionObj in self.parser.option_list:
                        # work only with Option object for the particular key 
                        if optionObj.dest != k:
                            continue
                        # Update iff
                        # * the long option is NOT in the list of the CLI arguments
                        if not (optionObj._long_opts[0] in sys.argv):
                            # * and not set via corresponding environment variable
                            envVar = 'STRATUSLAB_%s' % self._configKeysClassAttrsTwoWayMap[k].upper()
                            if not os.getenv(envVar):
                                setattr(self.options, k, self.config[k])
                else:
                    pass

class CommandBaseSysadmin(CommandBase):
    def __init__(self):
        super(CommandBaseSysadmin, self).__init__()

    def _addConfigFileOption(self):
        ConfigHolder.addConfigFileSysadminOption(self.parser)
