#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jul 13, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function, division

import math
import os
import sys

import ROOT

from config import channel
from root import stats
from template import templates

def efficiency(pass_, total_):
    if not pass_ or not pass_[0] or not total_ or not total_[0]:
        return (0, 0)

    a = pass_[0]
    b = total_[0]

    sa = pass_[1]
    sb = total_[1]

    return (a / b, (b * sa - a * sb) / b ** 2)

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
            "met": stats_(hist, 16),
            "chi2": stats_(hist, 19),
            "non_threshold": stats_(hist, 20)
            }

def format_stats(stats, sep="+-", is_header=False, is_efficiency=False):
    if is_header:
        return "{0:^{1}}".format(stats, 15 + len(sep))
    elif is_efficiency:
        return "{0:>8.2f} {sep} {1:<5.2f}".format(*stats, sep=sep)
    else:
        return "{0:>8.0f} {sep} {1:<5.0f}".format(*stats, sep=sep)

def print_cutflow_in_text(channel, cutflow,
                          fields=["jets", "electron", "veto_lepton",
                                  "twod_cut", "jet1", "htlep", "tricut",
                                  "met"]):
    cells = ["{0:>20}".format(channel if channel else "Channel"), ]
    for field_ in fields:
        if channel:
            cells.append(format_stats(cutflow[field_], is_efficiency=True)
                         if "eff" == field_ else format_stats(cutflow[field_]))
        else:
            cells.append(format_stats(field_, is_header=True))
    print(*cells, sep=" | ")

    if not channel:
        # print header separation line
        new_cells = []
        for cell in cells:
            new_cells.append('-' * len(cell))
        print(*new_cells, sep=" + ")


def print_cutflow_in_tex(channel, cutflow,
                         fields=["jets", "electron", "veto_lepton",
                                 "twod_cut", "jet1", "htlep", "tricut",
                                 "met"]):
    if not channel:
        return

    cells = [channel, ]
    for field_ in fields:
        cells.append(format_stats(cutflow[field_], sep="&"))
    print(*cells, sep=" & ", end=" \\\\\n")

