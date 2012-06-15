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

    result, common_keys = root.diff.diff(lfile, rfile, verbose=False)[1:3:2]

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
                lhist = lfile_.Get(key)
                if not lhist:
                    if verbose:
                        print("failed to extract", key, "from", lfile,
                              file=sys.stderr)

                    continue

                rhist = rfile_.Get(key)
                if not rhist:
                    if verbose:
                        print("failed to extract", key, "from", rfile,
                              file=sys.stderr)

                    continue

                # Process plots only
                if (not isinstance(lhist, ROOT.TH1) or
                    not isinstance(rhist, ROOT.TH1)):

                    continue

                # Skip equal plot 
                if lhist.Integral() == rhist.Integral():
                    continue

                # Adjust plots style
                lhist.SetLineColor(ROOT.kGreen + 1)
                rhist.SetLineColor(ROOT.kRed + 1)

                for hist in lhist, rhist:
                    hist.SetFillStyle(0)
                    hist.SetLineStyle(1)

                # Draw two histograms overlayed
                cmp_ = root.comparison.Canvas()
                cmp_.canvas.cd(1)

                stack = ROOT.THStack()
                stack.Add(lhist)
                stack.Add(rhist)
                stack.Draw("9 hist nostack")

                # Add legend for offline review
                legend = ROOT.TLegend(0.4, 0.7, 0.88, 0.8)
                legend.SetTextSizePixels(18)
                legend.SetHeader(key)
                legend.AddEntry(lhist, lfile, "l")
                legend.AddEntry(rhist, rfile, "l")
                legend.Draw("9")

                # Draw comparison
                cmp_.canvas.cd(2)
                ratio = root.comparison.ratio(lhist, rhist)
                ratio.GetYaxis().SetTitle("#frac{GREEN}{RED}")
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
