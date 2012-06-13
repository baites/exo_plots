#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Feb 16, 2012
Copyright 2011, All rights reserved
'''

from __future__ import print_function

import ROOT

class topen(object):
    '''
    Context manager for ROOT TFile
    
    Opening/closing file is automatically done, e.g.:

        with topen("input.root") as input_:
            plot = input_.Get("hello")

    the above code is equivalent to:

        input_ = ROOT.TFile("input.root")
        if not input_.IsZombie():
            plot = input_.Get("hello")

            input_.Close()
    '''

    def __init__(self, filename, mode = "readonly"):
        self._filename = filename
        self._file = None
        self._mode = mode

    def __enter__(self):
        '''
        Context management entry point
        '''

        if not self._file:
            self._file = ROOT.TFile.Open(self._filename, self._mode)
            if self._file.IsZombie():
                self._file = None

                raise RuntimeError("failed to open file "
                                   "{0!r}".format(self._filename))

        return self._file

    def __exit__(self, error_type, error_value, error_traceback):
        '''
        Exit the context management
        '''

        if not error_type and self._file:
            self._file.Close()
            self._file = None

if "__main__" == __name__:
    import sys

    if 2  == len(sys.argv):
        with topen(sys.argv[1]) as in_file:
            print("Successfully opened file " + in_file.GetName())

        with topen("nonexisting_file.root") as in_file:
            print("file is open " + in_file.GeName())
    else:
        print("input file is missing", file=sys.stderr)
