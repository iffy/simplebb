import datetime

from zope.interface import implements
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder



class FileBuilder:
    """
    I create and run FileBuilds found from my root directory.
    """
    
    implements(IBuilder)
    
    name = None
    path = None

    
    def __init__(self, path=None):
        if isinstance(path, FilePath):
            self.path = path
        elif path is not None:
            self.path = FilePath(path)











