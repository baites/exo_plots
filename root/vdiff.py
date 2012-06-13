#!/usr/bin/env python

'''
Created by Samvel Khalatyan, May 16, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function

import os
import sys

import ROOT
import root.tfile
import root.comparison
import root.diff

def vdiff(lfile, rfile, verbose=True):
    '''
    Compare two files and plot diffed histograms 

    Given two ROOT files and set of common top-level keys, plot only these
    histograms that are NOT equal. Integral of the histograms are used for
    the latter check.

    Usage:

        vdiff("file1.root", "file2.root")
    '''

    result, lkeys, common_keys, rkeys = root.diff.diff(lfile, rfile,
                                                       verbose=False)

    if result and verbose:
        print("warning: files have different content", file=sys.stderr)
        print()

    if not common_keys:
        if verbose:
            print("no common keys are found in files")

        return False

    with root.tfile.topen(lfile) as lfile_:
        with root.tfile.topen(rfile) as rfile_:
            for key in sorted(common_keys):
                lh = lfile_.Get(key)
                if not lh:
                    if verbose:
                        print("failed to extract", key, "from", lfile,
                              file=sys.stderr)

                    continue

                rh = rfile_.Get(key)
                if not rh:
                    if verbose:
                        print("failed to extract", key, "from", rfile,
                              file=sys.stderr)

                    continue

                # Process plots only
                if (not isinstance(lh, ROOT.TH1) or
                    not isinstance(rh, ROOT.TH1)):

                    continue

                # Skip equal plot 
                if lh.Integral() == rh.Integral():
                    continue

                # Adjust plots style
                lh.SetLineColor(ROOT.kGreen + 1)
                rh.SetLineColor(ROOT.kRed + 1)

                for h in lh, rh:
                    h.SetFillStyle(0)
                    h.SetLineStyle(1)

                # Draw two histograms overlayed
                cmp_ = root.comparison.Canvas()
                cmp_.canvas.cd(1)

                stack = ROOT.THStack()
                stack.Add(lh)
                stack.Add(rh)
                stack.Draw("9 hist nostack")

                # Add legend for offline review
                legend = ROOT.TLegend(0.4, 0.7, 0.88, 0.8)
                legend.SetTextSizePixels(18)
                legend.SetHeader(key)
                legend.AddEntry(lh, lfile, "l")
                legend.AddEntry(rh, rfile, "l")
                legend.Draw("9")

                # Draw comparison
                cmp_.canvas.cd(2)
                ratio = root.comparison.ratio(lh, rh, "#frac{GREEN}{RED}")
                ratio.GetYaxis().SetRangeUser(0, 5)
                ratio.Draw("9")

                cmp_.canvas.Update()
                cmp_.canvas.SaveAs(key + ".pdf")

    return result

if "__main__" == __name__:
    try:
        if len(sys.argv) != 3:
            raise RuntimeError("usage: {0} file1.root file2.root".format(
                               sys.argv[0]))

        for filename in sys.argv[1:]:
            if not os.path.exists(filename):
                raise RuntimeError("file does not exist " + filename)

        sys.argv.append("-b") # make ROOT work in batch mode

        sys.exit(1 if vdiff(*sys.argv[1:]) else 0)

    except RuntimeError as error:
        print(error, file=sys.stderr)

        sys.exit(1)
