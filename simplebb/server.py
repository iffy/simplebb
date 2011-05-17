
from simplebb.builder import ProjectRepo


class RequestManager:
    """
    I handle requests to build things and return responses
    places.
    """
    
    
    def __init__(self, project_root=None):
        self.builders = []
        if project_root:
            self.builders.append(ProjectRepo(project_root))
    
    
    def buildProject(self, project, version, test=None):
        """
        Request that this guy build a project.
        """
        for builder in self.builders:
            builder.buildProject(project, version, test)


