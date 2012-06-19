#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 14, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function

import os

import ROOT

from root import comparison
from root import style
from config import channel, plot
from template import loader
from util.arg import split_use_and_ban

class Templates(object):
    def __init__(self, options, args, config,
                 channel_loader=loader.ChannelLoader):

        self._batch_mode = (options.batch if options.batch
                            else config["core"]["batch"])

        self._verbose = (options.verbose if options.verbose
                         else config["core"]["verbose"])

        # load channel configuration
        #
        channel_config = (options.channel_config if options.channel_config
                          else config["template"]["channel"])
        if not channel_config:
            raise RuntimeError("channel config is not defined")

        self._channel_config = channel.load(os.path.expanduser(channel_config))

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

        for channel in self._channels:
            ch_loader = self._channel_loader(self._prefix,
                                             verbose=self._verbose)
            ch_loader.load(self._channel_config, self._plot_config, channel)

            # Channel plots are loaded. Store plots in the dictionary with
            # keys equal to plot name and values are dictionaries with keys
            # being the channel and values are plots
            #
            for key, hist in ch_loader.plots.items():
                if key not in self.plots:
                    self._plots[key] = {}

                self._plots[key][channel] = hist

    def plot(self):
        '''
        Plot loaded histograms
        '''

        canvases = []
        bg_channels = set(["mc", "qcd"])
        channel.expand(self._channel_config, bg_channels)

        for plot, channels in self.plots.items():
            canvas = comparison.Canvas()

            # Prepare stacks for data, background and signal
            background = ROOT.THStack()
            signal = ROOT.THStack()
            data = None

            legend = ROOT.TLegend(0.6, 0.5, .94, .89)

            # Use random item to plot axis
            #
            h_axis = channels[channels.keys().pop()].Clone()
            h_axis.SetDirectory(0)
            h_axis.Reset()

            # prepare channels order and append any missing channels to the
            # end in random order
            order = self._channel_config["order"]
            order.extend(set(channels.keys()) - set(order))

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

            # Make sure the background order the one in Legend
            if backgrounds:
                for bg_ in reversed(backgrounds):
                    background.Add(bg_)

            h_axis.Draw('9')
            background.Draw("9 hist same")
            signal.Draw("9 hist same nostack")

            if data:
                data.Draw("9 same")

            h_axis.SetMinimum(0)
            h_axis.SetMaximum(1.2 * max([
                background.GetMaximum(),
                signal.GetMaximum(),
                data.GetMaximum() if data else 0]))

            h_axis.Draw('9 axis same')

            legend.Draw('9')

            canvas.objects = [h_axis, background, signal, data]
            canvas.canvas.Update()

            canvases.append(canvas)

        raw_input("enter")
