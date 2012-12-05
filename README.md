# Summary

```exo_plot``` is a plotting tool for Exotica searches in the High Energy
Physics.

The input is a set of [ROOT](http://root.cern.ch) files, one per physics
input, e.g. ```wjets```, ```ttbar```, ```stop_s```, ```stop_t```, etc.
Each file has the same structure of folders and histograms.

The tool will load input files and merge plots into channels, e.g.:
```stop``` channel is the sum of inputs ```stop_s```, ```stop_t```,
```stop_tw```, ```satop_s```, etc.

Finally ```exo_plot``` will draw only those plots, that user asked for.

Read
[INSTALL](https://github.com/ksamdev/exo_plots/blob/master/INSTALL.md)
instructions before using it.


# Configurable

The tool is highly customizable with [YAML](http://www.yaml.org) configuration
files. It uses two configs:

* [channel config](https://github.com/ksamdev/exo_plots/blob/master/config/2012.input.yaml)
  the description of inputs, such as ```ttbar```, ```stop_t```, ```satop_tw```,
  their normalization (if any has to be applied), the collisions energy,
  luminosity; the file also describes how inputs should be merged into channels,
  e.g. ```zjets``` channel is the sum of inputs ```dy_10to50``` and
  ```dy_50toinf```; it also defines the color for each channel, if the plot has
  to be filled and line style; finally channels plotting order is defined at
  the end (any unspecified channel will be added to the bottom in random
  order) and channels abbreviations via regular expressions, e.g. ```mc```
  will load channels ```ttbar```, ```wjets```, ```zjets``` and some more
  instead of specifying each channel separately
* [plot config](https://github.com/ksamdev/exo_plots/blob/master/config/2012.plot.yaml)
  here each plot parameters are described such as rebinning, user-range,
  x-title axis 

Some parameters can be also configured with enviroment variables. These
include:

```EXO_PLOT_LABEL```  set label to plots
```EXO_PLOT_TFF_INPUT```  set the input plot for the TFractionFitter

Command line argument overrides enviroment variable value if used.

# Inputs

The input ROOT files should follow the name scheme: ```prefix.input.root```,
where ```prefix``` may be any string, ```input``` has to match that in the
channel config, e.g. ```stop_s```.

All files should have the same structure.


# Examples

The most basic script is ```tempalate/template_main.py```. It will load files,
and plot data vs background for all loaded plots. Run script without arguments
to get help or use ```-h``` or ```--help``` options.

Common example when using zprime sframe production

```bash
/.../exo_plots/preselection/template_main.py --prefix ZprimeSelectionCycle --channels data,zjets,wjets,ttbar,stop,qcd,diboson --channel-config 2012.input.yaml --plot-config 2012.plot.yaml --plots '/Event/MET:/Chi2/M_ttbar_rec' -s pdf -b -v --bg-error=4
```

The typical usage examples are given below


## Study at Monte-Carlo

All MC channels

```bash
# plot all MC channels only, histogram ABC
./template/template_main.py --channels mc --plots '/path/inside/file/ABC'
# plot histograms ABC and DEF for MC channels
./template/template_main.py --channels mc --plots '/path/inside/file/ABC:/path/inside/file/DEF'
# The script supports bash completion in the plot names, e.g:
# plot pt of jet1, jet2, jet3 from some path for MC channels
./template/template_main.py --channels mc --plots '/path/jet?_pt'
# plot pt of jet1 and jet2 only from some path for MC channels
./template/template_main.py --channels mc --plots '/path/jet[12]_pt'
# plot jet1 pt and eta plots from some path for MC channels
./template/template_main.py --channels mc --plots '/path/jet1_{pt,eta}'
```

Let's take a look at specific channels

```bash
# wjets channel only
./template/template_main.py --channels wjets --plots '/path/inside/file/ABC'
# wjets and zjets channels only
./template/template_main.py --channels wjets,zjets --plots '/path/inside/file/ABC'
```


## Compare MC to Data

```bash
# compare MC to data for plot ABC
./template/template_main.py --channels mc,data --plots '/path/inside/file/ABC'
# compare wjets+zjets to data for plot ABC
./template/template_main.py --channels wjets,zjets,data --plots '/path/inside/file/ABC'
# comare all MC but zjets to data for plot ABC: turn off channel with minus
./template/template_main.py --channels mc,-zjets,data --plots '/path/inside/file/ABC'
```


# Custom Config

Sometimes it is necessary to make a small modification to channels or plot
config. Instead of changing the global config in the
[config folder](https://github.com/ksamdev/exo_plots/tree/master/config)
simply copy it, change and run the script with corresponding option, e.g.:

```bash
# use custom channel config
./template_main.py --channel-config my_channel_config.yaml
# use custom plot config
./template_main.py --plot-config my_plot_config.yaml
```

# Further reading

The project documentation is bundled to the package and available in the
[docs folder](https://github.com/ksamdev/exo_plots/tree/3847e421d9a24e1d5b5bd21c01dad15dd18e8b12/docs)
: simply open md files in online with GitHub.

# What's next?

Welcome to the project! Start changing the code and sharing your ideas with
others. Follow these
[basic instructions](https://github.com/ksamdev/exo_plots/blob/master/docs/howto_modify.md)
on how to contribute to the project: clone, change code, create pull request
and your fix or improvement will be added to the package.
