#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 14, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function, division

import itertools
import os

import ROOT

from config import channel, plot, scale
from root import comparison, error, style, stats
from template import loader
from util.arg import split_use_and_ban

class Templates(object):
    '''
    Base for all template(s) processing units

    The most-basic functionality is implemented here and includes:
        - template(s) loading: inputs and group these into channels
        - prepare signal(s), background(s) and data for plotting
        - drawall plots in the same style
        - add experiment and user defined labels
    '''

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
        ''' Access loaded plots '''

        return self._plots

    def run(self):
        '''
        Entry point for the templates analysis
        
        WARNING: be carefull overriding this method - make sure the basic
                 functionality is implemented, e.g.: loading and plotting
        '''

        # It is essential to load style before any histogram is loaded or
        # created
        root_style = style.analysis()
        root_style.cd()

        ROOT.gROOT.ForceStyle()

        self.load()

        canvases = self.plot()
        if canvases:
            if self._save:
                for canvas in canvases:
                    canvas.canvas.SaveAs(
                        "{0}.{1}".format(canvas.canvas.GetName(), self._save))

            if not self._batch_mode:
                raw_input("enter")

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

            channel_scale_ = (self._channel_scale and
                              self._channel_scale.get(channel_, None))

            if self._verbose and channel_scale_:
                print("custom scale", channel_,
                      "x{0:.3f}".format(channel_scale_))

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
                if channel_ in bg_channels:
                    backgrounds.append(hist)
                    label = "fe"

                elif (channel_.startswith("zprime") or
                      channel_.startswith("kkgluon")):
                    # Signal order does not matter
                    signal.Add(hist)
                    label = "l"

                elif channel_ == "data":
                    data = hist
                    label = "lpe"

                legend.AddEntry(hist,
                                self._channel_config["channel"][channel_]
                                                    ["legend"],
                                label)

            # Add backgrounds to the Stack
            if backgrounds:
                map(background.Add, reversed(backgrounds))

            canvas = self.draw_canvas(plot_,
                                      signal=signal, background=background,
                                      data=data, legend=legend)
            if canvas:
                canvases.append(canvas)

        return canvases

    def draw_canvas(self, plot_name, signal=None, background=None, data=None,
                    legend=None, uncertainty=True):
        '''
        Draw canvas with signal, background, data, legend and labels

        Signal and background are expected to be THStack. The legend
        coordinates are automatically adjusted to make it readable.
        '''

        canvas = comparison.Canvas()
        canvas.canvas.SetName('c_' + plot_name.lstrip('/').replace('/', '_'))

        # Use the first defined plot for axis drawing
        #
        h_axis = next(itertools.chain(
            signal.GetHists() if signal and signal.GetHists() else [],
            background.GetHists() if background and background.GetHists()
                                  else [],
            [data, ] if data else [])).Clone()
        h_axis.SetDirectory(0)
        h_axis.Reset()
        h_axis.SetLineColor(ROOT.kBlack)
        h_axis.SetMinimum(0) # the maximum will be set later

        # Add backgrounds if uncertainty needs to be drawn
        uncertainty_ = (self.get_uncertainty(background)
                        if uncertainty and background
                        else None)

        if uncertainty_ and legend:
            legend.AddEntry(uncertainty_, "Uncertainty", "f")

        h_axis.SetMaximum(1.2 * stats.maximum(hists=[data, uncertainty_],
                                              stacks=[signal,]))

        h_axis.Draw('9')

        self.draw(background=background,
                  uncertainty=uncertainty_,
                  data=data,
                  signal=signal)

        # re-draw axis for nice look
        h_axis.Draw('9 same')

        # Store drawn objects in canvas
        canvas.objects = {
                "axis": h_axis,
                "background": background,
                "uncertainty": uncertainty_,
                "data": data,
                "signal": signal
                }

        # Adjust legend size
        if legend:
            legend.SetTextSizePixels(18)
            legend.SetX2(0.94)
            legend.SetY2(0.89)
            legend.SetX1(0.65)
            legend.SetY1(legend.GetY2() -
                         .035 * len(legend.GetListOfPrimitives()))

            legend.Draw('9')

            canvas.objects["legend"] = legend

        # Add experiment label
        if data:
            cms_label = ROOT.TLatex(0.2, 0.92,
                                    "CMS, {0:.1f} fb^".format(
                                        self._channel_config["luminosity"] / 1000) +
                                    "{-1}, #sqrt{s}= 7 TeV")
        else:
            cms_label = ROOT.TLatex(0.2, 0.92,
                                    "CMS Simulation, #sqrt{s}= 7 TeV")
        cms_label.SetTextSize(0.046)
        cms_label.Draw("9")
        canvas.objects["experiment-label"] = cms_label

        if self._label:
            user_label = ROOT.TLatex(0.95, 0.92, self._label)
            user_label.SetTextAlign(31) # Right aligned text
            user_label.SetTextSize(0.046)
            user_label.Draw("9")

            canvas.objects["user-label"] = user_label

        if self._sub_label:
            user_label = ROOT.TLatex(0.25, 0.87, self._sub_label)
            user_label.SetTextAlign(13) # left aligned text
            user_label.SetTextSize(0.046)
            user_label.Draw("9")

            canvas.objects["sub-label"] = user_label

        # re-draw everything for nice look
        canvas.canvas.Update()

        return canvas

    def draw(self, background=None, uncertainty=None, data=None, signal=None):
        ''' Let sub-classes redefine how each template should be drawn '''

        if background:
            background.Draw("9 hist same")

        if uncertainty:
            uncertainty.Draw("9 e2 same")

        if data:
            data.Draw("9 same")

        if signal:
            signal.Draw("9 hist same nostack")

    def get_uncertainty(self, background):
        ''' Calculate the background uncertainty band '''

        hist = None
        if background.GetHists():
            for bg_ in background.GetHists():
                if not hist:
                    hist = bg_.Clone()
                    hist.SetDirectory(0)
                else:
                    hist.Add(bg_)

            hist.SetMarkerSize(0)
            hist.SetLineWidth(0)
            hist.SetLineColor(ROOT.kGray + 3)
            hist.SetFillStyle(3005)
            hist.SetFillColor(ROOT.kGray + 3)

        return hist
