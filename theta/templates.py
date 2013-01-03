#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jul 13, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function, division

import math
import sys

import ROOT

from config import channel
import root.tfile
from template import templates

class Input(templates.Templates):
    ''' Save theta input plot(s) '''

    channel_names = {
            # Map channel type to channel name to be used in plot name

            # Backgrounds
            "wjets": "wlight",
            "zjets": "zlight",
            "stop": "singletop",
            "qcd": "eleqcd",
            "data": "DATA",

            # narrow resonances
            "zp500w5": "zp500w1p",
            "zp750w7p5": "zp750w1p",
            "zp1000w10": "zp1000w1p",
            "zp1250w12p5": "zp1250w1p",
            "zp1500w15": "zp1500w1p",
            "zp2000w20": "zp2000w1p",
            "zp3000w30": "zp3000w1p",
            "zp4000w40": "zp4000w1p",

            # wide resonances
            "zp500w50": "zp500w10p",
            "zp750w75": "zp750w10p",
            "zp1000w100": "zp1000w10p",
            "zp1250w125": "zp1250w10p",
            "zp1500w150": "zp1500w10p",
            "zp2000w200": "zp2000w10p",
            "zp3000w300": "zp3000w10p",
            "zp4000w400": "zp4000w10p",
    }

    def __init__(self, options, args, config):
        templates.Templates.__init__(self, options, args, config)

        self._theta_prefix = options.theta_prefix
        self._output = options.output
        self.__plots = options.plots

    def plot(self):
        ''' Process loaded histograms and draw these '''

        with root.tfile.topen(self._output, 'update') as output_:
            channels = self.plots[self.__plots]
            for channel_, hist in channels.items():
                channel_ = self.channel_names.get(channel_, channel_)
                name = "{prefix}_{plot}__{channel}".format(
                            prefix=self._theta_prefix,
                            plot="mttbar",
                            channel=channel_)
                hist.SetName(name)
                hist.Write()
