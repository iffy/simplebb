from zope.interface import implements
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder
from simplebb.build import FileBuild



class ReportableMixin:
    """
    Mix me in if you want to have the reporting part of the IBuilder
    interface.
    """


    def __init__(self):
        self._reporters = []
    
    
    def addReporter(self, reporter):
        """
        Add a reporter so that Build events will be given to the reporter.
        """
        if reporter not in self._reporters:
            self._reporters.append(reporter)
    
    
    def removeReporter(self, reporter):
        """
        Removes a reporter so it won't be notified anymore about Build events.
        """
        try:
            self._reporters.remove(reporter)
        except ValueError:
            pass



class FileBuilder(ReportableMixin):
    """
    I create and run FileBuilds found from my root directory.
    """
    
    implements(IBuilder)
    
    name = None
    
    uid = None
    
    path = None

    
    def __init__(self, path=None):
        ReportableMixin.__init__(self)
        
        self.builds = []
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
    
    
    def _getChildFiles(self, root):
        """
        Given the root file/directory, return all the file descendents
        """
        if root.isdir():
            for child in root.walk():
                if child.isfile():
                    yield child
        else:
            yield root

    
    def findBuilds(self, project, test_path=None):
        """
        Return a list of FileBuilds that match the given criteria
        """
        project_root = list(self._findHeads(project))
        if not project_root:
            return
        project_prefix = len(project_root[0].path) + 1
        
        heads = self._findHeads(project, test_path)
        for head in heads:
            for child in self._getChildFiles(head):
                # find test_path
                b = FileBuild(child)
                b.project = project
                b.test_path = child.path[project_prefix:]
                b.builder = self
                yield b











