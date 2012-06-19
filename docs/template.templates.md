## [template.templates](https://github.com/ksamdev/exo_plots/blob/master/template/templates.py)

Templates plotting core. It loads channel and plots configuration files,
templates from input ROOT files, adjusts these and plots histograms.

Extend this class to add more sophisticated analysis. For example, consider the
case when QCD channel needs to be scaled down by 50%.
plots scale:

```python
from template import templates

class QCDScaleTemplates(templates.Templates):
    def __init__(self, *parg, **karg):
        templates.Templates.__init__(self, *pargs, **karg)

    def run(self):
        # Apply styles
        self.load()
        self.scale() # < this is the extended scale
        self.plot()

    def self.scale():
        for plot, channels in self.plots.items():
            qcd = channels.get("qcd", None)
            if qcd:
                qcd.Scale(0.5)
```

As you see, the code will work the same way as the original templates plotting
tool but with altered QCD channel.
