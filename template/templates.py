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
                scale.load(os.path.expanduser(options.channel_scale),
                           self._channel_config)
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

        self._label = options.label or os.getenv("EXO_PLOT_LABEL", None)
        self._sub_label = options.sub_label or os.getenv("EXO_PLOT_SUBLABEL",
                                                         None)

        if options.plots:
            self._plot_patterns = options.plots.split(':')
        else:
            self._plot_patterns = []

        self._legend_align = "right"
        self._legend_valign = "top"

        self._log = options.log

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
                    canvas.SaveAs(
                        "{0}.{1}".format(canvas.GetName(), self._save))

            if not self._batch_mode:
                raw_input("enter")

            for canvas in canvases:
                canvas.Close()

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

            del(ch_loader)

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

                elif (channel_.startswith("zp") or
                      channel_.startswith("rsg")):
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

    def draw_canvas(self, plot_name,
                    signal=None, background=None, data=None,
                    legend=None, uncertainty=True):
        '''
        Draw canvas with signal, background, data, legend and labels

        Signal and background are expected to be THStack. The legend
        coordinates are automatically adjusted to make it readable.
        '''

        name = 'c_' + plot_name.lstrip('/').replace('/', '_')
        canvas = ROOT.TCanvas(name, "")

        canvas.objects = {
                "background": background,
                "data": data,
                "signal": signal
                }

        # Use the first defined plot for axis drawing
        #
        h_axis = next(itertools.chain(
            signal.GetHists() if signal and signal.GetHists() else [],
            background.GetHists() if background and background.GetHists()
                                  else [],
            [data, ] if data else [])).Clone()
        h_axis.SetDirectory(0)
        ROOT.SetOwnership(h_axis, False)

        canvas.objects["axis"] = h_axis

        h_axis.Reset()
        h_axis.SetLineColor(ROOT.kBlack)
        h_axis.SetLineStyle(1)
        h_axis.SetLineWidth(1)

        if not self._log:
            h_axis.SetMinimum(0) # the maximum will be set later
        else:
            h_axis.SetMinimum(0.1)

        # Add backgrounds if uncertainty needs to be drawn
        uncertainty_ = (self.get_uncertainty(background)
                        if uncertainty and background
                        else None)
        canvas.objects["uncertainty"] = uncertainty_

        if uncertainty_ and legend:
            legend.AddEntry(uncertainty_, "Uncertainty", "f")

        h_axis.SetMaximum((10 if self._log else 1.2) *
                          stats.maximum(hists=[data, uncertainty_],
                                              stacks = [signal, background]))

        h_axis.Draw('9')

        self.draw(background=background,
                  uncertainty=uncertainty_,
                  data=data,
                  signal=signal)

        # re-draw axis for nice look
        h_axis.Draw('9 same')

        if legend:
            self.draw_legend(legend, width=0.34 if signal else 0.29)
            canvas.objects["legend"] = legend

        # Add experiment label
        canvas.objects["experiment-label"] = self.draw_experiment_label(data)

        if self._label:
            canvas.objects["user-label"] = self.draw_label()

        if self._sub_label:
            canvas.objects["sub-label"] = self.draw_sub_label()

        if self._log:
            canvas.SetLogy()

        # re-draw everything for nice look
        canvas.Update()

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
            hist.SetFillStyle(3345)
            hist.SetFillColor(ROOT.kGray + 3)

        return hist

    def draw_legend(self, legend, width=0.29):
        if "right" == self._legend_align:
            x2 = 0.94
            x1 = x2 - width 
        elif "left" == self._legend_align:
            x1 = 0.23
            x2 = x1 + width
        else:
            raise RuntimeError(("only right and left legend alignment "
                                " is supported"))

        legend_height = 0.035 * (len(legend.GetListOfPrimitives()) +
                                 (1 if legend.GetHeader() else 0))
        if "top" == self._legend_valign:
            y2 = 0.89
            y1 = y2 - legend_height
        elif "bottom" == self._legend_valign:
            y1 = 0.18
            y2 = y1 + legend_height
        else:
            raise RuntimeError(("only top and bottom legend valign is "
                                "supported"))

        legend.SetTextSizePixels(18)
        legend.SetX1(x1)
        legend.SetY1(y1)
        legend.SetX2(x2)
        legend.SetY2(y2)

        legend.Draw('9')

    def draw_experiment_label(self, is_data):
        if is_data:
            label = "CMS Preliminary, {0:.1f} fb^".format(
                        self._channel_config["luminosity"] / 1000) + "{-1}"
        else:
            label = "CMS Simulation"

        label = ROOT.TLatex(0.2, 0.92,
                            label + ", #sqrt{s} = " +
                            "{0:.0f} TeV".format(self._channel_config["energy"]))
        label.SetTextSize(0.046)
        label.Draw("9")

        return label

    def draw_label(self):
        label = ROOT.TLatex(0.95, 0.92, self._label)
        label.SetTextAlign(31) # Right aligned text
        label.SetTextSize(0.046)
        label.Draw("9")

        return label

    def draw_sub_label(self):
        if 'top' == self._legend_valign and "left" == self._legend_align:
            label = ROOT.TLatex(0.93, 0.87, self._sub_label)
            label.SetTextAlign(33) # right aligned text
        else:
            label = ROOT.TLatex(0.25, 0.87, self._sub_label)
            label.SetTextAlign(13) # left aligned text

        label.SetTextSize(0.046)
        label.Draw("9")

        return label
