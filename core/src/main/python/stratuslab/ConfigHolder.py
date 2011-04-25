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
import os
from ConfigParser import SafeConfigParser

import Util
from Exceptions import ConfigurationException

class ConfigHolder(object):

    @staticmethod
    def configFileToDict(configFileName):
        config = ConfigHolder.parseConfig(configFileName)
        dict = ConfigHolder._convertToDict(config)
        return dict

    @staticmethod
    def configFileToDictWithFormattedKeys(configFileName, withMap=False):
        config = ConfigHolder.configFileToDict(configFileName)
        return ConfigHolder._formatConfigKeys(config, withMap)

    @staticmethod
    def configFileHandlerToDict(configFileHandler):
        config = SafeConfigParser()
        config.readfp(configFileHandler)
        dict = ConfigHolder._convertToDict(config)
        return dict

    @staticmethod
    def convertToSectionDict(config):
        dicts = {}
        for section in config.sections():
            dict = {}
            for k,v in config.items(section):
                dict[k] = v
            dicts[section] = dict
        return dicts

    @staticmethod
    def _convertToDict(config):
        dict = {}
        for section in config.sections():
            for k,v in config.items(section):
                dict[k] = v
        return dict

    @staticmethod
    def parseConfig(configFileName):
        if not os.path.isfile(configFileName):
            msg = 'Configuration file %s does not exist' % configFileName
            raise ConfigurationException(msg)
        config = SafeConfigParser()
        config.read(configFileName)
        return config

    @staticmethod
    def addConfigFileSysadminOption(parser):
        parser.add_option('-c', '--config', dest='configFile', 
                            help='configuration file. Default %s' % Util.defaultConfigFile, 
                            metavar='FILE',
                            default=Util.defaultConfigFile)
        return parser

    @staticmethod
    def addConfigFileUserOption(parser):
        parser.add_option('-c', '--config', dest='configFile', 
                           help='client configuration file. Default %s' % Util.defaultConfigFileClient, 
                           metavar='FILE',
                           default=Util.defaultConfigFileClient)
        return parser

    @staticmethod
    def _formatConfigKeys(config, withMap=False):
        _dict = {}
        _map = {}
        for k, v in config.items():
            camel = ConfigHolder._camelCase(k)
            _dict[camel] = v
            if withMap:
                _map[k] = camel
                _map[camel] = k
        if withMap:
            return _dict, _map
        else:
            return _dict

    @staticmethod
    def _camelCase(key):
        formattedKey = ''.join([part.title() for part in key.split('_')])
        if len(formattedKey) > 0:
            formattedKey = formattedKey[0].lower() + formattedKey[1:]
        return formattedKey

    def __init__(self, options={}, config={}):
        self.options = options
        self.config = config

    def assign(self, obj):
        Util.assignAttributes(obj, ConfigHolder._formatConfigKeys(self.config))
        Util.assignAttributes(obj, self.options)

    def copy(self):
        copy = ConfigHolder(self.options.copy(), self.config.copy())
        return copy

    def set(self, key, value):
        self.options[key] = value

    def __str__(self):
        output = '* %s:\n' % self.__class__.__name__
        for p in ['options', 'config']:
            if getattr(self, p):
                output += '** %s:\n' % p.upper()
                output += '\n'.join(['  %s = %s'%(k,v) for k,v in getattr(self, p).items()]) + '\n'
        return output
