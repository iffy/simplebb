from zope.interface import Interface, Attribute



class IBuildRequest(Interface):
    """
    I am a BuildRequest
    """
    
    uid = Attribute('''
        A unique identifier for this BuildRequest
        ''')
    
    project = Attribute('''
        Project name to build
        ''')
    
    version = Attribute('''
        Version string.
        ''')



class INote(Interface):
    """
    I am information about a build
    """
    
    uid = Attribute('''
        A unique indentifier for this Note
        ''')
    
    build_uid = Attribute('''
        The BuildRequest.uid that spawned this note.
        ''')

    project = Attribute('''
        Project name being built
        ''')

    version = Attribute('''
        Version being built
        ''')
    
    body = Attribute('''
        The body of the note.
        ''')


