#!/usr/bin/env python

'''
Victor E. Bazterra UIC 2012
'''

from __future__ import print_function, division

import math
import os
import sys

import ROOT

from config import channel
from root import stats
from template import templates

class Templates(templates.Templates):

    def __init__(self, options, args, config):
        options.plots = '/BTagEff_Chi2sel/*'
        templates.Templates.__init__(self, options, args, config)
        self._label = options.label or os.getenv("EXO_PLOT_LABEL", None)
        self._btag = {}

    def load(self):
        # Run default loading
        templates.Templates.load(self)

        mc_channels = set(["mc", ])
        channel.expand(self._channel_config, mc_channels)

        for var in ['pt', 'eta', 'phi']:
            for flavor in ['b', 'c', 'l']:
                key = '%s_%cjet' % (var, flavor)
                input = '/BTagEff_Chi2sel/%s_%cJet' % (var, flavor)
                for channel_, plot_ in self.plots[input].items():
                    if "data" == channel_ or "qcd" == channel_:
                        break
                    elif channel_ in mc_channels:
                        if key in self._btag:
                            self._btag[key].Add(plot_)
                            self._btag[key+'_btag'].Add(self.plots[input+'_bTag'][channel_])
                        else:
                            self._btag[key] = plot_.Clone()
                            self._btag[key+'_btag'] = self.plots[input+'_bTag'][channel_].Clone()


    def plot(self):

        canvases = [] 

        for var in ['pt', 'eta', 'phi']:

            efficiencies = []
            legend = ROOT.TLegend(0, 0, 0, 0)

            for flavor in ['b', 'c', 'l']:
                key = '%s_%cjet' % (var, flavor)
                efficiency = ROOT.TGraphAsymmErrors();
                efficiency.Divide(self._btag[key+'_btag'], self._btag[key], 'cl=0.683 b(1,1) mode');
                if flavor == 'b':
                    efficiency.SetLineColor(ROOT.kBlue);
                    efficiency.SetMarkerColor(ROOT.kBlue);
                elif flavor == 'c':
                    efficiency.SetLineColor(ROOT.kGreen);
                    efficiency.SetMarkerColor(ROOT.kGreen);            
                else:
                    efficiency.SetLineColor(ROOT.kRed);
                    efficiency.SetMarkerColor(ROOT.kRed);    
                efficiencies.append(efficiency)
                legend.AddEntry(efficiency, '%c-jets' % flavor, 'l')

                if var == 'pt':
                    bins = []
                    effs = []
                    abins = self._btag[key].GetXaxis().GetXbins()
                    for i in range(abins.GetSize()):
                        bins.append(abins[i])
                    for i in range(1,self._btag[key].GetNbinsX()+1):
                        effs.append(efficiency.Eval(self._btag[key].GetBinCenter(i)))
                    print('Efficiencies for %c-flavor' % flavor)
                    print(bins)
                    print(effs)
                    print()

            axisname = 'Jet p_{T} [GeV/c]'
            if var == 'phi':
                axisname = 'Jet #phi'
            elif var == 'eta':
                axisname = 'Jet #eta'
            
            canvas = self.draw_efficiency_canvases(
                'btageff_%s' % var,
                axisname,
                efficiencies=efficiencies,
                legend=legend
            )

            if canvas:
                canvases.append(canvas)

        return canvases        


    def draw_efficiency_canvases(self, plotname, axisname, efficiencies,
                                 legend, is_data=False):
        '''
        Draw canvas with efficiencies, legend and labels

        Efficiencies is the array of efficieny plots. The legend
        coordinates are automatically adjusted to make it readable.
        '''

        name = 'c_' + plotname.lstrip('/').replace('/', '_')
        canvas = ROOT.TCanvas(name, "")
        canvas.SetLogy()
        canvas.objects = { "efficiencies": efficiencies }

        multigraph = ROOT.TMultiGraph()
        canvas.objects["multigraph"] = multigraph        

        for efficiency in efficiencies:
            multigraph.Add(efficiency)
        
        multigraph.Draw('9 ap')
        multigraph.GetXaxis().SetTitle(axisname)
        multigraph.GetYaxis().SetTitle('Efficiency')
        multigraph.GetYaxis().SetRangeUser(1.e-4, 10.0)

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

