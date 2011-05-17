from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath


from simplebb.server import RequestManager
from simplebb.builder import ProjectRepo


class RequestManagerTest(TestCase):
    
    
    def test_basic(self):
        """
        It should have these attributes.
        """
        r = RequestManager()
        self.assertEqual(r.projectRepo, None)

    
    def test_initWithRepo(self):
        """
        You should be able to initialize with a path to a project repo
        """
        f = FilePath(self.mktemp())
        r = RequestManager(project_root=f.path)
        self.assertTrue(isinstance(r.projectRepo, ProjectRepo))
        self.assertEqual(r.projectRepo.path, f)