#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 14, 2012
Copyright 2012, All rights reserved
'''

from optparse import OptionParser

def parser():
    '''
    Default template options parser

    This parser should be used as a baseline for all other template bases
    analysis. For example, consider systematic analysis that uses template
    plots but does not need scales and need to define type of the systematic
    to be processed. Use:

        def syst_parser():
            opt_parser = parser()

            opt_parser.remove_option("--scales")

            opt_parser.add_option(
                "--systematic",
                action="store", default=None,
                help="Systematic type to be processed")

            return opt_parser
    '''

    parser_ = OptionParser(usage="usage: %prog [options]")

    parser_.add_option(
            "-b", "--batch",
            action="store_true", default=False,
            help="Run application in batch mode: do not draw canvases")

    parser_.add_option(
            "-v", "--verbose",
            action="store_true", default=False,
            help="Print debug and progress info")

    parser_.add_option(
            "--config",
            action="store", default="~/.exo/template.yaml",
            help="template configuration")

    parser_.add_option(
            "--channel-config",
            action="store", default=None,
            help="input/channel templates configuration")

    parser_.add_option(
            "--channel-scale",
            action="store", default=None,
            help="channel scales to be applied on top of x-sec * Lumi / N_ev")

    parser_.add_option(
            "--plot-config",
            action="store", default=None,
            help="plots configuration")

    parser_.add_option(
            "--channels",
            action="store", default="mc,data",
            help=("Load templates only for comma separated channels. Signal "
                  "channels can be groupped with: zp, zpwide, kk. Individual "
                  "channel can be turned OFF by prefixing it with minus, "
                  "e.g.: zp,-zprime_m1000_w10"))

    parser_.add_option(
            "--plots",
            action="store", default=None,
            help=("load only plots specified (or all plots otherwise). "
                  "Plots should be colon separated and should include full "
                  "path with respect to the ROOT file, e.g.: "
                  "/plot1,/folder/plot2 . "
                  "BASH wildcards are supported in the names"))

    parser_.add_option(
            "--prefix",
            action="store", default="cms.2011",
            help="file prefix, e.g.: prefix.ttbar.root")

    parser_.add_option(
            "-s", "--save",
            action="store", default=None,
            help="set canvas save format: ps or pdf (prefered)")

    parser_.add_option(
            "--bg-error",
            action="store", default=None,
            help="set background error to percent, e.g.: 25")

    parser_.add_option(
            "--label",
            action="store", default=None,
            help="add label to the top-right corner of the canvas")

    return parser_
