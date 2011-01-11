from twisted.protocols import amp
from simplebb.commands import SuggestBuild
from twisted.internet.protocol import ClientCreator
from twisted.internet import reactor, utils, defer
from optparse import OptionParser
import sys
import re

class Client:  
    conn = None
    proto = amp.AMP
    
    def connect(self, host, port=7900):
        d1 = ClientCreator(reactor, self.proto).connectTCP(host, port)
        d1.addCallback(self._connected)
        return d1
    
    def _connected(self, conn):
        self.conn = conn
        return self
    
    def suggestBuild(self, projectName, revision):
        d = self.conn.callRemote(SuggestBuild, projectName=projectName, revision=revision)
        return d

def getRevisions():
    """
    Reads revisions from stdin
    """
    while True:
        line = sys.stdin.readline()
        if not line or not line.strip():
            break
        
        try:
            oldrev, newrev, refname = line.split(None, 2)
        except:
            continue
        
        print line
        
        # We only care about regular heads, i.e. branches
        m = re.match(r'^refs\/heads\/(.+)$', refname)
        if not m:
            continue
        
        branch = m.group(1)
        
        # updated/created/deleted ?
        if re.match(r'^0*$', newrev):
            # deleted
            continue
        elif re.match(r'^0*$', oldrev):
            # created
            yield branch
        else:
            # updated
            yield branch


def main(projectName, revisions=[], host='127.0.0.1'):
    c = Client()
    queue = []
    def done(ign):
        reactor.stop()
    def cb(c):
        if revisions:
            for revision in revisions:
                queue.append(c.suggestBuild(projectName, revision))
        else:
            # look in stdin
            for branch in getRevisions():
                print 'branch', branch
                queue.append(c.suggestBuild(projectName, branch))
        d = defer.gatherResults(queue)
        return d
    c.connect(host).addCallback(cb).addBoth(done)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-H', '--host', dest='host', default='127.0.0.1', help='Host of simplebb server')
    parser.add_option('-r', '--rev', dest='revision', default=None, help='Specific revision to suggest -- otherwise stdin will list them')
    options, args = parser.parse_args()
    if len(args) < 1:
        parser.error('you must include the project name')
    revisions = []
    if len(args) > 1:
        revisions = args[1:]
    elif options.revision:
        revisions = [options.revision]
    main(args[0], revisions, options.host)
    reactor.run()


