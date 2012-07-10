## [template.templates](https://github.com/ksamdev/exo_plots/blob/master/template/templates.py)

```Templates``` is the base plots analyzer. Its purpose is:

1. Parse command line options, arguments
2. Load application, input and plot configurations, scales, etc.
3. When run:
    - apply standard ROOT style
    - load templates
    - plot histograms
    - save canvases if asked to

The ```Templates``` class will plot all loaded channels by default. However,
child classes may redefine some of its functionality to extend the analysis.

## Example: compare background shapes

The idea is to plot **only** backgrounds overlayed to compare the shapes. Let
user still specify what channels to load and process only these in the
```Templates::plot``` method, e.g.:

```python
from __future__ import division # for python 2.x

import ROOT

from config import channel
from template import templates

class Backgrounds(templates.Templates):
    def __init__(self, options, args, config):
        templates.Templates.__init__(self, options, args, config)

    def plot(self):
        # store all plotted canvases (one per histogram) in array
        canvases_ = []

        # use abbreviation for backgrounds and auto-expand into channels
        bg_channels_ = set(["mc", "qcd"])
        channel.expand(self._channel_config, bg_channels_)

        # loop over all loaded plots and process only background channels
        for plot_, channels_ in self.plots.items():
            background_ = ROOT.THStack()
            legend_ = ROOT.TLegend(0, 0, 0, 0) # coords will be adjusted

            # process only background channels
            for channel_ in channels_:
                if channel_ not in bg_channels_:
                    continue

                hist = channels_[channel_]

                # Remove fill from plot and keep only stroke
                hist.SetLineColor(hist.GetFillColor())
                hist.SetLineStyle(1)
                hist.SetLineWidth(2)

                # normalize for shape comparison
                hist.Scale(1 / hist.Integral())

                background_.Add(hist)

                # use channel name as specified in the config
                legend_.AddEntry(hist, self._channel_config["channel"][channel_]
                                                           ["legend"], "l")

            canvas_ = self.draw_canvas(plot_, background=background_,
                                       legend=legend_, uncertainty=False)
            if canvas_:
                canvases_.append(canvas_)

        return canvas_

    def draw(self, background=None, uncertainty=None, data=None, signal=None):
        ''' Plot only backgrounds '''

        if background:
            background.Draw("9 hist same nostack")
```
