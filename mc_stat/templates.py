#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Sep 14, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function, division

import itertools
import math
import sys

import ROOT
from numpy import array

from config import channel
from root import stats
from template import templates

class Templates(templates.Templates):
    def __init__(self, options, args, config):
        templates.Templates.__init__(self, options, args, config)

        self._rebin = options.rebin

    def draw_canvas(self, plot_name,
                    signal=None, background=None, data=None,
                    legend=None, uncertainty=True):
        rebin_objects = {}
        if self._rebin:
            h_axis = next(itertools.chain(
                signal.GetHists() if signal and signal.GetHists() else [],
                background.GetHists() if background and background.GetHists()
                                      else [],
                [data, ] if data else [])).Clone()

            edges = [0]
            for bin_ in range(1, h_axis.GetXaxis().GetNbins() + 1):
                low_edge = h_axis.GetXaxis().GetBinLowEdge(bin_)
                if 0.4 <= low_edge <= 1.3:
                    edges.append(low_edge)
            edges.append(4)

            bins = len(edges) - 1
            edges = array(edges)

            # rebin all plots
            if data:
                data_old = data
                data = data.Rebin(bins, data.GetName() + "_rebin", edges)
                rebin_objects["data"] = data

            if signal and signal.GetHists():
                signal_rebin = ROOT.THStack()
                rebin_objects["signal"] = signal_rebin

                for hist in signal.GetHists():
                    hist = hist.Rebin(bins, hist.GetName() + "_rebin", edges)
                    signal_rebin.Add(hist)

                signal = signal_rebin

            if background and background.GetHists():
                background_rebin = ROOT.THStack()
                rebin_objects["background"] = background_rebin

                for hist in background.GetHists():
                    hist = hist.Rebin(bins, hist.GetName() + "_rebin", edges)
                    background_rebin.Add(hist)

                background = background_rebin

        canvas = templates.Templates.draw_canvas(self, plot_name,
                                                 signal, background, data,
                                                 legend, uncertainty)

        canvas.objects['rebin'] = rebin_objects

        return canvas
