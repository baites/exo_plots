#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 14, 2012
Copyright 2012, All rights reserved
'''

import os
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
        raise RuntimeErorr("yaml config file does not exist: " + filename)

    cfg = None
    with open(filename) as input_:
        cfg = yaml.load('\n'.join(input_.readlines()))

    if not cfg:
        raise RuntimeError("failed to read yaml config: " + filename)

    # Convert colors from list to the value
    #
    for x in cfg["channel"]:
        if "color" not in x:
            raise RuntimeError("missing color in channel: " + x["name"])

        x["color"] = sum(x["color"])

    # Remove all unused objects except luminosity, input and channel
    #
    for x in set(cfg.keys()) - set("luminosity", "input", "channel"):
        cfg.pop(x)

    return cfg
