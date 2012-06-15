#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Feb 23, 2012
Copyright 2011, All rights reserved
'''

import ROOT

def compare(function):
    '''
    Wrap ratio function and adjust style of the ratio plot

    example:

        @compare
        def simple_ratio(numerator, denominator):
            return numberator.Divide(denominator)
    '''

    def compare_decorator(*parg, **karg):
        '''
        wrapper around custom ratio calculator: adjust ratio plot style
        '''

        # let custom function calculate ratio and set all titles
        ratio_ = function(*parg, **karg)

        # adjust style of the ratio plot
        axis = ratio_.GetXaxis()
        axis.SetTitleSize(0.1)
        axis.SetTitleOffset(1.2)

        axis = ratio_.GetYaxis()
        axis.SetTitleSize(0.1)
        axis.SetTitleOffset(0.7)
        axis.SetNdivisions(4)
        axis.SetRangeUser(-1, 1)

        for axis in ratio_.GetYaxis(), ratio_.GetXaxis():
            axis.SetLabelSize(0.09)

        ratio_.SetMarkerSize(1)
        ratio_.SetMarkerStyle(20)
        ratio_.SetLineWidth(2)
        ratio_.SetLineColor(ROOT.kGray + 2)
        ratio_.SetLineStyle(1)
        ratio_.SetMarkerColor(ROOT.kBlack)

        return ratio_

    return compare_decorator

@compare
def ratio(numerator, denominator):
    '''Return ratio of two plots: numerator / denominator'''

    hist = numerator.Clone()
    hist.SetDirectory(0)
    hist.Reset()

    hist.Divide(numerator, denominator)

    return hist

@compare
def data_mins_bg_over_bg(data, background):
    '''Return ratio of two plots: (data - bg) / bg'''

    hist = data.Clone()
    hist.SetDirectory(0)

    hist.Add(background, -1)
    hist.Divide(background)

    return hist

class Canvas(object):
    '''
    Canvas with two pads:

        1   (top)       original plots should be drawn here
        2   (bottom)    comparison of the plots should be drawn in this pad

    It is recommended to use Canvas class in conjuction with compare
    decorator, e.g.:

        class DataMcCanvas(Canvas):
            ...

            @compare
            def ratio(self, data, mc):
                ratio = data.Clone()
                ratio.SetDirectory(0)

                ratio.Add(mc, -1)
                ratio.Divide(mc)
                ratio.GetYaxis().SetTitle("#frac{Data - MC}{MC}")

                return ratio

            def draw(self, data, mc):
                canvas = self.canvas
                canvas.cd(1)

                stack = ROOT.THStack()
                stack.Add(data)
                stack.Add(mc)
                stack.Draw("nostack hist 9")

                canvas.cd(2)
                self.ratio(data, mc).Draw("e 9")
            
            ...

    in the above example ratio method will be wrapped into compare decorator
    and comparison plot (ratio) style will be automatically adjusted

    Canvas is automatically created on acesss
    '''

    def __init__(self, pads=2, lazy_init=False):
        '''
        Initialize with empty canvas
        '''

        self._canvas = None
        self._pads = pads

        if not lazy_init:
            self._canvas = self._create_canvas()

    @property
    def canvas(self):
        '''
        Create canvas if one does not exist and split it into N pads.
        '''

        if not self._canvas:
            self._canvas = self._create_canvas()

        return self._canvas

    def _create_canvas(self):
        '''Create canvas object and split into specified nubmer of pads'''

        # create canvas
        canvas = ROOT.TCanvas()
        canvas.SetWindowSize(640, 560 if 1 == self._pads else 800)

        if 1 != self._pads:
            canvas.Divide(1, self._pads)

            # prepare top pad for original plots to be drawn overlayed
            pad = canvas.cd(1)
            pad.SetPad(0, 0.3, 1, 1)
            pad.SetMargin(0.15, 0.03, 0.1, 0.1)

            # prepare bottom pad for comparison/ratio draw
            pad_height = 0.3 / (self._pads - 1) if 1 != self._pads else 0.3
            for pad_number in range(1, self._pads):
                pad = canvas.cd(pad_number + 1)
                pad.SetPad(0, 0.3 - pad_number * pad_height,
                           1, 0.3 - (pad_number - 1) * pad_height)

                pad.SetMargin(0.15, 0.03, 0.1, 0.1)
                pad.SetGrid()

            canvas.cd(1)
        else:
            pad = canvas.cd(1)
            pad.SetMargin(0.15, 0.03, 0.15, 0.15)

        return canvas

if "__main__" == __name__:
    # Prepare function for later random fill
    my_gaus1 = ROOT.TF1("my_gaus1", "gaus(0)", 0, 100)
    my_gaus1.SetParameters(1, 50, 10)

    my_gaus2 = ROOT.TF1("my_gaus2", "gaus(0)", 0, 100)
    my_gaus2.SetParameters(1, 40, 10)

    # Create plot and randomly fill with above function
    plot1 = ROOT.TH1F("plot1", "plot1", 50, 0, 100)
    plot1.FillRandom("my_gaus1", 10000)
    plot1.SetLineColor(ROOT.kRed + 1)
    plot1.GetXaxis().SetTitle("jet P_{T} [GeV]")
    plot1.GetYaxis().SetTitle("event yield")

    plot2 = ROOT.TH1F("plot2", "plot2", 50, 0, 100)
    plot2.FillRandom("my_gaus2", 10000)
    plot2.GetXaxis().SetTitle("jet P_{T} [GeV]")
    plot2.GetYaxis().SetTitle("event yield")

    class ComparePlots(Canvas):
        '''Example of the compare canvas'''

        @staticmethod
        @compare
        def ratio(first, second):
            '''Simple ratio calculator'''

            ratio_ = first.Clone()
            ratio_.SetDirectory(0)
            ratio_.Reset()

            ratio_.Divide(first, second)
            ratio_.GetYaxis().SetTitle("#frac{" + first.GetName() +
                                      "}{" + second.GetName() + "}")

            return ratio_

        def __call__(self, first, second):
            canvas = self.canvas
            canvas.cd(1)

            stack = ROOT.THStack()
            stack.Add(first)
            stack.Add(second)
            stack.Draw("nostack hist 9")

            stack.GetXaxis().SetTitle(first.GetXaxis().GetTitle())
            stack.GetYaxis().SetTitle(first.GetYaxis().GetTitle())

            canvas.cd(2)
            ratio_ = ComparePlots.ratio(first, second)
            ratio_.GetXaxis().SetLabelSize(0)
            ratio_.Draw("e 9")

            canvas.Update()
            
            raw_input("enter")

    compare = ComparePlots()
    compare(plot1, plot2)
