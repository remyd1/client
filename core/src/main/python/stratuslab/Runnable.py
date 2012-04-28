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
import sys
import pprint

from stratuslab.Runner import Runner
from stratuslab.AuthnCommand import AuthnCommand
import stratuslab.Util as Util

from marketplace.Util import Util as MarketplaceUtil

class Runnable(AuthnCommand):
    '''Base class for command which need to start a machine.'''
    parser_usage = '''%prog [defaultOptions] image'''
    parser_description = 'image - Marketplace image ID or PDISK volume UUID'

    def __init__(self):
        self.options = None
        self.args = None
        self.image = None
        self.checkCredentials = True

        super(Runnable, self).__init__()

    def parse(self):
        defaultOptions = Runner.defaultRunOptions()

        self.parser.usage = self.parser_usage

        self.parser.description = self.parser_description

        self.parser.add_option('-k', '--key', dest='userPublicKeyFile',
                help='SSH public key(s) (.pub) to log on the machine. Default %s. In case of multiple keys, concatenate them to the file.' % defaultOptions['userPublicKeyFile'], 
                metavar='FILE',
                default=defaultOptions['userPublicKeyFile'])

        self.parser.add_option('-t', '--type', dest='instanceType',
                help='instance type to start (see --list-type for default)', metavar='TYPE',
                default=None)

        self.parser.add_option('-l', '--list-type', dest='listType',
                help='list available instance type',
                default=False, action='store_true')

        self.parser.add_option('--cpu', dest='vmCpu',
                help='number of CPU cores',
                default=None)

        self.parser.add_option('--ram', dest='vmRam',
                help='RAM in megabytes',
                default=None)

        self.parser.add_option('--swap', dest='vmSwap',
                help='swap space in megabytes',
                default=None)

        self.parser.add_option('--context-file', dest='extraContextFile', metavar='FILE',
                help='extra context file with one key=value per line',
                default=defaultOptions['extraContextFile'])
        self.parser.add_option('--context', dest='extraContextData', metavar='CONTEXT',
                help='extra context string (separate by %s)' % Util.cliLineSplitChar,
                default=defaultOptions['extraContextData'])

        self.parser.add_option('--vnc-port', dest='vncPort', metavar='PORT', type='int',
                help='VNC port number. Note for KVM it\'s the real one, not the '
                     'VNC port. So for VNC port 0 you should specify 5900, for '
                     'port 1 is 5901 and so on. ',
                default=defaultOptions['vncPort'])
        self.parser.add_option('--vnc-listen', dest='vncListen', metavar='ADDRESS',
                help='IP to listen on',
                default=defaultOptions['vncListen'])

        self.parser.add_option('--vm-template-file', dest='vmTemplateFile', metavar='FILE',
                help='VM template file. Default %s' % defaultOptions['vmTemplateFile'],
                default=defaultOptions['vmTemplateFile'])

        self.parser.add_option('--vm-cpu-amount', dest='vmCpuAmount', metavar='CPU', type='float',
                help='Percentage of CPU divided by 100 required for the Virtual Machine. '
                     'Half a processor is written 0.5. No default. If not provided, CPU value from '
                     'predefined instance types is used.',
                default=defaultOptions['vmCpuAmount'])

        self.parser.add_option('--vm-disks-bus', dest='vmDisksBus', metavar='BUSTYPE',
                help='VM disks bus type defined for all disks. Overrides "disks-bus" '
                'element value defined in image manifest. '
                'Available types: %s. ' % ', '.join(Runner.DISKS_BUS_AVAILABLE) + 
                'If not provided, by default the value is taken from disks-bus '
                'element of image manifest. If the latter is not set, '
                'by default "%s" is assumed.' % Runner.DISKS_BUS_DEFAULT,
                default=defaultOptions['vmDisksBus'])

        MarketplaceUtil.addEndpointOption(self.parser)

        AuthnCommand.addCloudEndpointOptions(self.parser)

        super(Runnable, self).parse()

        options, self.args = self.parser.parse_args()
        self._assignOptions(defaultOptions, options)


    def _assignOptions(self, defaultOptions, options):
        obj = lambda: None
        Util.assignAttributes(obj, defaultOptions)
        Util.assignAttributes(obj, options.__dict__)
        self.options = obj


    def checkOptions(self):

        if self.options.listType:
            self.displayInstanceType()
 
        if self.options.instanceType is None:
            self.options.instanceType = self.getDefaultInstanceType;

        self._checkArgs()

        self.image = self.args[0]

        AuthnCommand.checkCloudEndpointOptionsOnly(self)

        self._checkKeyPair()

        if self.options.instanceType not in self.getAvailableInstanceTypes().keys():
            self.parser.error('Specified instance type not available')
        if self.options.extraContextFile and not os.path.isfile(self.options.extraContextFile):
            self.parser.error('Extra context file does not exist')
        if self.options.vncListen and not Util.validateIp(self.options.vncListen):
            self.parser.error('VNC listen IP is not valid')

        MarketplaceUtil.checkEndpointOption(self.options)

        super(Runnable, self).checkOptions()

    def _checkArgs(self):
        if len(self.args) != 1:
            self.parser.error('Please specify the machine image to start')

    def _checkKeyPair(self):
        if self.checkCredentials:
            if not self.options.userPublicKeyFile:
                self.parser.error('Unspecified user public key. See --key option.')

            self.options.userPrivateKeyFile = self.options.userPublicKeyFile.strip('.pub')

            for key in [self.options.userPublicKeyFile, self.options.userPrivateKeyFile]:
                if not os.path.isfile(key):
                    self.parser.error('Key `%s` does not exist' % key)

    def getDefaultInstanceType(self):
        try:
            return self.config['defaultInstanceType']
        except KeyError:
            return Runner.DEFAULT_INSTANCE_TYPE

    def getAvailableInstanceTypes(self):
        availableTypes = Runner.getDefaultInstanceTypes()
        userDefinedTypes = self.config['userDefinedInstanceTypes']

        availableTypes.update(userDefinedTypes)

        return availableTypes

    def displayInstanceType(self):
        types = self.getAvailableInstanceTypes()
        default = self.getDefaultInstanceType();

        columnSize = 10

        print ' '.ljust(1),
        print 'Type'.ljust(columnSize),
        print 'CPU'.rjust(columnSize),
        print 'RAM'.rjust(columnSize),
        print 'SWAP'.rjust(columnSize)
        for name, spec in types.items():
            if (name == default):
                flag = '*'
            else:
                flag = ' '
            cpu, ram, swap = spec
            print '%s %s %s %s %s' % (flag.ljust(1), 
                                      name.ljust(columnSize),
                                      ('%s CPU' % cpu).rjust(columnSize),
                                      ('%s MB' % ram).rjust(columnSize),
                                      ('%s MB' % swap).rjust(columnSize))
        sys.exit(0)
