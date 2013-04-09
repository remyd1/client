#!/usr/bin/python
#
# Created as part of the StratusLab project (http://stratuslab.eu),
# co-funded by the European Commission under the Grant Agreement
# INFSO-RI-261552.
#
# Copyright (c) 2012, Centre National de la Recherche Scientifique
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
# ${BUILD_INFO}
#

import cgi
import sys

sys.path.append('/var/lib/stratuslab/python')

from stratuslab.pat.Service import PortTranslationService

# Debug CGI
# http://docs.python.org/library/cgi.html#using-the-cgi-module
import cgitb
cgitb.enable()

if __name__ == '__main__':
    configFile = '/etc/stratuslab/stratuslab.cfg'
    if (len(sys.argv) > 1):
        configFile = sys.argv[1]
    service = PortTranslationService(configFile)
    service.run()

