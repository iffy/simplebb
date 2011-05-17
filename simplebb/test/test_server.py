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
        self.assertEqual(r.builders, [])

    
    def test_initWithRepo(self):
        """
        You should be able to initialize with a path to a project repo
        """
        f = FilePath(self.mktemp())
        r = RequestManager(project_root=f.path)
        self.assertEqual(len(r.builders), 1)
        
        pr = r.builders[0]
        self.assertTrue(isinstance(pr, ProjectRepo))
        self.assertEqual(pr.path, f)
    
    
    def test_buildProject(self):
        """
        buildProject should tell the projectRepo to build
        """
        pr = ProjectRepo()
        called = []
        def f(project, version, test):
            called.append((project, version, test))
        pr.buildProject = f
        
        r = RequestManager()
        r.builders = [pr]
        
        r.buildProject('project', 'version', 'test')
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], ('project', 'version', 'test'))



