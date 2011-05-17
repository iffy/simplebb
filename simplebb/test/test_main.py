from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath


from simplebb.main import Glue
from simplebb.server import RequestManager
from simplebb.builder import ProjectRepo


class GlueTest(TestCase):
    
    
    def test_init(self):
        """
        Should have a RequestManager if nothing else
        """
        g = Glue()
        self.assertTrue(isinstance(g.requestManager, RequestManager))
    
    
    def test_getServices(self):
        """
        Should return [] by default
        """
        g = Glue()
        self.assertEqual(list(g.getServices()), [])
    
    
    def test_addProjectRoot(self):
        """
        You should be able to set the project root
        """
        g = Glue()
        g.addProjectRoot('foo')
        self.assertEqual(len(g.requestManager.builders), 1)
        builder = g.requestManager.builders[0]
        self.assertTrue(isinstance(builder, ProjectRepo))
        self.assertEqual(builder.path, FilePath('foo'))
    
    
    def test_useApplication(self):
        """
        call setServiceParent on each getServices
        """
        class FakeService:
            def __init__(self):
                self.called = []
            def setServiceParent(self, application):
                self.called.append(application)
        
        g = Glue()
        services = [FakeService(), FakeService()]
        g.getServices = lambda: services
        
        o = object()
        g.useApplication(o)
        
        self.assertEqual(services[0].called, [o])
        self.assertEqual(services[1].called, [o])






