from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath
from twisted.internet import defer
from zope.interface.verify import verifyClass


from simplebb.interface import IBuild
from simplebb.builder import Build



class BuildTest(TestCase):


    timeout = 1
    
    def test_IBuild(self):
        verifyClass(IBuild, Build)
    
    
    def test_doneDeferred(self):
        """
        A Build should have a done Deferred.
        """
        b = Build()
        self.assertTrue(isinstance(b.done, defer.Deferred))
    
    
    def test_attrs(self):
        """
        A Build should have the following attributes.
        """
        b = Build()
        self.assertEqual(b.uid, None)
        self.assertEqual(b.status, None)
        self.assertEqual(b.version, None)
        self.assertEqual(b.project, None)
        self.assertEqual(b.test_path, None)
        self.assertEqual(b.builder, None)
        self.assertEqual(b.runtime, None)
    
    
    def test_finish_0(self):
        """
        Finishing a build with 0 means the build succeeded.
        """
        b = Build()
        
        def cb_done(res):
            self.assertEqual(res, b)
        b.done.addCallback(cb_done)
        
        b._finish(0)
        self.assertEqual(b.status, 0)
        
        return b.done
    
    
    def test_finish_1(self):
        """
        Finishing a build with non-zero means the build failed.
        """
        b = Build()
        
        def cb_done(res):
            self.assertEqual(res, b)
        b.done.addCallback(cb_done)
        
        b._finish(1)
        self.assertEqual(b.status, 1)
        
        return b.done
    
    
    def test_run(self):
        """
        Build.run finished immediately by default
        """
        b = Build()

        def cb(res):
            self.assertEqual(res, b)
            self.assertEqual(b.status, None)
        b.done.addCallback(cb)
        
        b.run()
        return b.done        
        
        
        
        




