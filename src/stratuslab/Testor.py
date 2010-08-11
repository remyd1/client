from stratuslab.CloudConnectorFactory import CloudConnectorFactory
from stratuslab.Util import fileGetContent
from stratuslab.Util import printAction
from stratuslab.Util import printError
from stratuslab.Util import printStep

class Testor(object):
    
    def __init__(self, config, options):
        self.config = config
        self.options = options

        self.cloud = CloudConnectorFactory.getCloud()
        self.cloud.setFrontend(self.config.get('frontend_ip'),
                               self.config.get('one_port'))
        self.cloud.setCredentials(self.config.get('one_username'),
                                  self.config.get('one_password'))
        
        # Attributes initialization
        self.vmTemplate = None
        self.vmId = None
        
        
    def runTests(self):
        printAction('Launching smoke test')
        
        printStep('Starting VM')
        self.startVmTest()
        
        printStep('Shutting down VM')
        self.stopVmTest()

        printAction('Smoke test finished')
    
    def buildVmTemplate(self):
        self.vmTemplate = fileGetContent(self.options.vmTemplate) % self.config
    
    def startVmTest(self):
        self.buildVmTemplate()
        self.vmId = self.cloud.vmStart(self.vmTemplate)
        
        vmStarted = self.cloud.waitUntilVmRunningOrTimeout(self.vmId, 120)
            
        if not vmStarted:
            printError('Failing to start VM')
        
    def stopVmTest(self):
        vmStopped = self.cloud.vmStop(self.vmId)
        
        if not vmStopped:
            printError('Failing to stop VM')
