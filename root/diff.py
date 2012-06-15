#!/usr/bin/env python

'''
Created by Samvel Khalatyan, May 16, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function

import os
import sys

import root.tfile

def diff(lfile, rfile, verbose=True):
    '''
    Compare two ROOT file keys and report if files are different

    The content is compared only at the top level. No histogram equality is
    checked.

    Example:

        diff("file1.root", "file2.root")

    Function will return list with four items:

        [0] True if files are different, False otherwise
        [1] keys that are exclusive to file1
        [2] common keys to two files
        [3] keys that are found only in file2
    '''

    # Extract keys from left file
    lkeys = set()
    with root.tfile.topen(lfile) as lfile_:
        # keys are cached and objects are removed once file is closed:
        # extract the names from cache
        #
        lkeys = set(x.GetName() for x in lfile_.GetListOfKeys())

    # Extract keys from right file
    rkeys = set()
    with root.tfile.topen(rfile) as rfile_:
        rkeys = set(x.GetName() for x in rfile_.GetListOfKeys())

    common_keys = lkeys & rkeys
    lonly_keys = lkeys - common_keys
    ronly_keys = rkeys - common_keys

    if verbose and lonly_keys:
        print("keys exlusive to file", lfile)
        print('\n'.join("< " + str(x) for x in sorted(lonly_keys)))
        print()

    if verbose and ronly_keys:
        print("keys exlusive to file", rfile)
        print('\n'.join("> " + str(x) for x in sorted(ronly_keys)))
        print()

    return bool(lonly_keys or ronly_keys), lonly_keys, common_keys, ronly_keys



if "__main__" == __name__:
    try:
        if len(sys.argv) != 3:
            raise RuntimeError("usage: {0} file1.root file2.root".format(
                               sys.argv[0]))

        for filename in sys.argv[1:]:
            if not os.path.exists(filename):
                raise RuntimeError("file does not exist " + filename)

        sys.exit(1 if diff(*sys.argv[1:])[0] else 0)

    except RuntimeError as error:
        print(error, file=sys.stderr)

        sys.exit(1)
