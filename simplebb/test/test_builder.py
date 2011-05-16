from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath
from twisted.internet import defer


from simplebb.builder import FileBuild, Build
from simplebb.builder import FileNotFoundError



class BuildTest(TestCase):

    timeout = 1
    
    
    def test_doneDeferred(self):
        """
        A Build should have a done Deferred.
        """
        b = Build()
        self.assertTrue(isinstance(b.done, defer.Deferred))
    
    
    def test_status(self):
        b = Build()
        self.assertEqual(b.status, None)
    
    
    def test_finish_0(self):
        """
        Finishing a build with 0 means the build succeeded.
        """
        b = Build()
        
        def cb_done(res):
            self.assertEqual(res, b)
        b.done.addCallback(cb_done)
        
        b.finish(0)
        self.assertEqual(b.status, 0)
        
        return b.done
    
    
    def test_finish_1(self):
        """
        Finishing a build with non-zero means the build failed.
        """
        b = Build()
        
        def eb_done(res):
            self.assertEqual(res.value, b)
        def cb_done(res):
            self.fail("Should errback, not callback")
        b.done.addCallbacks(cb_done, eb_done)
        
        b.finish(1)
        self.assertEqual(b.status, 1)
        
        return b.done
    
    
    def test_run(self):
        """
        Build.run is meant to be overwritten
        """
        b = Build()
        self.assertRaises(NotImplementedError, b.run)



class FileBuildTest(TestCase):
    
    timeout = 3
    
    
    def test_subClass(self):
        self.assertTrue(issubclass(FileBuild, Build),
            "FileBuild should subclass Build")

    
    def test_initFilename(self):
        """
        Should save the initialized filename as a FilePath
        """
        f = self.mktemp()
        fb = FileBuild(f)
        self.assertEqual(fb.path, FilePath(f))
    
    
    def test_initFilePath(self):
        """
        Should save a given FilePath as as the path
        """
        f = FilePath(self.mktemp())
        fb = FileBuild(f)
        self.assertEqual(fb.path, f)
    
    
    def test_run(self):
        """
        The file should be run and the result returned.
        """
        f = FilePath(self.mktemp())
        f.setContent('#!/bin/bash\nexit 0\n')
        f.chmod(0777)
        
        fb = FileBuild(f)
        def cb(res):
            self.assertEqual(res.status, 0)
        fb.done.addCallback(cb)
        
        fb.run()
        
        return fb.done


    def test_run_dne(self):
        """
        A file that does not exist can not be run
        """
        f = FilePath(self.mktemp())
        f.makedirs()
        fb = FileBuild(f.child('foo'))
        self.assertRaises(FileNotFoundError, fb.run)


        
        
    
    
    



        
