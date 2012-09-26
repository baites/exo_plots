#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jul 13, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function

import os
import sys

from config import config
from template.options import parser

def main():
    class HelpExit(Exception): pass

    verbose = False
    try:
        opt_parser = parser()
        opt_parser.get_option("--plots").help = (
                "Only /cutflow or /cutflow_no_weight plots are accepted "
                "[one at a time]")
        opt_parser.remove_option("--label")
        opt_parser.remove_option("--sub-label")
        opt_parser.remove_option("-s")
        opt_parser.add_option("--mode",
                              action="store", default="text",
                              help="print output in one of the formats: text, tex")
        opt_parser.add_option("--non-threshold",
                              action='store_true', default=False,
                              help="print non-threshold cutflow")

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
        from preselection import templates

        if not options.plots:
            options.plots = "/cutflow"
        elif options.plots not in ["/cutflow", "/cutflow_no_weight"]:
            raise RuntimeError("choose either /cutflow or /cutflow_no_weight plot")

        app = templates.Cutflow(options, args, config_)
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
