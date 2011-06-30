from twisted.trial.unittest import TestCase


from simplebb.note import Notary



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
        You can create notes about builds.
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



