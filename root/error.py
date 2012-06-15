#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Feb 24, 2012
Copyright 2011, All rights reserved
'''

from __future__ import division, print_function

import math

def add(hist, percent):
    '''
    Add error to the bin contnet. The error is specified as a percent of the
    bin content.
    '''

    # Add in quadrature the % * bin_content to the bin error
    for bin_ in range(1, hist.GetNbinsX() + 1):
        hist.SetBinError(bin_,
                         math.sqrt(hist.GetBinError(bin_) ** 2 +
                                   (hist.GetBinContent(bin_) * percent) ** 2))