class Cutflow(templates.Templates):
    ''' Produce S / B plot '''

    def __init__(self, options, args, config):
        templates.Templates.__init__(self, options, args, config)

        self._print_mode = options.mode
        self._non_threshold = options.non_threshold

    def plot(self):
        ''' Process loaded histograms and draw these '''

        # the main executable script should make sure only one plot is loaded:
        # /cutflow or /cutflow_no_weight
        channels = self.plots[self.plots.keys().pop()]

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
                #"wjets": r"$W\rightarrow l\nu$",
                "wb": r"$W\rightarrow l\nu$ (bX)",
                "wc": r"$W\rightarrow l\nu$ (cX)",
                "wlight": r"$W\rightarrow l\nu$ (lightX)",
                "ttbar": r"QCD $t\bar{t}$",
                } if "text" != self._print_mode else {
                "zprime_m1000_w10": r"Z' 1 Tev",
                "zprime_m2000_w20": r"Z' 2 Tev",
                "zprime_m3000_w30": r"Z' 3 Tev",
                "stop": r"Single-Top",
                "zjets": r"Z/gamma -> l+ l-",
                #"wjets": r"W -> l nu",
                "wb": r"W-> l nu (bX)",
                "wc": r"W-> l nu (cX)",
                "wlight": r"W-> l nu (lightX)",
                "ttbar": r"QCD ttbar",
                }

        print_function = (print_cutflow_in_text
                          if self._print_mode == "text"
                          else print_cutflow_in_tex)

        fields_to_print = [["jets", "electron", "veto_lepton", "twod_cut"],
                           ["jet1", "htlep", "tricut", "met"]]
        if self._non_threshold:
            fields_to_print.append(["chi2", "non_threshold", "eff"])
            for samples_cutflow_ in (signal_, background_):
                if not samples_cutflow_:
                    continue

                for channel_, cutflow_ in samples_cutflow_.items():
                    cutflow_["eff"] = efficiency(cutflow_.get("non_threshold", 0),
                                                 cutflow_.get("chi2", 0))

            for cutflow_ in (total_background_, data_):
                    cutflow_["eff"] = efficiency(cutflow_.get("non_threshold", 0),
                                                 cutflow_.get("chi2", 0))

        for fields in fields_to_print:
            print_function(None, None, fields)

            for channel_ in self._channel_config["order"]:
                if (not channel_.startswith("zprime") or
                    channel_ not in signal_):

                        continue

                print_function(channel_names.get(channel_, channel_),
                               signal_[channel_], fields)

            for channel_ in ["stop", "zjets", "wb", 'wc', 'wlight', "ttbar"]:
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
        
        self._tff_input = options.tff_input or os.getenv("EXO_PLOT_TFF_INPUT",
                                                         '/Event/MET')
        options.plots = options.plots + ':%s' % self._tff_input
        
        templates.Templates.__init__(self, options, args, config)

        self._label = options.label or os.getenv("EXO_PLOT_LABEL", None)


    def load(self):
        # Run default loading
        templates.Templates.load(self)

        # Run TFraction Fitter to get MC and QCD scales
        try:
            if self._verbose:
                print("{0:-<80}".format("-- TFractionFitter "))

            if (self._tff_input not in self.plots):
                raise RuntimeError("load plot " + self._tff_input)

            # Extract met DATA, QCD and MC
            met = {}
            mc_channels = set(["mc", ])
            channel.expand(self._channel_config, mc_channels)
            for channel_, plot_ in self.plots[self._tff_input].items():
                if "data" == channel_:
                    met["data"] = plot_
                elif "qcd" == channel_:
                    met["qcd"] = plot_
                elif channel_ in mc_channels:
                    if "mc" in met:
                        met["mc"].Add(plot_)
                    else:
                        met["mc"] = plot_.Clone()

            print (met.keys())

            missing_channels = set(["data", "qcd", "mc"]) - set(met.keys())
            if missing_channels:
                raise RuntimeError("channels {0!r} are not loaded".format(
                                    missing_channels))

            # prepare variable tempaltes for TFractionFitter
            templates_ = ROOT.TObjArray(2)
            templates_.Add(met['mc'])
            templates_.Add(met["qcd"])

            # Setup TFractionFitter
            fitter = ROOT.TFractionFitter(met["data"], templates_)

            # Run TFRactionFitter
            fit_status = fitter.Fit()
            if fit_status:
                raise RuntimeError("fitter error {0}".format(fit_status))

            # Extract MC and QCD scales from TFractionFitter and keep
            # only central values (drop errors)
            fraction = ROOT.Double(0)
            fraction_error = ROOT.Double(0)
            fractions = {}
            fraction_errors = {}
            scales = {}
            scale_errors = {}

            data_integral_ = met["data"].Integral(0,met["data"].GetNbinsX()+1)
            qcd_integral_ = met["qcd"].Integral(0,met["qcd"].GetNbinsX()+1)
            mc_integral_ = met["mc"].Integral(0,met["mc"].GetNbinsX()+1)

            mc_integral_error_ = 0.0
            for i in range(0,met["mc"].GetNbinsX()+2):
                mc_integral_error_ = mc_integral_error_ + met["mc"].GetBinError(i)**2
            mc_integral_error_ = math.sqrt(mc_integral_error_) / mc_integral_

            fitter.GetResult(0, fraction, fraction_error)
            fractions["mc"] = float(fraction)
            fraction_errors["mc"] = float(fraction_error) / float(fraction)
            scales["mc"] = float(fraction) * data_integral_ / mc_integral_
            scale_errors["mc"] = math.sqrt(
                (1/data_integral_) + mc_integral_error_**2 + fraction_errors["mc"]**2
            )

            fitter.GetResult(1, fraction, fraction_error)
            fractions["qcd"] = float(fraction)
            fraction_errors["qcd"] = float(fraction_error) / float(fraction)
            scales["qcd"] = float(fraction) * data_integral_ / qcd_integral_
            scale_errors["qcd"] = math.sqrt(
                (1/data_integral_) + mc_integral_error_**2 + fraction_errors["qcd"]**2
            )

            # Print found fractions
            if self._verbose:
                print('\n'.join("{0:>3} fraction: {1:.3f} +- {2:.1f}%".format(key.upper(),
                                                                  value, 100*fraction_errors[key])
                                for key, value in fractions.items()))
                print('\n'.join("{0:>3} scale: {1:.3f} +- {2:.1f}%".format(key.upper(),
                                                                  value, 100*scale_errors[key])
                                for key, value in scales.items()))

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
                for channel_, hist_ in channels_.items():
                    if channel_ in mc_channels:
                        hist_.Scale(scales["mc"])
                    elif "qcd" == channel_:
                        hist_.Scale(scales["qcd"])

        except RuntimeError as error:
            if self._verbose:
                print("failed to use TFractionFitter - {0}".format(error),
                      file = sys.stderr)

        finally:
            if self._verbose:
                print()
