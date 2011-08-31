from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject

from simplebb.interface import IBuildRequest, INote
from simplebb.note import BuildRequest, Note



class BuildRequestTest(TestCase):


    def test_IBuildRequest(self):
        verifyClass(IBuildRequest, BuildRequest)
        verifyObject(IBuildRequest, BuildRequest())


    def test_uid_unique(self):
        a, b = BuildRequest(), BuildRequest()
        self.assertNotEqual(a.uid, b.uid)


    def test_init(self):
        """
        You can init with project name and version
        """
        r = BuildRequest('project', 'version')
        self.assertEqual(r.project, 'project')
        self.assertEqual(r.version, 'version')


    def test_init_uid(self):
        """
        You can init with a uid
        """
        r = BuildRequest(uid='foo')
        self.assertEqual(r.uid, 'foo')



class NoteTest(TestCase):


    def test_INote(self):
        verifyClass(INote, Note)
        verifyObject(INote, Note())


    def test_uid_unique(self):
        a, b = Note(), Note()
        self.assertNotEqual(a.uid, b.uid)



