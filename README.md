# What? How?

exo\_plot is a plotting tool for Exotica searches in the High Energy Physics.

The input is defined by [ROOT](http://root.cern.ch) files with bunch of
historams save in each file. The tool expects one root file to be present per
input to be loaded. For example:

* 2011.ttbar.root
* 2011.wjets.root
* 2011.run2011a.root
* 2011.run2011b.root
* 2011.signal.root

Input plots are automatically normalized to cross-sections, luminosity when 
loaded according to the
[configuration file](https://github.com/ksamdev/exo_plots/blob/c48160b2ccd5f16543af2f29c47f9d5a036d0ba3/config/2011.input.yaml#L50-52).
Each plots is rebinned. Its axis titles with units are set according to the
predefined [user configuation](https://github.com/ksamdev/exo_plots/blob/16efdd82a1d27a9e7a5de720de374c51d91e8579/config/2011.plot.yaml#L42-45).

Finally, histograms from different inputs are merged into channels and basic
styles are applied such as color, line style, etc. according to
[user configuration](https://github.com/ksamdev/exo_plots/blob/c48160b2ccd5f16543af2f29c47f9d5a036d0ba3/config/2011.input.yaml#L266-271).

For example *data* channel is the merge of _2011.run2011a.root_ and 
_2011.run2011b.root_ inputs.

At the end the plotting tool will stack backgrounds if any are loaded and draw
these with error band. The data and signal will be overlayed.

# Example

User may define which channels to load, e.g.:

```bash
# plot Monte-Carlo only
./template_main.py --channels mc
# plot signal only
./template_main.py --channels zp
# plot signal and monte-carlo
./template_main.py --channels mc,zp
# plot signal and monte-carlo except zjets
./template_main.py --channels mc,zp,-zjets
# plot data background comparison
./template_main.py --channels mc,data
```

The tool is highly flexible for run and can easily be extended to add more
featured depending on the analysis carried.

```bash
# run in batch mode
./template_main.py -b
# print debug information (useful for developing)
./template_main.py -v
# save plots in PDF
./template_main.py -s pdf
# get HELP 
./template_main.py
./template_main.py -h
```

# Further reading

The project documentation is bundled to the package and available in the
[docs](https://github.com/ksamdev/exo_plots/tree/3847e421d9a24e1d5b5bd21c01dad15dd18e8b12/docs)
folder.

# What's next?

Welcome to the project! Start changing the code and sharing your ideas with
others. Follow these [basic instructions](https://github.com/ksamdev/exo_plots/blob/master/docs/howto_modify.md)
on how to contribute to the project.
