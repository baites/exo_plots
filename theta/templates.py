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

            "ttbar_fall11": "ttbar",
            "stop": "singletop",
            "qcd": "eleqcd",
            "data": "DATA",

            # narrow resonances
            "zprime_m1000_w10": "zp1000",
            "zprime_m1500_w15": "zp1500",
            "zprime_m2000_w20": "zp2000",
            "zprime_m3000_w30": "zp3000",
            "zprime_m4000_w40": "zp4000",

            # wide resonances
            "zprime_m1000_w100": "zp1000wide",
            "zprime_m1500_w150": "zp1500wide",
            "zprime_m2000_w200": "zp2000wide",
            "zprime_m3000_w300": "zp3000wide",
            "zprime_m4000_w400": "zp4000wide",

            # rsgluon
            "rsgluon_m1000": "rsg1000",
            "rsgluon_m1500": "rsg1500",
            "rsgluon_m2000": "rsg2000",
            "rsgluon_m3000": "rsg3000",
            "rsgluon_m4000": "rsg4000",

            "ttbar_matching_plus": "ttbar",
            "ttbar_matching_minus": "ttbar",

            "ttbar_scale_plus": "ttbar",
            "ttbar_scale_minus": "ttbar",
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
                hist.Write(name)
