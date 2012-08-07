#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 15, 2012
Copyright 2012, All rights reserved
'''

from __future__ import division, print_function

import re
import sys

import ROOT

from root import template

class InputLoader(template.Loader):
    '''
    Load input file
    
    The plots are saved in dictionary with key being the path with histogram
    name
    '''

    def __init__(self, plot_patterns=[]):
        '''
        Specify which plots will be added in patterns

        Patterns is an array of paths inside ROOT file including foler, e.g.:

            /plot1
            /jet/pt

        Bash wildcards are accepted in patterns. These include:

            *       any number of masked symbols in the name [note: only word
                    characters are accepted, e.g.: a-z A-Z 0-9 _ -

            ?       one masked symbol [note: the same restriction as above]
            [a-d]   any symbol in the range. a, b, c, d in the example
            [!a-c]  any symbol except specified ones. a, b, c in the example
            {ab,cd} any comma separated combination. ab, or cd in the example

        Examples:

            consider structure:

                    /jet1/pt
                    /jet1/eta
                    /jet2/pt
                    /jet2/eta
                    /jet3a/pt
                    /jet3a/eta

            /jet?/pt        load all jet1 and jet2 pT
            /jet*/eta       load all jets pT
            /jet[1-2]/pt    load jet1 and jet1 pt
            /jet[!1-2]/eta  load only jet3a eta
            /jet{1,3a}/eta  load jet1 and jet3a eta
            /jet1/*         load all jet properties
        '''

        template.Loader.__init__(self)

        self._plots = {}

        search_and_replace = {
                r'\*': "\w*",
                r'\?': "\w",
                r'\[!': '[^',
                r'\{': '(?:',
                r'\}': ')',
                r',': '|'
                }

        self._plot_patterns = []
        for pattern in plot_patterns:
            for srch, repl in search_and_replace.items():
                pattern = re.sub(srch, repl, pattern)

            self._plot_patterns.append(re.compile("^" + pattern + "$"))

    @property
    def plots(self):
        '''Access plots'''

        return self._plots

    def process_plot(self, hist):
        '''Store plot'''

        # skip 2D plots
        if 1 != hist.GetDimension():
            return

        dir_ = hist.GetDirectory()
        fmt = "{0}/{1}" if dir_ else "{1}"

        key = fmt.format(dir_.GetPath().split(':', 1)[1],
                         hist.GetName())

        key = key.replace("//", '/')

        if (self._plot_patterns and
            not any(re_.match(key) for re_ in self._plot_patterns)):

            return

        clone = hist.Clone()
        clone.SetDirectory(0)

        self._plots[key] = clone

class ChannelLoader(object):
    '''
    Load Channel plots
    
    The class will load all enabled inputs, scale these, merge into channel
    and apply styles
    '''

    def __init__(self, prefix, input_loader=InputLoader, verbose=False):
        ''' Initialize the channel loader

        the arguments are:

            prefix          filename prefix to be used by input loader
            input_loader    class to be used to load inputs
            verbose         print debug info

        All the loaded plots are kept in the plots dictionary. The keys are
        histograms paths with names (e.g. /jet1/pt) and values are histogram
        objects
        '''

        self._prefix = prefix
        self._plots = None
        self._input_loader = input_loader
        self._verbose = verbose

    @property
    def plots(self):
        '''Access loaded plots'''

        return self._plots

    def load(self, ch_config, plt_config, channel, plot_patterns=[]):
        ''' Load and process inputs

        the arguments are:

            ch_config       channel configuration (specify styles, what inputs
                            belong to channel, etc.)
            plt_config      plot configuration (rebin, visible range, etc.)
            channel         channel name to be loaded
            plot_patterns   plots to be loaded
        '''

        self._plots = None
        loaded_plots = []
        luminosity = ch_config["luminosity"]
        for input_ in ch_config["channel"][channel]["inputs"]:
            # skip input if it is disabled
            if not ch_config["input"][input_]["enable"]:
                if self._verbose:
                    print("warning: skip input", input_,
                          "because it is disabled")

                continue

            if self._verbose:
                print("load input:", input_)

            loader = self._input_loader(plot_patterns=plot_patterns)
            loader.load("{0}.{1}.root".format(self._prefix, input_))

            # Scale all loaded plots to theory and style
            info = ch_config["input"][input_]
            xsection, events = info["xsection"], info["events"]

            if xsection and events:
                normalization = xsection * luminosity / events
                if self._verbose:
                    print("normalize", input_, "to", normalization)

                for hist in loader.plots.values():
                    hist.Scale(normalization)

            loaded_plots.append(loader.plots)

        # all the input plots are loaded: combine inputs
        info = ch_config["channel"][channel]
        for plots in loaded_plots:
            if not self._plots:
                self._plots = plots
            else:
                for key, plot in self._plots.items():
                    plot.Add(plots[key])

        # apply channel styles, plot rebinning etc.
        #
        color = info["color"]
        fill = info["fill"]
        line = info["line"]
        for key, plot in self._plots.items():
            plot.SetLineColor(color)
            plot.SetFillColor(color)

            plot.SetFillStyle(1001 if fill else 0)

            if "data" == channel:
                plot.SetMarkerStyle(20)
                plot.SetMarkerSize(1)
            else:
                plot.SetMarkerStyle(1)

            plot.SetLineWidth(2)
            if line:
                plot.SetLineStyle(line)

            cfg = plt_config["plot"].get(key, None)
            if not cfg:
                if self._verbose:
                    print("plot", plot,
                          "is not found in the template configuration",
                          file=sys.stderr)

                continue

            if "rebin" in cfg:
                # 1D plot
                rebin = cfg.get("rebin")
                if rebin and 1 < rebin:
                    plot.Rebin(rebin)

                title = cfg["title"]
                units = cfg["units"]
                if title:
                    plot.GetXaxis().SetTitle(("{0} [{1}]" if units
                                              else "{0}").format(title,
                                                                 units))

                plot.GetYaxis().SetTitle("event yield")

                # Apply user range to the x-axis if set
                range_ = cfg["range"]
                if range_:
                    plot.GetXaxis().SetRangeUser(*range_)
            else:
                # 2D plot
                for axis, frebin, fget_axis in (
                                 ("x", ROOT.TH2.RebinX, ROOT.TH1.GetXaxis),
                                 ("y", ROOT.TH2.RebinY, ROOT.TH1.GetYaxis)
                                               ):

                    rebin = cfg.get(axis + "rebin")
                    if rebin and 1 < rebin:
                        frebin(plot, rebin)
                    
                    title = cfg[axis + "title"]
                    units = cfg[axis + "units"]
                    if title:
                        fget_axis(plot).SetTitle(("{0} [{1}]" if units
                                                  else "{0}").format(title,
                                                                     units))

                    # Apply user range to each axis if set
                    range_ = cfg.get(axis + "range")
                    if range_:
                        fget_axis(plot).SetRangeUser(*range_)
