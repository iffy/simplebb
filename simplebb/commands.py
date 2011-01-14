from twisted.protocols import amp

#------------------------------------------------------------------------------
# client to server
#------------------------------------------------------------------------------
class SendResult(amp.Command):
    arguments = [
        ('projectName', amp.String()),
        ('revision', amp.String()),
        ('specs', amp.String()),
        ('returnCode', amp.Integer()),
    ]
    response = []

class Identify(amp.Command):
    arguments = [
        ('kind', amp.String()),
        ('name', amp.String()),
    ]
    response = []


#------------------------------------------------------------------------------
# either
#------------------------------------------------------------------------------
class SuggestBuild(amp.Command):
    arguments = [
        ('projectName', amp.String()),
        ('revision', amp.String()),
    ]
    response = []


#------------------------------------------------------------------------------
# server to client
#------------------------------------------------------------------------------
class SendStatus(amp.Command):
    arguments = [
        ('projectName', amp.String()),
        ('revision', amp.String()),
        ('builderName', amp.String()),
        ('returnCode', amp.Integer()),
    ]
    response = []

