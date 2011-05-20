from zope.interface import implements
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder
from simplebb.build import FileBuild



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
        
    
    def _findHeads(self, project, test_path=None):
        """
        Find the directory roots for a given project and test_path
        """
        project_fp = self.path.child(project)
        if project_fp.exists():
            if test_path:
                for child in project_fp.globChildren(test_path):
                    yield child
            else:
                yield project_fp

    
    def findBuilds(self, project, test_path=None):
        """
        Return a list of Builds that match the given criteria
        """
        
        def getFiles(root):
            if root.isfile():
                yield root
            elif root.isdir():
                for i in root.children():
                    if i.isfile():
                        yield i
                    elif i.isdir():
                        for x in getFiles(i):
                            yield x
        
        p = self.path.child(project)
        if p.exists():
            roots = [p]
            if test_path:
                roots = p.globChildren(test_path)
            for root in roots:
                for item in getFiles(root):
                    b = FileBuild(item)
                    b.project = project
                    b.builder = self
                    try:
                        tp = '/'.join(item.segmentsFrom(p))
                    except Exception, e:
                        tp = None
                    b.test_path = tp
                    yield b

