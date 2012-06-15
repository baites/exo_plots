#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Feb 14, 2012
Copyright 2011, All rights reserved

Collection of stadard labels used in histograms. These should be used in all
plots to ensure standard look.
'''

from __future__ import print_function, division

import ROOT

class Label(object):
    '''
    ROOT Legend wrapper to automatically set its style. It tracks one
    property to set legend header.

    Usage:

        # box coordinates: x1, y1, x2, y2
        my_label = Label([.1, .1, .5, .5])
        my_label.label = "This is a generic label"
        ...
        my_label.draw()

    A Legend object is automatically created when accessed
    '''

    def __init__(self, box_coordinates, text_size=None):
        '''
        Initialize label with empty label and box coordinates
        '''

        self.__label = None
        self.__box_coordinates = box_coordinates
        self.__text_size = text_size if text_size else 0.04

    @property
    def label(self):
        '''
        Access legend: automatically create object if it does not exist
        '''
        
        if not self.__label:
            label = ROOT.TLegend(*self.__box_coordinates)

            label.SetTextSize(self.__text_size)
            label.SetMargin(0.12)
            label.SetFillColor(10)
            label.SetBorderSize(0)

            self.__label = label

        return self.__label

    @label.setter
    def label(self, header):
        '''
        Set label header
        '''

        self.label.SetHeader(header)

    @label.deleter
    def label(self):
        del self.__label


    def draw(self):
        '''
        Draw label object
        '''

        self.label.Draw("9")

    def __str__(self):
        '''
        Nice print for label with class name and header if any is set
        '''

        return "<{Class} {header!r} at 0x{ID:x}>".format(
                Class = self.__class__.__name__,
                header = self.label.GetHeader() if self else "",
                ID = id(self))

class CMSLabel(Label):
    '''
    CMS Label with experiment energy, specific size and location, etc.
    '''

    def __init__(self, text_size=None):
        Label.__init__(self, [.20, .91, 1, .96], text_size=text_size)

        self.label = "CMS Preliminary #sqrt{s} = 7 TeV"

class CMSSimulationLabel(CMSLabel):
    '''
    CMS Simulation Label with experiment energy, specific size and location,
    etc.
    '''

    def __init__(self, text_size=None):
        CMSLabel.__init__(self, text_size=text_size)

        self.label = "CMS Simulation Preliminary"

class LuminosityLabel(Label):
    '''
    Luminosity label
    '''

    def __init__(self, luminosity, text_size=None):
        Label.__init__(self, [.65, .91, 1, .96], text_size=text_size)

        self.label = ("L = {0:.1f}".format(luminosity / 1000) +
                        " fb^{-1}, e+jets")

class ChannelLabel(Label):
    '''
    Label with chanenel type, e.g.: 0-btag, 1+btag, etc.
    '''

    def __init__(self, label_, text_size=None):
        Label.__init__(self, [.25, .81, .88, .86], text_size=text_size)

        self.label = label_
