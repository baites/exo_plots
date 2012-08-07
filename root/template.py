#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 15, 2012
Copyright 2012, All rights reserved
'''

import os

from root import tfile
import ROOT

class Loader(object):
    '''
    Load histograms from ROOT file.

    The processing of each plot and found directory should be defined by child
    classes by overriding process_plot and process_dir methods
    '''

    def __init__(self):
        pass

    def load(self, filename):
        '''Check if file exists and load plots from it'''

        if not os.path.exists(filename):
            raise RuntimeError("input file does not exit: " + filename)

        with tfile.topen(filename) as input_:
            self._load(input_)

    def process_plot(self, hist):
        '''Called whenever a plot is loaded from file'''

        pass

    def _load(self, dir_):
        '''The loader back-end'''

        for key in dir_.GetListOfKeys():
            obj = dir_.Get(key.GetName())
            if not obj:
                continue

            if isinstance(obj, ROOT.TH1):
                self.process_plot(obj)

            elif isinstance(obj, ROOT.TDirectory):
                self._load(obj)
