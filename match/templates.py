#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jul 11, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function, division

import math

import ROOT

from config import channel
from root import stats
from template import templates

class Templates(templates.Templates):
    ''' Produce S / B plot '''

    def __init__(self, options, args, config):
        templates.Templates.__init__(self, options, args, config)

        self._background_channels = set(["ttbar",])

    def plot(self):
        ''' Process loaded histograms and draw these '''

        canvases = []
        for plot, channels in self.plots.items():
            signal = ROOT.THStack()
            background_ = ROOT.THStack()
            legend = ROOT.TLegend(0, 0, 0, 0)

            order = self._channel_config["order"]
            order.extend(set(channels.keys()) - set(order))

            # split channels into stacks
            background = None
            for channel_ in order:
                if channel_ not in channels:
                    continue

                hist = channels[channel_]
                hist.Scale(1 / hist.Integral())
                
                title = "#Delta R(q_{1}, q_{2}, b)"
                for key, value in {
                        "/pt": "P_{T}",
                        "/eta": "#eta",
                        "/mass": "M",
                        }.items():
                    if key in plot:
                        title = value

                hist.GetYaxis().SetTitle("dN / N / d" +
                                         title + "")

                if channel_ in self._background_channels:
                    hist.SetLineColor(hist.GetFillColor())
                    hist.SetLineStyle(1)
                    hist.SetLineWidth(2)
                    hist.SetFillStyle(0)

                    background_.Add(hist)

                elif (channel_.startswith("zprime") or
                      channel_.startswith("kkgluon")):

                    signal.Add(hist)
                else:
                    continue

                legend.AddEntry(hist,
                                self._channel_config["channel"][channel_]
                                                    ["legend"], "l")

            canvas = self.draw_canvas(plot, signal=signal,
                                      background=background_,
                                      legend=legend, uncertainty=False)
            if canvas:
                canvases.append(canvas)

        return canvases

    def draw(self, background=None, uncertainty=None, data=None, signal=None):
        ''' Draw background and signal only '''

        if background:
            background.Draw("9 hist same nostack c")

        if signal:
            signal.Draw("9 hist same nostack c")

class DRTemplates(templates.Templates):
    ''' Produce S / B plot '''

    def __init__(self, options, args, config):
        templates.Templates.__init__(self, options, args, config)

        self._background_channels = set(["ttbar",])

    def plot(self):
        '''
        Process loaded histograms and draw them

        The plot() method is responsible for processing loaded channels, e.g.
        put data into Stack, conbine signals, etc.
        '''

        canvases = []
        bg_channels = set(["mc", "qcd"])
        channel.expand(self._channel_config, bg_channels)

        for plot_, channels in self.plots.items():
            # Prepare stacks for data, background and signal
            signal = ROOT.THStack()
            background = ROOT.THStack()
            data = None
            legend = ROOT.TLegend(0, 0, 0, 0) # coordinates will be adjusted

            # prepare channels order and append any missing channels to the
            # end in random order
            order = self._channel_config["order"]
            order.extend(set(channels.keys()) - set(order))

            # process channels in order
            backgrounds = [] # backgrounds should be added to THStack in
                             # reverse order to match legend order
            for channel_ in order:
                if channel_ not in channels:
                    continue

                hist = channels[channel_]
                hist.Scale(1 / hist.Integral())
                hist.SetFillStyle(0)

                if channel_ in bg_channels:
                    backgrounds.append(hist)
                    label = "l"

                elif (channel_.startswith("zprime") or
                      channel_.startswith("kkgluon")):
                    # Signal order does not matter
                    signal.Add(hist)
                    label = "l"

                elif channel_ == "data":
                    data = hist
                    label = "l"

                legend.AddEntry(hist,
                                self._channel_config["channel"][channel_]
                                                    ["legend"],
                                label)

            # Add backgrounds to the Stack
            if backgrounds:
                map(background.Add, reversed(backgrounds))

            canvas = self.draw_canvas(plot_,
                                      signal=signal, background=background,
                                      data=data, legend=legend,
                                      uncertainty=False)
            if canvas:
                canvases.append(canvas)

        return canvases

    def draw(self, background=None, uncertainty=None, data=None, signal=None):
        ''' Let sub-classes redefine how each template should be drawn '''

        if background:
            background.Draw("9 hist same nostack")

        if data:
            data.Draw("9 hist same")

        if signal:
            signal.Draw("9 hist same nostack")
