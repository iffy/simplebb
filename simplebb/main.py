from twisted.internet.protocol import Factory
from twisted.application import internet

from simplebb.server import RequestManager
from simplebb.builder import ProjectRepo
from simplebb.shell import ShellProtocol



class Glue:
    """
    I stick all the servers together.
    """
    
    requestManager = None
    
    
    def __init__(self):
        self.requestManager = RequestManager()
        self.services = []
    
    
    def addProjectRoot(self, path):
        """
        Choose the directory where build steps are defined for the projects.
        """
        self.requestManager.addBuilder(ProjectRepo(path))
    
    
    def useApplication(self, application):
        """
        Use the given twisted application for my services.
        """
        for service in self.services:
            service.setServiceParent(application)
    
    
    def startTelnetShell(self, port):
        """
        Start a shell on the given port that can be used to control/inspect
        this instance once it's running.
        """
        factory = Factory()
        factory.brain = self.requestManager
        factory.protocol = ShellProtocol
        service = internet.TCPServer(port, factory)
        self.services.append(service)
        







