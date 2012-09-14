#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Sep 14, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function

import os
import sys

from config import config
import template.options

def parser():
    parser_ = template.options.parser()

    parser_.add_option(
            "--rebin",
            action="store_true", default=False,
            help="Merge first and last bins")

    parser_.remove_option("--plots")

    return parser_

def main():
    class HelpExit(Exception): pass

    verbose = False
    try:
        opt_parser = parser()
        options, args = opt_parser.parse_args()

        # load application configuration
        #
        if not options.config:
            raise RuntimeError("application configuration is not specified")

        config_ = config.load(os.path.expanduser(options.config))
        verbose = (options.verbose if options.verbose
                   else config_["core"]["verbose"])

        if verbose:
            print("loaded configuration from:", options.config)

        if 1 == len(sys.argv):
            raise HelpExit()

        # import templates only here otherwise PyROOT inhercepts --help option
        from mc_stat import templates

        options.plots = "/mttbar_after_htlep"
        app = templates.Templates(options, args, config_)
        app.run()
    except HelpExit:
        opt_parser.print_help()

        return 0
    except Exception as error:
        if verbose:
            # print Exception traceback for debug
            import traceback

            traceback.print_tb(sys.exc_info()[2])

        print(error, file=sys.stderr)

        return 1
    else:
        return 0

if "__main__" == __name__:
    sys.exit(main())
