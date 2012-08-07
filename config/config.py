#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 18, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function

import os
import yaml

def load(filename):
    ''' Load plot YAML configuration '''

    if not os.path.exists(filename):
        raise RuntimeError("yaml config file does not exist: " + filename)

    cfg = None
    with open(filename) as input_:
        cfg = yaml.load('\n'.join(input_.readlines()))

    if not cfg:
        raise RuntimeError("failed to read yaml config: " + filename)

    return cfg

if "__main__" == __name__:
    import sys

    cfg = load(sys.argv[1])
    for k, v in cfg.items():
        print("{0:>10} {1}".format(k, v))
