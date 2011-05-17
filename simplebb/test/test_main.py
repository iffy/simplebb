from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath

from twisted.internet.protocol import Factory

from simplebb.main import Glue
from simplebb.server import RequestManager
from simplebb.builder import ProjectRepo
from simplebb.shell import ShellProtocol


class GlueTest(TestCase):
    
    
    def test_init(self):
        """
        Should have a RequestManager if nothing else
        """
        g = Glue()
        self.assertTrue(isinstance(g.requestManager, RequestManager))
    
    
    def test_services(self):
        """
        Should return [] by default
        """
        g = Glue()
        self.assertEqual(g.services, [])
    
    
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
        call setServiceParent on each service
        """
        class FakeService:
            def __init__(self):
                self.called = []
            def setServiceParent(self, application):
                self.called.append(application)
        
        g = Glue()
        g.services = [FakeService(), FakeService()]
        
        o = object()
        g.useApplication(o)
        
        self.assertEqual(g.services[0].called, [o])
        self.assertEqual(g.services[1].called, [o])
    
    
    def test_startTelnetShell(self):
        """
        You can have shell access via telnet with startTelnetShell
        """
        g = Glue()
        g.startTelnetShell(5678)
        
        self.assertEqual(len(g.services), 1)
        
        service = g.services[0]
        port = service.args[0]
        self.assertEqual(port, 5678)
        
        factory = service.args[1]
        self.assertEqual(factory.brain, g.requestManager)
        self.assertEqual(factory.protocol, ShellProtocol) 






