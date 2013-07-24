#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2013 Marcos Dione <mdione@grulic.org.ar>
# for licensing details see the file LICENSE.txt

import os
import sys
import sh
import importlib
import builtins

class CommandWrapper (sh.Command):
    # this class changes the behaviour of sh.Command
    # so is more shell scripting freindly
    def __call__ (self, *args, **kwargs):
        # if _out or _err are not provided, connect them to the original ones
        if not '_out' in kwargs:
            kwargs['_out']= sys.stdout.buffer

        super ().__call__ (*args, **kwargs)

def polute (d):
    # these functions will be loaded from each module and put in the globals
    builtins= {
        'os': [ 'chdir', 'getcwd', 'uname', 'chmod', 'chown', 'link', 'listdir',
                'mkdir', 'remove' ],
        'time': [ 'sleep', ],
        'sys': [ 'argv', 'exit' ],

        'ayrton.file_test': [ '_a', '_b', '_c', '_d', '_e', '_f', '_g', '_h',
                              '_k', '_p', '_r', '_s', '_u', '_w', '_x', '_L',
                              '_N', '_S', '_nt', '_ot' ],
        'ayrton.expansion': [ 'bash', ],
        }

    for module, functions in builtins.items ():
        m= importlib.import_module (module)
        for function in functions:
            d[function]= getattr (m, function)

    for std in ('stdin', 'stdout', 'stderr'):
        d[std]= getattr (sys, std).buffer

class Globals (dict):
    def __init__ (self):
        super ().__init__ ()
        polute (self)

    def __getitem__ (self, k):
        try:
            ans= getattr (builtins, k)
        except AttributeError:
            try:
                ans= super ().__getitem__ (k)
            except KeyError:
                ans= CommandWrapper._create (k)

        return ans

if __name__=='__main__':
    s= compile (open (sys.argv[1]).read (), sys.argv[1], 'exec')
    g= Globals ()
    # l= os.environ.copy ()

    # remove ayrton from the arguments
    sys.argv.pop (0)

    # fire!
    exec (s, g)