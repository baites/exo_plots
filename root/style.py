#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 19, 2012
Copyright 2012, All rights reserved
'''

from array import array
import ROOT

def analysis():
    '''
    Exotica Analisis Note style - based on TDR
    '''

    style = ROOT.TStyle("exo_an_style", "CMS Exotica for Analysis Note")

    # Canvas
    style.SetCanvasBorderMode(0)
    style.SetCanvasColor(ROOT.kWhite)
    style.SetCanvasDefH(600) # height, width
    style.SetCanvasDefW(600)
    style.SetCanvasDefX(0)   # position x, y
    style.SetCanvasDefY(0)

    # Pad
    style.SetPadBorderMode(0)
    style.SetPadColor(ROOT.kWhite)
    style.SetPadGridX(True)
    style.SetPadGridY(True)
    style.SetGridColor(ROOT.kGray + 2)
    style.SetGridStyle(3)
    style.SetGridWidth(1)

    # Margins:
    style.SetPadLeftMargin(0.20)
    style.SetPadRightMargin(0.05)
    style.SetPadBottomMargin(0.15)
    style.SetPadTopMargin(0.10)

    # For the frame:
    style.SetFrameBorderMode(0)
    style.SetFrameBorderSize(1)
    style.SetFrameFillColor(0)
    style.SetFrameFillStyle(0)
    style.SetFrameLineColor(1)
    style.SetFrameLineStyle(1)
    style.SetFrameLineWidth(1)

    # Stats box
    style.SetOptFile(0)
    style.SetOptStat(0) # hide
    style.SetStatColor(ROOT.kWhite)
    style.SetStatFont(42)
    style.SetStatFontSize(0.035)
    style.SetStatTextColor(1)
    style.SetStatFormat("6.4g")
    style.SetStatBorderSize(1)
    style.SetStatH(0.5)
    style.SetStatW(0.4)

    # legends
    style.SetLegendBorderSize(0)

    # For the histo:
    style.SetHistLineColor(ROOT.kBlack)
    style.SetHistLineStyle(0)
    style.SetHistLineWidth(2)
    style.SetEndErrorSize(2)
    style.SetMarkerStyle(ROOT.kFullCircle)
    style.SetMarkerSize(2)
    style.SetOptTitle(0) # Hide histogram title
    style.SetHatchesSpacing(0.75)
    style.SetHatchesLineWidth(1)

    # axis titles:
    style.SetTitleColor(ROOT.kBlack, "xyz")
    style.SetTitleFont(62, "xyz")
    style.SetTitleOffset(1., "x")
    style.SetTitleOffset(1.5, "y")
    style.SetTitleSize(0.06, "xyz")

    # axis labels:
    style.SetLabelColor(ROOT.kBlack, "xyz")
    style.SetLabelFont(42, "xyz")
    style.SetLabelOffset(0.007, "xyz")
    style.SetLabelSize(0.05, "xyz")

    # axis
    style.SetAxisColor(ROOT.kBlack, "xyz")
    style.SetStripDecimals(True)
    style.SetTickLength(0.03, "xyz")
    style.SetNdivisions(8, "xyz")

    #For the fit/function:
    style.SetOptFit(0)
    style.SetFitFormat("5.4g")
    style.SetFuncColor(ROOT.kAzure + 4)
    style.SetFuncStyle(1)
    style.SetFuncWidth(1)

    #For the date:
    style.SetOptDate(0)

    # Log plots:
    style.SetOptLogx(0)
    style.SetOptLogy(0)
    style.SetOptLogz(0)

    # 2D Plots palette
    #
    red = array('d', [ 0.60, 0.00, 0.00, 0.00, 1.00, 1.00, 1.00])
    green = array('d', [ 0.00, 0.00, 0.60, 1.00, 1.00, 0.60, 0.00])
    blue = array('d', [ 1.00, 1.00, 1.00, 0.00, 0.00, 0.00, 0.00])
    length = array('d', [ 0.00, 0.17, 0.34, 0.51, 0.68, 0.85, 1.00])

    ROOT.TColor.CreateGradientColorTable(len(red), length, red, green, blue, 50)

    # There is no way to chane all TLegend fill colors to whie through TStyle... wrap constructor
    def style_legend(wrapped):
        def init(self, *parg, **karg):
            wrapped(self, *parg, **karg)

            self.SetFillColor(ROOT.kWhite)
            self.SetBorderSize(0)

        # Copy documentation string for interactive help
        init.__doc__ = wrapped.__doc__

        return init

    ROOT.TLegend.__init__ = style_legend(ROOT.TLegend.__init__)


    # do the same with all TLatex
    def style_latex(wrapped):
        def init(self, *parg, **karg):
            wrapped(self, *parg, **karg)

            self.SetNDC()
            self.SetTextFont(62)

        init.__doc__ = wrapped.__doc__

        return init

    ROOT.TLatex.__init__ = style_latex(ROOT.TLatex.__init__)

    return style

def pas():
    style = analysis()

    style.SetPadGridX(False)
    style.SetPadGridY(False)

    return style
