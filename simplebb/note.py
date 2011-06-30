"""
Messaging stuff goes in here
"""

import datetime

from twisted.internet import reactor

from simplebb.util import generateId



class Notary:
    """
    I make and interpret note dicts
    """
    
    def create(self):
        """
        Return a standard note dict.
        """
        return {
            'uid': generateId(),
            'time': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S %f%Z'),
            'kind': None
        }


    def createBuildRequest(self, project, version, testpath=None):
        """
        Return a build request note.
        """
        note = self.create()
        note.update({
            'kind': 'buildreq',
            'project': project,
            'version': version,
            'testpath': testpath,
        })
        return note


    def createBuildInfo(self, builder, project, version, testpath):
        """
        Return a build info note
        """
        ret = self.create()
        ret.update({
            'kind': 'build',
            'builder': 'bob',
            'build_id': generateId(),
            'project': project,
            'version': version,
            'testpath': testpath,
        })
        return ret


    def createBuildResponse(self, request, buildinfo, note):
        """
        Return a build response note.
        
        @param request: The note that initiated this build request.
        """
        ret = self.create()
        ret.update({
            'kind': 'response',
            'request_id': request['uid'],
            'build': buildinfo,
            'note': note,
        })
        return ret



notary = Notary()



class NoteTaker:
    """
    I take notes.
    """
    
    reactor = reactor
    
    forgetInterval = 3600
    
    
    def __init__(self):
        self.received = set([])


    def receiveNote(self, note):
        """
        Someone else has given me a note.
        """
        if note['uid'] in self.received:
            return
        self.received.add(note['uid'])
        self.reactor.callLater(self.forgetInterval,
                               self.received.remove, note['uid'])
        
        self.noteReceived(note)




