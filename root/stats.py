#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jul 07, 2012
Copyright 2012, All right reserved
'''

from __future__ import division

import ROOT

def efficiency(hist, invert=False, normalize=True):
    '''
    Calculate histogram efficiency

    the efficiency is defined as:

        eff = Integral(hist, X, max) / Integral(hist, min, max)

    or it's inverted counterpart:

        eff = Integral(hist, min, X) / Integral(hist, min, max)
    '''

    clone_ = hist.Clone()
    clone_.Reset()

    error_ = ROOT.Double()
    bins_ = hist.GetNbinsX()
    for bin_ in range(1, bins_ + 1):
        if invert:
            clone_.SetBinContent(bin_, hist.IntegralAndError(bin_,
                                                             bins_ + 1, error_))
        else:
            clone_.SetBinContent(bin_, hist.IntegralAndError(0, bin_, error_))

        clone_.SetBinError(bin_, error_)

    if normalize:
        clone_.Scale(1 / hist.Integral())

    return clone_

def find_maximum(hist):
    '''
    Return the "Y + error" for the bin with maximum
    
    WARNING: the true maximum value might be incorrect especially in the case
             of bins with low stats and large errors; scan manually bin by bin
             in these cases
    '''

    bin_ = hist.GetMaximumBin()
    return hist.GetBinContent(bin_) + hist.GetBinError(bin_)

def maximum(hists=[], stacks=[]):
    '''
    Search for maximum "Y + error" amonh histograms and stacks

    empty stacks are accepted. The function has the same limitations as the
    find_maximum function (read WARNINGs)
    '''

    maximums = [find_maximum(hist) for hist in hists if hist]

    for stack in stacks:
        if stack and stack.GetHists():
            maximums.extend([find_maximum(hist) for hist in stack.GetHists() if hist])

    return max(maximums)
