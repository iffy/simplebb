"""
Utility functions
"""

import random
import hashlib
import time
import datetime


_idcount = 0

def generateId():
    """
    Returns a uniqueish id.
    """
    global _idcount
    _idcount += 1
    random_part = hashlib.sha256(str(random.getrandbits(256))).hexdigest()
    time_part = datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    num_part = str(_idcount)
    return hashlib.sha256(num_part + time_part + random_part).hexdigest()