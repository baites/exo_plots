#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 14, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function

import os
import re
import yaml

def load(filename):
    '''
    Load YAML configuration file into memory

    The function will raise RuntimeError if:

        - file does not exist
        - reading YAML config failed or contains no Data

    A loaded YAML config data is returned
    '''
    if not os.path.exists(filename):
        raise RuntimeError("yaml config file does not exist: " + filename)

    cfg = None
    with open(filename) as input_:
        cfg = yaml.load('\n'.join(input_.readlines()))

    if not cfg:
        raise RuntimeError("failed to read yaml config: " + filename)

    # Convert colors from list to the value, e.g.:
    # [10, 5] -> 15
    #
    for x in cfg["channel"]:
        if "color" not in x:
            raise RuntimeError("missing color in channel: " + x["name"])

        x["color"] = sum(x["color"])

    # Remove all unused objects except luminosity, input and channel
    #
    for x in set(cfg.keys()) - set(["luminosity", "input", "channel"]):
        cfg.pop(x)

    # Convert inputs and channels from list to dictionary: keys are input names
    #
    for key in ("input", "channel"):
        input_ = {}
        for x in cfg[key]:
            name = x.pop("name")
            input_[name] = x

        cfg[key] = input_

    return cfg

def expand(config, channels, verbose=False):
    '''
    Expand any channel abbreviations in the set of channels

    WARNING: the channels set is modified

    All invalid channels are removed or the ones that have all of the iputs
    turned OFF

    Supported abbreviations are:
        zp      Z' 1% width
        zpwide  Z' 10% width
        kk      KK gluon
        mc      All Monte-Carlo nominal backgrounds
    '''

    def expand_(config, channels, pattern):
        '''
        Search for channels that match pattern, remove those that have all
        inputs turned OFF
        '''

        # Get list of channels that match narrow Z'
        #
        ch = set(c for c in config["channel"].keys() if pattern.match(c))

        # Get sub-set of the above channels that have at least one input
        # turned ON
        #
        ch_on = set(c for c in ch if any(config["input"][i]["enable"]
                                         for i in config["channel"][c]["inputs"]))

        # Get all the channels to be removed
        #
        ch_off = ch - ch_on

        if ch_off and verbose:
            print("warning: some of the channels have all inputs turned OFF -",
                  ','.join(ch_off))

        return ch_on

    # Process abbreviations
    #
    for abbreviation, pattern in {
            "zp": "^zprime_m(?P<width>\d{2})\d{2}_w(?P=width)$",
            "zpwide": "^zprime_m(?P<width>\d{3})\d{1}_w(?P=width)$",
            "kk": "^kkgluon_m\d{4}$",
            "mc": "^(ttbar|wb|wc|wlight|stop)$"
            }.items():

        if abbreviation in channels:
            pattern = re.compile(pattern)
            channels.remove(abbreviation)

            channels.update(expand_(config, channels, pattern))

    # Make sure all of the expanded channels are supported
    #
    ch_unsupported = channels - set(config["channel"].keys())

    if ch_unsupported and verbose:
        print("warning: removing unsupported channels -",
              ','.join(ch_unsupported))

    channels -= ch_unsupported

    return channels
