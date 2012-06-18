#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 18, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function

import os
import yaml

from config import config

destination = os.path.expanduser("~/.exo")
if not os.path.exists(destination):
    os.mkdir(destination, 0o755)
    print("created configuration folder:", destination)
    
config_destination = os.path.join(destination, "template.yaml")
if not os.path.exists(config_destination):
    pwd = os.getcwd()

    cfg = config.load("config/config.yaml")

    cfg["template"]["channel"] = os.path.join(pwd, "config/2011.input.yaml")
    cfg["template"]["plot"] = os.path.join(pwd, "config/2011.plot.yaml")

    with open(config_destination, "w") as output_:
        yaml.dump(cfg, output_)

    print("the application configuration is saved in:", config_destination)

print("the system is setup for running")
