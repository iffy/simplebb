from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath
from twisted.internet import defer
from zope.interface.verify import verifyClass


from simplebb.interface import IBuild
from simplebb.builder import Build, FileBuild, FILE_NOT_FOUND, MISSING_VERSION



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



class FileBuildTest(TestCase):
    
    
    timeout = 0.5
    
    
    def test_IBuild(self):
        verifyClass(IBuild, FileBuild)

    
    def test_initPath(self):
        """
        Initializing with a string path will set the _filepath attribute
        """
        b = FileBuild('foo')
        self.assertEqual(b._filepath, FilePath('foo'))
    
    
    def test_initFilePath(self):
        """
        Init should handle a FilePath
        """
        p = FilePath('foo')
        b = FileBuild(p)
        self.assertEqual(b._filepath, p)
        
    
    def test_run(self):
        """
        Running should execute the given file.        
        """
        f = FilePath(self.mktemp())
        f.setContent('#!/bin/bash\nexit 12')
        
        b = FileBuild(f)
        b.version = 'foo'
        
        def cb(build):
            self.assertEqual(build, b)
            self.assertEqual(build.status, 12)
        b.done.addCallback(cb)
        
        b.run()
        return b.done
    
    
    def test_run_noVersion(self):
        """
        If no version is supplied, the build will fail with MISSING_VERSION
        """
        f = FilePath(self.mktemp())
        f.setContent('#!/bin/bash\nexit 11')
        
        b = FileBuild(f)
        
        def cb(build):
            self.assertEqual(build, b)
            self.assertEqual(build.status, MISSING_VERSION)
        b.done.addCallback(cb)
        
        b.run()
        return b.done
    
    
    def test_run_noFile(self):
        """
        If a file does not exit, fail with FILE_NOT_FOUND
        """
        b = FileBuild('hey')
        b.version = 'foo'
        
        def cb(build):
            self.assertEqual(build, b)
            self.assertEqual(build.status, FILE_NOT_FOUND)
        b.done.addCallback(cb)
        
        b.run()
        return b.done
        
        
        








