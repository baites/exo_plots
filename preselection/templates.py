#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jul 13, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function, division

import math
import sys

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
                "ttbar": r"QCD $t\bar{t}$",
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

class Templates(templates.Templates):
    def __init__(self, options, args, config):
        templates.Templates.__init__(self, options, args, config)

    def load(self):
        # Run default loading
        templates.Templates.load(self)

        # Run TFraction Fitter to get MC and QCD scales
        try:
            if self._verbose:
                print("{0:-<80}".format("-- TFractionFitter "))

            if ("/met" not in self.plots or
                "/met_no_weight" not in self.plots):

                raise RuntimeError("load plots /met and /met_no_weight")

            # Extract met DATA, QCD and MC
            met = {}
            mc_channels = set(["mc", ])
            channel.expand(self._channel_config, mc_channels)
            for channel_, plot_ in self.plots["/met"].items():
                if "data" == channel_:
                    met["data"] = plot_
                elif "qcd" == channel_:
                    met["qcd"] = plot_
                elif channel_ in mc_channels:
                    if "mc" in met:
                        met["mc"].Add(plot_)
                    else:
                        met["mc"] = plot_.Clone()

            missing_channels = set(["data", "qcd", "mc"]) - set(met.keys())
            if missing_channels:
                raise RuntimeError("channels {0!r} are not loaded".format(
                                    missing_channels))

            met_noweight = None
            for channel_, plot_ in self.plots["/met_no_weight"].items():
                if channel_ in mc_channels:
                    if met_noweight:
                        met_noweight.Add(plot_)
                    else:
                        met_noweight = plot_.Clone()

            if not met_noweight:
                raise RuntimeError(("none of the channels {0!r} have "
                                    "/met_no_weight").foramt(mc_channels))

            # prepare MC weights for TFraction fitter
            mc_weights = met["mc"].Clone()
            mc_weights.Divide(met_noweight)

            # Set any zero bins to at least 1 event
            for bin_ in range(1, mc_weights.GetNbinsX() + 1):
                if 0 >= mc_weights.GetBinContent(bin_):
                    mc_weights.SetBinContent(bin_, 1)

            # prepare variable tempaltes for TFractionFitter
            templates_ = ROOT.TObjArray(2)
            templates_.Add(met_noweight)
            templates_.Add(met["qcd"])

            # Setup TFractionFitter
            fitter = ROOT.TFractionFitter(met["data"], templates_)
            fitter.SetWeight(0, mc_weights)

            # Run TFRactionFitter
            fit_status = fitter.Fit()
            if fit_status:
                raise RuntimeError("fitter error {0}".format(fit_status))

            # Extract MC and QCD fractions from TFractionFitter and keep
            # only central values (drop errors)
            fraction = ROOT.Double(0)
            fraction_error = ROOT.Double(0)
            fractions = {}

            fitter.GetResult(0, fraction, fraction_error)
            fractions["mc"] = float(fraction)

            fitter.GetResult(1, fraction, fraction_error)
            fractions["qcd"] = float(fraction)

            # Print found fractions
            if self._verbose:
                print('\n'.join("{0:>3} fraction: {1:.3f}".format(key.upper(),
                                                                  value)
                                for key, value in fractions.items()))

            # Scale all MC and QCD samples with fractions
            for plot_, channels_ in self.plots.items():
                # Skip normalization if one of the channels is missing
                if ("data" not in channels_ or 
                    "qcd" not in channels_):
                    continue

                # Get MC sum
                mc_sum_ = None
                for channel_, hist_ in channels_.items():
                    if channel_ in mc_channels:
                        if mc_sum_:
                            mc_sum_.Add(hist_)
                        else:
                            mc_sum_ = hist_.Clone()

                if not mc_sum_:
                    continue

                data_integral_ = channels_["data"].Integral()

                mc_scale = fractions["mc"] * data_integral_ / mc_sum_.Integral()
                for channel_, hist_ in channels_.items():
                    if channel_ in mc_channels:
                        hist_.Scale(mc_scale)
                    elif "qcd" == channel_:
                        hist_.Scale(fractions["qcd"] *
                                    data_integral_ / hist_.Integral())

        except RuntimeError as error:
            if self._verbose:
                print("failed to use TFractionFitter - {0}".format(error),
                      file = sys.stderr)

        finally:
            if self._verbose:
                print()
