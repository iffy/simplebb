========
simplebb
========


simplebb manages running builds with a distributed network of builders.
Simple setup is the goal.  I wrote this because I couldn't get
Buildbot to do what I wanted.


Quick Start
===========

1. Get the code::

    $ git clone git@github.com:iffy/simplebb.git simplebb.git
    
2. Install dependencies::

    $ easy_install Twisted

3. Start a sample ``simplebb`` server::
    
    $ cd simplebb.git
    $ PYTHONPATH=. python example/server.py

4. Telnet to the server::

    $ telnet 127.0.0.1 9223

5. Request a build of the ``echo`` project::

    > build echo "Hello, world!"
    Build requested (failures not reported here)
    > quit

6. See that the build script was run::

    $ cat example/projects/_echo 
    Hello, world!

