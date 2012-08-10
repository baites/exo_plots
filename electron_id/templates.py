#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jul 17, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function, division

import math
import sys

import ROOT

from config import channel
from root import stats
from template import templates

class ElectronIDEfficiency(templates.Templates):
    def __init__(self, options, args, config):
        templates.Templates.__init__(self, options, args, config)

        self._legend_valign = "bottom"

    def plot(self):
        ''' Process loaded histograms and draw these '''

        el_no_ids = [key_ for key_ in self.plots.keys()
                           if key_.startswith("/el_no_id")]
        if not el_no_ids:
            raise RuntimeError("/el_no_id/* plots are not loaded")

        electron_ids = [key_ for key_ in self.plots.keys()
                        if key_.startswith("/el_id_")]
        if not electron_ids:
            raise RuntimeError("/el_id_?/* plots are not loaded")

        canvases = []

        el_id_style = {
            "el_id_0": {
                "name": "VeryLoose",
                "color": ROOT.kGray
            },
            "el_id_1": {
                "name": "Loose",
                "color": ROOT.kGray + 1
                },
            "el_id_2": {
                "name": "Medium",
                "color": ROOT.kGreen + 1
                },
            "el_id_3": {
                "name": "Tight",
                "color": ROOT.kAzure + 1
                },
            "el_id_4": {
                "name": "SuperTight",
                "color": ROOT.kBlue + 1
                },
            "el_id_5": {
                "name": "HyperTight1",
                "color": ROOT.kRed
            },
            "el_id_6": {
                "name": "HyperTight2",
                "color": ROOT.kRed + 1
                },
            "el_id_7": {
                "name": "HyperTight3",
                "color": ROOT.kRed + 2
                },
            "el_id_8": {
                "name": "HyperTight4",
                "color": ROOT.kRed + 3
                }
        }

        for plot_key in el_no_ids:
            el_no_id = self.plots[plot_key]
            plot_suffix = plot_key.rsplit('/', 1)[1]

            el_id_order = ["/el_id_{0}".format(id_) + "/" + plot_suffix
                           for id_ in range(0, 9)]

            for channel_, el_no_id_plot in el_no_id.items():
                stack = ROOT.THStack()
                legend = ROOT.TLegend(0, 0, 0, 0)
                legend.SetHeader(self._channel_config["channel"][channel_]
                                                     ["legend"])

                for id_ in el_id_order:
                    if id_ not in electron_ids:
                        continue

                    el_id = self.plots[id_]
                    if channel_ not in el_id:
                        continue

                    hist = el_id[channel_]
                    el_id_plot = hist.Clone()
                    el_id_plot.Divide(hist, el_no_id_plot, 1, 1, "b")
                    el_id_plot.SetLineStyle(1)
                    el_id_plot.SetFillStyle(0)
                    el_id_plot.GetYaxis().SetTitle("Electron ID Efficiency")

                    style = el_id_style.get(id_.split('/', 2)[1], None)
                    if style:
                        el_id_plot.SetLineColor(style["color"])

                    stack.Add(el_id_plot)
                    legend.AddEntry(el_id_plot,
                                    style["name"] if style else "unknown",
                                    'l')

                if not stack.GetHists():
                    continue

                canvas = self.draw_canvas(channel_, signal=stack, legend=legend,
                                          data=None, uncertainty=False)
                if canvas:
                    canvases.append(canvas)

        return canvases

    def draw(self, background=None, uncertainty=None, data=None, signal=None):
        ''' Let sub-classes redefine how each template should be drawn '''

        if signal:
            signal.Draw("9 hist same nostack e1")
