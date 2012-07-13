#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jul 13, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function, division

import math

import ROOT

from config import channel
from root import stats
from template import templates

def cutflow(hist):
    if not hist:
        return None

    def stats_(hist, x_):
        bin_ = hist.FindBin(x_)

        return (hist.GetBinContent(bin_), hist.GetBinError(bin_))

    return {"jets": stats_(hist, 5),
            "electron": stats_(hist, 6),
            "veto_lepton": stats_(hist, 8),
            "twod_cut": stats_(hist, 9),
            "jet1": stats_(hist, 10),
            "htlep": stats_(hist, 14),
            "tricut": stats_(hist, 15),
            "met": stats_(hist, 16)
            }

def format_stats(stats, sep="+-"):
    return "{0:>8.0f} {sep} {1:<5.0f}".format(*stats, sep=sep)

def print_cutflow_in_text(channel, cutflow,
                          fields=["jets", "electron", "veto_lepton",
                                  "twod_cut", "jet1", "htlep", "tricut",
                                  "met"]):
    cells = ["{0:>20}".format(channel), ]
    for field_ in fields:
        cells.append(format_stats(cutflow[field_]))
    print(*cells, sep=" | ")

def print_cutflow_in_tex(channel, cutflow,
                         fields=["jets", "electron", "veto_lepton",
                                 "twod_cut", "jet1", "htlep", "tricut",
                                 "met"]):
    cells = [channel, ]
    for field_ in fields:
        cells.append(format_stats(cutflow[field_], sep="&"))
    print(*cells, sep=" & ", end=" \\\\\n")

class Cutflow(templates.Templates):
    ''' Produce S / B plot '''

    def __init__(self, options, args, config):
        templates.Templates.__init__(self, options, args, config)

        self._print_mode= options.mode

    def plot(self):
        ''' Process loaded histograms and draw these '''

        if "/cutflow" not in self.plots:
            raise RuntimeError("cutflow plot was not loaded")

        channels = self.plots["/cutflow"]

        signal_channels = set(["zp", "zpwide", "kk"])
        channel.expand(self._channel_config, signal_channels)

        background_channels = set(["mc", ])
        channel.expand(self._channel_config, background_channels)

        signal_ = {}
        background_ = {}
        total_background_ = None
        data_ = None
        for channel_, hist in channels.items():
            if channel_ in signal_channels:
                signal_[channel_] = cutflow(hist)
            elif channel_ in background_channels:
                background_[channel_] = cutflow(hist)
                if not total_background_:
                    total_background_ = hist.Clone()
                else:
                    total_background_.Add(hist)
            elif channel_ == "data":
                data_ = cutflow(hist)

        total_background_ = cutflow(total_background_)

        channel_names = {
                "zprime_m1000_w10": r"Z' 1 Tev/c\textsuperscript{2}",
                "zprime_m2000_w20": r"Z' 2 Tev/c\textsuperscript{2}",
                "zprime_m3000_w30": r"Z' 3 Tev/c\textsuperscript{2}",
                "stop": r"Single-Top",
                "zjets": r"$Z/\gamma^{\ast}\rightarrow l^{+}l^{-}$",
                "wjets": r"$W\rightarrow l\nu$",
                "ttbar": r"QCD t\bar{t}",
                }

        print_function = (print_cutflow_in_text
                          if self._print_mode == "text"
                          else print_cutflow_in_tex)

        for fields in [["jets", "electron", "veto_lepton", "twod_cut"],
                       ["jet1", "htlep", "tricut", "met"]]:

            for channel_ in self._channel_config["order"]:
                if (not channel_.startswith("zprime") or
                    channel_ not in signal_):

                        continue

                print_function(channel_names.get(channel_, channel_),
                               signal_[channel_], fields)

            for channel_ in ["stop", "zjets", "wjets", "ttbar"]:
                if channel_ not in background_:
                    continue

                print_function(channel_names.get(channel_, channel_),
                               background_[channel_], fields)

            print_function("Total MC", total_background_, fields)

            if data_:
                print_function("Data 2011", data_, fields)

            print()

        return None
