import datetime

from zope.interface import implements
from twisted.python.filepath import FilePath
from twisted.internet import reactor, protocol, defer

from simplebb.interface import IBuilder, IPublisher
from simplebb.note import Note

import json


class BuildProtocol(protocol.ProcessProtocol):
    
    
    def __init__(self):
        self.done = defer.Deferred()


    def processEnded(self, status):
        self.done.callback(status.value.exitCode)



class FileBuilder:
    """
    I create and run FileBuilds found from my root directory.
    """
    
    implements(IBuilder, IPublisher)
    
    name = None
    path = None

    
    def __init__(self, path=None):
        self._subscribed = []
        if isinstance(path, FilePath):
            self.path = path
        elif path is not None:
            self.path = FilePath(path)


    def findScript(self, project):
        """
        Given a project name, return the script that should be executed
        to build this project.
        """
        return self.path.child(project)


    def _getNote(self, request, body):
        note = Note()
        note.build_uid = request.uid
        note.builder = self.name
        note.project = request.project
        note.version = request.version
        note.body = json.dumps(body)
        return note


    def build(self, request):
        """
        Build the request.
        """
        script = self.findScript(request.project)
        if not script:
            return
        proto = BuildProtocol()
        reactor.spawnProcess(proto, script.path, args=[script.path])
        
        note = self._getNote(request, {'event': 'start'})
        self.publish(note)
        
        def cb(status, request):
            note = self._getNote(request, {'event': 'end', 'status': status})
            self.publish(note)
            return status
        return proto.done.addCallback(cb, request)


    def subscribe(self, func):
        self._subscribed.append(func)


    def unsubscribe(self, func):
        if func in self._subscribed:
            self._subscribed.remove(func)


    def publish(self, note):
        for s in self._subscribed:
            s(note)










