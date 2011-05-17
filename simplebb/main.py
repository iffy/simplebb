
from simplebb.server import RequestManager
from simplebb.builder import ProjectRepo


class Glue:
    """
    I stick all the servers together.
    """
    
    requestManager = None
    
    
    def __init__(self):
        self.requestManager = RequestManager()
    
    
    def getServices(self):
        """
        Return the twisted.application services that should be started.
        """
        return []
    
    
    def addProjectRoot(self, path):
        """
        Choose the directory where build steps are defined for the projects.
        """
        self.requestManager.addBuilder(ProjectRepo(path))
    
    
    def useApplication(self, application):
        """
        Use the given twisted application for my services.
        """
        for service in self.getServices():
            service.setServiceParent(application)