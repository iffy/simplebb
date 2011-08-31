"""
Notes live in here.
"""

import hashlib
import random

from simplebb.interface import IBuildRequest, INote
from zope.interface import implements



class BuildRequest:
    """
    I am a request to build a certain version of a project.
    """
    
    implements(IBuildRequest)
    
    uid = None
    project = None
    version = None

    def __init__(self, project=None, version=None, uid=None):
        self.uid = uid or hashlib.sha256(hex(random.getrandbits(256)) + \
                                         repr(id([])))
        self.project = project
        self.version = version



class Note:
    """
    I have some information about a build
    """
    
    implements(INote)
    
    uid = None
    body = None
    
    build_uid = None
    project = None
    version = None


    def __init__(self):
        self.uid = hashlib.sha256(hex(random.getrandbits(256)) + \
                                  repr(id([])))





