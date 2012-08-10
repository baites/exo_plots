#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jul 05, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function, division

import math

import ROOT

from config import channel
from root import stats
from template import templates

class Efficiency(templates.Templates):
    def __init__(self, options, args, config):
        templates.Templates.__init__(self, options, args, config)

        self._legend_align = "left"
        self._legend_valign = "bottom"

    def plot(self):
        ''' Process loaded histograms and draw these '''

        canvases = []

        # extract channels
        electron_ref = self.plots["/electron_ref/pt"]
        electron_ref_test = self.plots["/electron_ref_test/pt"]

        for channel, plot in electron_ref_test.items():
            if channel not in electron_ref:
                raise RuntimeError("{1} is missing in channel {0}".format(
                                     channel, plot.GetName()));

            efficiency = ROOT.TGraphAsymmErrors()
            efficiency.Divide(plot, electron_ref[channel],
                              "cl=0.683 b(1,1) mode")
            self.copy_axis_style(plot, efficiency)
            efficiency.SetMarkerColor(ROOT.kBlack)
            efficiency.SetMarkerSize(1)
            efficiency.SetMarkerStyle(8)
            efficiency.SetLineColor(ROOT.kBlack)
            efficiency.SetLineStyle(1)
            efficiency.SetLineWidth(1)

            legend = ROOT.TLegend(0, 0, 0, 0)
            legend.AddEntry(efficiency,
                            self._channel_config["channel"][channel]
                                                ["legend"], 'l')

            xaxis = plot.GetXaxis()
            fit_function = ROOT.TF1("fit_" + channel, "pol0",
                                    xaxis.GetBinLowEdge(xaxis.GetFirst()),
                                    xaxis.GetBinUpEdge(xaxis.GetLast()))

            result = efficiency.Fit("fit_" + channel, "NE")
            if not result:
                fit_function = None
            else:
                fit_function.SetLineWidth(3)
                fit_function.SetLineStyle(1)
                fit_function.SetLineColor(ROOT.kRed + 1)

                fit_function.SetMarkerSize(0)

                legend.AddEntry(fit_function,
                                "Fit: {0:.3f} +/- {1:.3f}".format(
                                    fit_function.GetParameter(0),
                                    fit_function.GetParError(0)),
                                'l')

            canvas = self.draw_efficiency_canvases(
                            "trigger_eff_" + channel,
                            axis=plot,
                            efficiencies=(efficiency,),
                            legend=legend,
                            is_data=("data" == channel),
                            functions=(fit_function,))
            if canvas:
                canvases.append(canvas)

        return canvases

    def draw_efficiency_canvases(self, plot_name,
                                 axis, efficiencies,
                                 legend, is_data=False,
                                 functions=[]):
        '''
        Draw canvas with efficiencies, legend and labels

        Efficiencies is the array of efficieny plots. The legend
        coordinates are automatically adjusted to make it readable.
        '''

        name = 'c_' + plot_name.lstrip('/').replace('/', '_')
        canvas = ROOT.TCanvas(name, "")

        canvas.objects = { "efficiencies": efficiencies }

        xaxis = axis.GetXaxis()
        for efficiency in efficiencies:
            efficiency.GetYaxis().SetTitle("Trigger Efficiency")
            efficiency.GetXaxis().SetRangeUser(
                    xaxis.GetBinLowEdge(xaxis.GetFirst()),
                    xaxis.GetBinUpEdge(xaxis.GetLast()))
            efficiency.SetMinimum(0)
            efficiency.SetMaximum(1.2)

        if efficiencies:
            multigraph = ROOT.TMultiGraph()
            canvas.objects["multigraph"] = multigraph

            canvas.objects["graphs"] = []
            for function in functions:
                if function:
                    graph = ROOT.TGraph(function)
                    canvas.objects["graphs"].append(graph)

                    graph.SetLineStyle(function.GetLineStyle())
                    graph.SetLineWidth(function.GetLineWidth())
                    graph.SetLineColor(function.GetLineColor())

                    multigraph.Add(graph, "l")

            for eff in efficiencies:
                multigraph.Add(eff)

            multigraph.Draw("9 ap")

            multigraph.GetXaxis().SetRangeUser(
                    xaxis.GetBinLowEdge(xaxis.GetFirst()),
                    xaxis.GetBinUpEdge(xaxis.GetLast()))
            multigraph.GetXaxis().SetTitle(xaxis.GetTitle())
            multigraph.GetYaxis().SetTitle(
                    efficiencies[0].GetYaxis().GetTitle())
            multigraph.GetYaxis().SetRangeUser(0, 1.2)

        if legend:
            self.draw_legend(legend, width=0.34)
            canvas.objects["legend"] = legend

        # Add experiment label
        canvas.objects["experiment-label"] = self.draw_experiment_label(is_data)

        if self._label:
            canvas.objects["user-label"] = self.draw_label()

        if self._sub_label:
            canvas.objects["sub-label"] = self.draw_sub_label()

        # re-draw everything for nice look
        canvas.Update()

        return canvas

    def copy_axis_style(self, source, destination):
        destination.SetLineWidth(source.GetLineWidth())
        destination.SetLineColor(source.GetLineColor())
        destination.SetMarkerStyle(source.GetMarkerStyle())
        destination.SetMarkerSize(source.GetMarkerSize())



class Validation(Efficiency):
    def __init__(self, options, args, config):
        Efficiency.__init__(self, options, args, config)

    def plot(self):
        ''' Process loaded histograms and draw these '''

        canvases = []

        # extract channels
        electron = self.plots["/electron/pt"]
        electron_test = self.plots["/electron_test/pt"]
        electron_ref = self.plots["/electron_ref/pt"]
        electron_ref_test = self.plots["/electron_ref_test/pt"]

        for channel, plot in electron_ref_test.items():
            if (channel not in electron_ref or
                channel not in electron_test or
                channel not in electron):
                raise RuntimeError("{1} is missing in channel {0}".format(
                                     channel, plot.GetName()));

            legend = ROOT.TLegend(0, 0, 0, 0)
            legend.SetHeader(self._channel_config["channel"][channel]
                                                 ["legend"])

            mc_method_efficiency = ROOT.TGraphAsymmErrors();
            mc_method_efficiency.Divide(electron_test[channel],
                                        electron[channel],
                                        "cl=0.683 b(1,1) mode")
            self.copy_axis_style(plot, mc_method_efficiency)
            mc_method_efficiency.SetLineColor(ROOT.kBlack)
                            
            efficiency = ROOT.TGraphAsymmErrors();
            efficiency.Divide(plot, electron_ref[channel],
                              "cl=0.683 b(1,1) mode")
            self.copy_axis_style(plot, efficiency)
            efficiency.SetLineColor(ROOT.kRed + 1)

            legend.AddEntry(mc_method_efficiency, "MC Truth Method", "l")
            legend.AddEntry(efficiency, "Trigger Method", "l")

            canvas = self.draw_efficiency_canvases(
                            "validation_" + channel,
                            axis=plot,
                            efficiencies=(mc_method_efficiency, efficiency),
                            legend=legend,
                            is_data=("data" == channel))

            if canvas:
                canvases.append(canvas)

        return canvases

    def draw(self, background=None, uncertainty=None, data=None, signal=None):
        ''' Let sub-classes redefine how each template should be drawn '''

        if signal:
            signal.Draw("9 hist same nostack e1")
