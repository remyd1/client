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
import re
from ConfigParser import SafeConfigParser

import Util
from Exceptions import ConfigurationException
import ConfigParser

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
            for k, v in config.items(section):
                dict[k] = v
            dicts[section] = dict
        return dicts

    @staticmethod
    def _convertToDict(config):
        dict = {}
        for section in config.sections():
            for k, v in config.items(section):
                _v = v
                if '\n' in v:
                    _v = ConfigHolder._convertToMultiLineValue(v)
                dict[k] = _v
        return dict

    @staticmethod
    def _convertToMultiLineValue(value):
        return ' ' + '\n '.join(filter(None, value.split('\n')))

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
                           help='user configuration file. Default %s' % Util.defaultConfigFileUser,
                           metavar='FILE',
                           default=Util.defaultConfigFileUser)
        parser.add_option('--user-config-section', dest='selected_section',
                           help='Section to load in the user configuration file. ' \
                           'Can also be set via environment variable: %s' % Util.userConfigFileSelectedSection,
                           default=os.getenv(Util.userConfigFileSelectedSection, None))
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
        if '_' not in key:
            return key

        formattedKey = ''.join([part.title() for part in key.split('_')])
        if len(formattedKey) > 1:
            formattedKey = formattedKey[0].lower() + formattedKey[1:]
        return formattedKey

    def __init__(self, options={}, config={}):
        if not isinstance(options, dict):
            raise TypeError('options parameter must be omitted or a dictionary')
        if not isinstance(config, dict):
            raise TypeError('config parameter must be omitted or a dictionary')
        object.__setattr__(self, 'options', options)
        object.__setattr__(self, 'config', config)

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
        for attr in ['options', 'config']:
            if getattr(self, attr):
                output += '** %s:\n' % attr.upper()
                pkeys = getattr(self, attr).keys()
                pkeys.sort()
                output += '\n'.join(['  %s = %s' % (k, getattr(self, attr)[k]) for k in pkeys]) + '\n'
        return output

    def __getattribute__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            pass
        try:
            return object.__getattribute__(self, 'options')[key]
        except KeyError:
            pass
        try:
            return object.__getattribute__(self, 'config')[key]
        except KeyError:
            pass
        raise AttributeError("'%s' object has no attribute '%s'" % (object.__getattribute__(self, '__class__'), key))

    def __setattr__(self, key, value):
        self.options[key] = value
    
    
class UserConfigurator(object):
    
    SELECTED_SECTION = 'selected_section'
    INSTANCE_TYPES_SECTION = 'instance_types'
    
    @staticmethod
    def configFileToDictWithFormattedKeys(configFile, withMap=False, selected_section=None):
        '''This accepts either a file-like object or a filename.'''
        usercfg = UserConfigurator(configFile)
        config = usercfg.getDict(selected_section)
        config['user_defined_instance_types'] = usercfg.getUserDefinedInstanceTypes()
        return ConfigHolder._formatConfigKeys(config, withMap)

    def __init__(self, configFile=Util.defaultConfigFileUser):
        '''Reads argument as file-like object first, then as a filename.
           Note that NO checks are made on the existance of the referenced file.'''
        self._dict = {}
        self._parser = SafeConfigParser()
        try:
            try:
                self._parser.readfp(configFile)
            except AttributeError:
                self._parser.read(configFile)
        except ConfigParser.ParsingError, ex:
            raise ConfigurationException(ex)
    
    def _loadDefaults(self):
        self._loadSection('default')
    
    def _loadSection(self, section):
        self._dict.update(dict(self._parser.items(section)))

    def getUserDefinedInstanceTypes(self):
        types = self.getSectionDict(UserConfigurator.INSTANCE_TYPES_SECTION)
        for name in types.keys():
            t = UserConfigurator._instanceTypeStringToTuple(types[name])
            if UserConfigurator._validInstanceTypeTuple(t):
                types[name] = t
            else:
                del types[name]
        return types

    @staticmethod
    def _validInstanceTypeTuple(t):
        if (len(t) != 3):
            return None
        cpu, ram, swap = t
        if (not isinstance(cpu, int) or cpu <= 0):
            return None
        if (not isinstance(ram, int) or ram <=0):
            return None
        if (not isinstance(swap, int) or swap < 0):
            return None
        return t

    @staticmethod
    def _instanceTypeStringToTuple(s):
        return tuple(map (int, re.findall('\d+', s)))

    def getDefaultInstanceType(self):
        if (hasattr(self, 'defaultInstanceType') and self.defaultInstanceType):
            return self.defaultInstanceType
        else:
            return None

    def getDict(self, selected_section=None):
        self._dict = {}
        try:
            self._loadDefaults()
        except ConfigParser.NoSectionError, ex:
            raise ConfigurationException(ex)

        if not selected_section:
            if self._parser.has_option('default', UserConfigurator.SELECTED_SECTION):
                selected_section = self._parser.get('default', UserConfigurator.SELECTED_SECTION)

        if selected_section:
            try:
                self._loadSection(selected_section)
            except ConfigParser.NoSectionError, ex:
                raise ConfigurationException(ex)
        ConfigHolder._formatConfigKeys(self._dict)
        return self._dict

    def getSectionDict(self, section=None):
        '''Create dictionary from configuration file section.
           Returns an empty dictionary if section doesn't exist.'''
        values = {}

        if section:
            try:
                values = dict(self._parser.items(section))
            except ConfigParser.NoSectionError, ex:
                pass

        return values
