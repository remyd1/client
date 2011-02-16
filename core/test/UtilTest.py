#
# Created as part of the StratusLab project (http://stratuslab.eu),
# co-funded by the European Commission under the Grant Agreement
# INFSO-RI-261552."
#
# Copyright (c) 2010, SixSq Sarl
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
import unittest
import os
import sys

import stratuslab.Util as Util

class UtilTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAppendOrReplaceMultilineBlockInString(self):
        self.assertEqual(Util.appendOrReplaceMultilineBlockInString('', ''), '')

        content = """
line one
line two
#
"""
        data = """
start block
  block LINE ONE
"""
        result = """
line one
line two
#

start block
  block LINE ONE

"""
        self.assertEqual(Util.appendOrReplaceMultilineBlockInString(content, data), 
                         result)

        content = """
line one
start block
  block line 1
  block line 2

#
"""
        result = """
line one
start block
  block LINE ONE

#
"""
        self.assertEqual(Util.appendOrReplaceMultilineBlockInString(content, data), 
                         result)

        content = """
line one
start block
  block line 1
  block line 2
"""
        result = """
line one
start block
  block LINE ONE

"""
        self.assertEqual(Util.appendOrReplaceMultilineBlockInString(content, data), 
                         result)

    def testExecuteWithOutput(self):
        output = Util.execute('ls -l'.split(), withOutput=True)

        self.assertEquals(type(output), tuple)
        self.assertEquals(len(output), 2)
        self.assertTrue(isinstance(output[1], basestring))
        assert len(output[1]) >= 1
    
    def testGatewayIpFromNetAddress(self):
        self.assertEquals(Util.gatewayIpFromNetAddress('0.0.0.0'), '0.0.0.1')
        
        
    def testConstructEndPoint(self):
        self.assertEquals(Util.constructEndPoint('protocol://address:1234/path'), 'protocol://address:1234/path')
        self.assertEquals(Util.constructEndPoint('address', 'protocol', '1234', 'path'), 'protocol://address:1234/path')
    
if __name__ == "__main__":
    unittest.main()
