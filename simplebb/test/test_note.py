from twisted.trial.unittest import TestCase
from twisted.internet.task import Clock
from twisted.internet import reactor

from simplebb.note import Notary, notary, NoteTaker



class notaryTest(TestCase):


    def test_isNotary(self):
        self.assertTrue(isinstance(notary, Notary))



class NotaryTest(TestCase):


    def test_create(self):
        """
        A newly created note has a unique id
        """
        g = Notary()
        note = g.create()
        self.assertNotEqual(note['uid'], None)
        self.assertNotEqual(note['time'], None)
        self.assertEqual(note['kind'], None)
        
        note2 = g.create()
        self.assertNotEqual(note['uid'], note2['uid'])


    def test_createBuildRequest(self):
        """
        Should use the result of create and add the build request attributes. 
        """
        g = Notary()
        d = {}
        g.create = lambda: d
        
        note = g.createBuildRequest('project', 'version')
        
        self.assertEqual(note, d, "Should use the result of create")
        self.assertEqual(note['kind'], 'buildreq')
        self.assertEqual(note['project'], 'project')
        self.assertEqual(note['version'], 'version')
        self.assertEqual(note['testpath'], None)


    def test_createBuildRequest_testpath(self):
        """
        A third argument can be a test path
        """
        g = Notary()
        
        note = g.createBuildRequest('project', 'version', 'foo')
        self.assertEqual(note['testpath'], 'foo')


    def test_createBuildResponse(self):
        """
        You can create notes regarding build progress.
        """
        n = Notary()
        original = n.create()
        
        d = {}
        n.create = lambda: d
        
        build_info = {}
        
        note = n.createBuildResponse(original, build_info, 'a note')
        self.assertEqual(note['request_id'], original['uid'])
        self.assertEqual(note['build'], build_info)
        self.assertEqual(note['kind'], 'response')
        self.assertEqual(note['note'], 'a note')
        self.assertEqual(note, d, "should use Notary.create")


    def test_createBuildInfo(self):
        """
        You can create notes describing builds
        """
        n = Notary()
        
        d = {}
        n.create = lambda: d
        
        note = n.createBuildInfo('bob', 'proj', 'version', 'tp')
        self.assertEqual(note, d, "should use Notary.create")
        self.assertEqual(note['kind'], 'build')
        self.assertEqual(note['builder'], 'bob')
        self.assertNotEqual(note['build_id'], None)
        self.assertEqual(note['project'], 'proj')
        self.assertEqual(note['version'], 'version')
        self.assertEqual(note['testpath'], 'tp')



class NoteTakerTest(TestCase):


    def test_attrs(self):
        """
        Should have the following attributes.
        """
        nt = NoteTaker()
        self.assertEqual(nt.reactor, reactor)
        self.assertTrue(nt.forgetInterval >= 60*60, "Default forget should be"
            "longer than an hour.")

    def test_receiveNote(self):
        """
        receiveNote should call noteReceived in the default configuration
        """
        nt = NoteTaker()
        nt.reactor = Clock()
        called = []
        nt.noteReceived = called.append
        
        n = notary.create()
        nt.receiveNote(n)
        
        self.assertEqual(called, [n])
        
        nt.receiveNote(n)
        self.assertEqual(called, [n], "Should not receive the same note again")
        
        nt.reactor.advance(nt.forgetInterval+1)


    def test_expire(self):
        """
        receiveNote forgets what it received after forgetInterval
        """
        nt = NoteTaker()
        nt.reactor = Clock()
        nt.forgetInterval = 10
        called = []
        nt.noteReceived = called.append
        n = notary.create()
        
        nt.receiveNote(n)
        self.assertEqual(called, [n])
        
        nt.reactor.advance(9)
        nt.receiveNote(n)
        self.assertEqual(called, [n])
        
        nt.reactor.advance(2)
        nt.receiveNote(n)
        self.assertEqual(called, [n, n], 'After expiry, notes should be '
            'received again.')



