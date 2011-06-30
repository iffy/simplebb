"""
Messaging stuff goes in here
"""

import datetime

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





