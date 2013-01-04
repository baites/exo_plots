#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Nov 17, 2012
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
        opt_parser.remove_option("--label")
        opt_parser.remove_option("--sub-label")
        opt_parser.remove_option("-s")
        opt_parser.remove_option("--log")
        opt_parser.remove_option("--bg-error")
        opt_parser.add_option("--theta-prefix",
                              action="store", default="el",
                              help="theta plots prefix")
        opt_parser.add_option('-o', "--output",
                              action='store', default='theta_input.root',
                              help="output filename")

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
        import theta.templates

        app = theta.templates.Input(options, args, config_)
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
