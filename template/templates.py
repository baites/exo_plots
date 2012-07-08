#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 14, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function, division

import math
import os

import ROOT

from root import comparison, error, style, stats
from config import channel, plot, scale
from template import loader
from util.arg import split_use_and_ban

class Templates(object):
    def __init__(self, options, args, config,
                 channel_loader=loader.ChannelLoader):

        self._verbose = (options.verbose if options.verbose
                         else config["core"]["verbose"])

        self._batch_mode = (options.batch if options.batch
                            else config["core"]["batch"])

        if self._batch_mode and not options.save and self._verbose:
            print("warning: script is run in batch mode but canvases are not "
                  "saved")

        # load channel configuration
        #
        channel_config = (options.channel_config if options.channel_config
                          else config["template"]["channel"])
        if not channel_config:
            raise RuntimeError("channel config is not defined")

        self._channel_config = channel.load(os.path.expanduser(channel_config))

        # load channel scale(s)
        #
        self._channel_scale = (
                scale.load(os.path.expanduser(options.channel_scale))
                if options.channel_scale
                else None)

        # load plot configuration
        #
        plot_config = (options.plot_config if options.plot_config
                        else config["template"]["plot"])

        if not plot_config:
            raise RuntimeError("plot config is not defined")

        self._plot_config = plot.load(os.path.expanduser(plot_config))

        # Get list of channels to be loaded
        #
        if not options.channels:
            raise RuntimeError("no channels are specified")

        use, ban = split_use_and_ban(ch.strip()
                                     for ch in options.channels.split(','))
        if not use:
            raise RuntimeError("no channels are turned ON")

        use = channel.expand(self._channel_config, use, verbose=self._verbose)

        if ban:
            use -= channel.expand(self._channel_config, ban,
                                  verbose=self._verbose)

        if not use:
            raise RuntimeError("all channels are turned OFF")

        self._channels = use

        # Loaded plots are kept in the structures like:
        # plot_name: {
        #   channel1: hist_obj,
        #   channel2: hist_obj,
        #   etc.
        # }
        #
        self._plots = {}
        self._channel_loader = channel_loader
        self._prefix = options.prefix
        if options.save:
            value = options.save.lower()

            if value not in ["ps", "pdf"]:
                raise RuntimeError("unsupported save format: " + value)

            self._save = value
        else:
            self._save = False

        self._bg_error = options.bg_error
        if self._bg_error:
            self._bg_error = float(self._bg_error)
            if not (0 <= self._bg_error <= 100):
                raise RuntimeError("background error is out of range")
            else:
                self._bg_error /= 100

        self._label = options.label
        self._sub_label = options.sub_label

        if options.plots:
            self._plot_patterns = options.plots.split(':')
        else:
            self._plot_patterns = []

    @property
    def plots(self):
        return self._plots

    def run(self):

        # It is essential to load style before any histogram is loaded or created
        self._root_style = style.analysis()
        self._root_style.cd()
        ROOT.gROOT.ForceStyle()

        self.load()
        self.plot()

    def load(self):
        '''
        Load all channels into memory

        Child classes may explicitly call this function to load plots
        '''

        bg_channels = set(["mc", ])
        channel.expand(self._channel_config, bg_channels)
        for channel_ in self._channels:
            ch_loader = self._channel_loader(self._prefix,
                                             verbose=self._verbose)
            ch_loader.load(self._channel_config, self._plot_config, channel_,
                           plot_patterns=self._plot_patterns)

            channel_scale_ = self._channel_scale and self._channel_scale.get(channel_, None)

            # Channel plots are loaded. Store plots in the dictionary with
            # keys equal to plot name and values are dictionaries with keys
            # being the channel and values are plots; scale the plots if scale
            # is provided
            #
            for key, hist in ch_loader.plots.items():
                if key not in self.plots:
                    self._plots[key] = {}

                if channel_scale_:
                    hist.Scale(channel_scale_)

                if self._bg_error and channel_ in bg_channels:
                    error.add(hist, self._bg_error)

                self._plots[key][channel_] = hist

    def plot(self):
        '''
        Plot loaded histograms
        '''

        canvases = []
        bg_channels = set(["mc", "qcd"])
        channel.expand(self._channel_config, bg_channels)

        for plot, channels in self.plots.items():
            # Prepare stacks for data, background and signal
            background = ROOT.THStack()
            signal = ROOT.THStack()
            data = None

            legend = ROOT.TLegend(0.6, 0.6, .94, .89)
            legend.SetTextSizePixels(18)

            # Use random item to plot axis
            #
            h_axis = channels[channels.keys().pop()].Clone()
            h_axis.SetDirectory(0)
            h_axis.Reset()
            h_axis.SetLineColor(ROOT.kBlack)

            # prepare channels order and append any missing channels to the
            # end in random order
            order = self._channel_config["order"]
            order.extend(set(channels.keys()) - set(order))

            bg_error_band = None

            # split channels into stacks
            backgrounds = []
            for channel_ in order:
                if channel_ not in channels:
                    continue

                hist = channels[channel_]
                if channel_ in bg_channels:
                    backgrounds.append(hist)
                    label = "fe"

                elif (channel_.startswith("zprime") or
                      channel_.startswith("kkgluon")):

                    signal.Add(hist)
                    label = "l"

                elif channel_ == "data":
                    data = hist
                    label = "lpe"

                legend.AddEntry(hist,
                                self._channel_config["channel"][channel_]["legend"],
                                label)

            # Make sure the background order match the TLegend
            if backgrounds:
                for bg_ in reversed(backgrounds):
                    if not bg_error_band:
                        bg_error_band = bg_.Clone()
                    else:
                        bg_error_band.Add(bg_)

                    background.Add(bg_)

                bg_error_band.SetMarkerSize(0)
                bg_error_band.SetLineWidth(0)
                bg_error_band.SetLineColor(ROOT.kGray + 3)
                bg_error_band.SetFillStyle(3005)
                bg_error_band.SetFillColor(ROOT.kGray + 3)

                legend.AddEntry(bg_error_band,
                                "Uncertainty",
                                "f")

            # Adjust legend height
            legend.SetY1(0.89 - .035 * len(legend.GetListOfPrimitives()))

            canvas = comparison.Canvas()
            canvas.canvas.SetName('c_' + plot[1:].replace('/', '_'))

            # Draw all plots
            h_axis.Draw('9')
            background.Draw("9 hist same")

            if bg_error_band:
                bg_error_band.Draw("9 e2 same")

            signal.Draw("9 hist same nostack")

            if data:
                data.Draw("9 same")

            h_axis.SetMinimum(0)
            h_axis.SetMaximum(1.2 * stats.maximum(hists=[data, bg_error_band],
                                                  stacks=[signal,]))

            h_axis.Draw('9 same')

            legend.Draw('9')

            label = ROOT.TLatex(0.2, 0.92,
                                "CMS, {0:.1f} fb^".format(
                                    self._channel_config["luminosity"] / 1000) +
                                "{-1}, #sqrt{s}= 7 TeV")
            label.SetTextSize(0.046)
            label.Draw("9")

            canvas.objects = [h_axis, bg_error_band, background, signal, data,
                              label, legend]

            if self._label:
                user_label = ROOT.TLatex(0.95, 0.92, self._label)
                user_label.SetTextAlign(31)
                user_label.SetTextSize(0.046)
                user_label.Draw("9")

                canvas.objects.append(user_label)

            if self._sub_label:
                user_label = ROOT.TLatex(0.25, 0.87, self._sub_label)
                user_label.SetTextAlign(13)
                user_label.SetTextSize(0.046)
                user_label.Draw("9")

                canvas.objects.append(user_label)

            canvas.canvas.Update()

            canvases.append(canvas)

        if canvases:
            if self._save:
                for c_ in canvases:
                    c_.canvas.SaveAs("{0}.{1}".format(c_.canvas.GetName(),
                                                      self._save))

            if not self._batch_mode:
                raw_input("enter")
