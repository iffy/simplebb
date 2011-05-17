
from simplebb.builder import ProjectRepo


class RequestManager:
    """
    I handle requests to build things and return responses
    places.
    """
    
    projectRepo = None
    
    
    def __init__(self, project_root=None):
        if project_root:
            self.projectRepo = ProjectRepo(project_root)