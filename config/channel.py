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
    for chnl in cfg["channel"]:
        if "color" not in chnl:
            raise RuntimeError("missing color in channel: " + chnl["name"])

        chnl["color"] = sum(chnl["color"])

    # Remove all unused objects except luminosity, input and channel
    #
    for key in set(cfg.keys()) - set(["luminosity", "input", "channel"]):
        cfg.pop(key)

    # Convert inputs and channels from list to dictionary: keys are input names
    #
    for key in ("input", "channel"):
        input_ = {}
        for list_ in cfg[key]:
            name = list_.pop("name")
            input_[name] = list_

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

    def expand_(config, pattern):
        '''
        Search for channels that match pattern, remove those that have all
        inputs turned OFF
        '''

        # Get list of channels that match narrow Z'
        #
        channel = set(c for c in config["channel"].keys() if pattern.match(c))

        # Get sub-set of the above channels that have at least one input
        # turned ON
        #
        ch_on = set(c for c in channel
                    if any(config["input"][i]["enable"]
                           for i in config["channel"][c]["inputs"]))

        # Get all the channels to be removed
        #
        ch_off = channel - ch_on

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

            channels.update(expand_(config, pattern))

    # Make sure all of the expanded channels are supported
    #
    ch_unsupported = channels - set(config["channel"].keys())

    if ch_unsupported and verbose:
        print("warning: removing unsupported channels -",
              ','.join(ch_unsupported))

    channels -= ch_unsupported

    return channels

if "__main__" == __name__:
    import sys

    cfg = load(sys.argv[1])
    format_str = "{0:>25} {1}"
    for key, values in cfg.items():
        print(("-- {0} --".format(key)).ljust(80, '-'))

        if "luminosity" == key:
            print(format_str.format("", values))
        else:
            for k, v in values.items():
                print("{0:>25} {1}".format(k, v))
