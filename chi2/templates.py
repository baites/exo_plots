#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jul 05, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function, division

import math

import ROOT

from root import stats
from template import templates

class SignalOverBackground(templates.Templates):
    ''' Produce S / B plot '''

    def __init__(self, options, args, config):
        templates.Templates.__init__(self, options, args, config)

    def plot(self):
        ''' Process loaded histograms and draw these '''

        canvases = []
        bg_channels = set(["wb", "wc", "wlight"]) # use only W+X channels
        for plot, channels in self.plots.items():
            signal = ROOT.THStack()
            legend = ROOT.TLegend(0, 0, 0, 0)

            order = self._channel_config["order"]
            order.extend(set(channels.keys()) - set(order))

            # split channels into stacks
            background = None
            for channel_ in order:
                if channel_ not in channels:
                    continue

                hist = stats.efficiency(channels[channel_], normalize=False)
                hist.GetYaxis().SetTitle("S / B , B = W#rightarrowl#nu")
                if channel_ in bg_channels:
                    if not background:
                        background = hist.Clone()
                    else:
                        background.Add(hist)

                elif (channel_.startswith("zprime") or
                      channel_.startswith("kkgluon")):

                    signal.Add(hist)
                    legend.AddEntry(hist,
                                    self._channel_config["channel"][channel_]
                                                        ["legend"], "l")

            if not signal.GetHists():
                raise RuntimeError("no signal is loaded")

            if not background:
                raise RuntimeError("no background is loaded")

            self.transform(signal, background)

            canvas = self.draw_canvas(plot, signal=signal, legend=legend)
            if canvas:
                canvases.append(canvas)

        return canvases

    def draw(self, background=None, uncertainty=None, data=None, signal=None):
        ''' Draw smoothened signal '''

        if background:
            background.Draw("9 hist same")

        if uncertainty:
            uncertainty.Draw("9 e2 same")

        if data:
            data.Draw("9 same")

        if signal:
            signal.Draw("9 hist same nostack c")

    def transform(self, signal, background):
        ''' Calculate the signal over background ratio '''

        for hist in signal.GetHists():
            hist.Divide(background)

class SignalOverSqrtSignalPlusBackground(SignalOverBackground):
    ''' Produce the S / sqrt(S + B) plot '''

    def __init__(self, options, args, config):
        SignalOverBackground.__init__(self, options, args, config)

    def transform(self, signal, background):
        ''' Calculate the signal over sqrt(S+B) ratio '''

        for hist in signal.GetHists():
            hist.GetYaxis().SetTitle("S / #sqrt{S + B}")
            for bin_ in range(1, hist.GetNbinsX() + 1):
                hist.SetBinContent(bin_, hist.GetBinContent(bin_) /
                                         math.sqrt(hist.GetBinContent(bin_) +
                                         background.GetBinContent(bin_)))

