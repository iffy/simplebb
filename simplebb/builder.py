from zope.interface import implements
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder



class FileSystemBuilder:
    """
    I create and run FileBuilds found from my root directory.
    """
    
    implements(IBuilder)
    
    path = None

    
    def __init__(self, path=None):
        if isinstance(path, FilePath):
            self.path = path
        elif path is not None:
            self.path = FilePath(path)


    def requestBuild(self, version, project, test_path=None):
        """
        Find the build in the file system and start it.
        """