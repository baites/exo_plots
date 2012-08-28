#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jul 06, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function

import os
import yaml

import channel

def load(filename, config):
    '''
    Load plot YAML configuration
    '''

    if not os.path.exists(filename):
        raise RuntimeError("yaml scales file does not exist: " + filename)

    scales = None
    with open(filename) as input_:
        scales = yaml.load('\n'.join(input_.readlines()))

    if not scales:
        raise RuntimeError("failed to read yaml scales: " + filename)

    # Expand all channel abbreviations
    scales_ = {}
    for channel_, scale_ in scales.items():
        sources_ = set([channel_,])
        channel.expand(config, sources_)

        scales_.update(dict.fromkeys(sources_, scale_))

    return scales_

if "__main__" == __name__:
    import sys

    scales = load(sys.argv[1])
    for channel, scale in scales.items():
        print("{0:>15} {1:.3f}".format(channel, scale))
