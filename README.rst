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

3. See the build script that will take what ever version you want to build
   and append that version to ``example/project/_echo``::

    $ cat example/project/echo

4. Start a sample ``simplebb`` server::
    
    $ cd simplebb.git
    $ PYTHONPATH=. python example/server.py

5. From another terminal, telnet to the server::

    $ telnet 127.0.0.1 9223

6. Request some builds of the ``echo`` project::

    > build echo "Hello, world!"
    Build requested: 2fa067baeec87928717906efdba550e26d6d0ee8fbc727db1a2f7a7d896283cf
    > build echo another  
    Build requested: 6ec610b90b7a60cfd1f0b8d8d393d657bbc535e65885282c9bb9f01735110769
    > quit

7. See that the build script was run::

    $ cat example/projects/_echo 
    built echo project version Hello, world!
    built echo project version another


What makes simplebb cool?
=========================

Everything is a builder
-----------------------

The server is a builder, the client is a builder, the build-step executer is a
builder.  Some builders simply pass on build requests to other builders.  Others
execute scripts.


It's distributed
----------------

If you connect a builder to a receive build requests from a remote builder,
the local builder is responsible for acquiring code and defining build steps.
You can report the results to the remote builder but you don't have to. If 
you're in QA, you could make a builder that fails every build.



