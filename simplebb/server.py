
from simplebb.builder import ProjectRepo


class RequestManager:
    """
    I handle requests to build things and return responses
    places.
    """
    
    
    def __init__(self, project_root=None):
        self.builders = []
        if project_root:
            self.addBuilder(ProjectRepo(project_root))
    
    
    def buildProject(self, project, version, test=None):
        """
        Request that this guy build a project.
        """
        for builder in self.builders:
            builder.buildProject(project, version, test)
    
    
    def addBuilder(self, builder):
        """
        Adds a builder to this request manager
        """
        if builder not in self.builders:
            self.builders.append(builder)
    
    
    def removeBuilder(self, builder):
        """
        Removes a builder from this request manager (so that requests
        are no longer passed along)
        """
        if builder in self.builders:
            self.builders.remove(builder)





