## [template.loader.py](https://github.com/ksamdev/exo_plots/blob/master/template/loader.py)

All histograms are kept in separate file per input, e.g. ttbar, wlight, wb,
zjets, data_spring_2011, data_summer_2011, etc.

```InputLoader``` will load into memory each input independently and read only
these histograms from file that are defined though arguments.

The ```ChannelLoader``` is responsible for loading the whole channel which
consists of at least one input, e.g.: load each input, process it and finally
merge inputs into channel.

## InputLoader

Load plots that are specified in patterns. The patterns is an array such that
each entry represents path inside ROOT file to plot to be loaded, e.g.:

```
/njets
/jet1/pt
```

The [BASH wildcards](http://www.tuxfiles.org/linuxhelp/wildcards.html) are
accepted. For example, consider folder structure:

```
/jet1/pt
/jet1/eta
/jet2/pt
/jet2/eta
/jet3a/pt
/jet3a/eta
```

In this case, the below paths would be expanded to:

* ```/jet?/pt```
  load all jet1 and jet2 pT
* ```/jet*/eta```
  load all jets pT
* ```/jet[1-2]/pt```
  load jet1 and jet1 pt
* ```/jet[!1-2]/eta```
  load only jet3a eta
* ```/jet{1,3a}/eta```
  load jet1 and jet3a eta
* ```/jet1/*```
  load all jet properties

**WARNING**: _only 1D plots are loaded by default - extend the Loader for 2D
plots_

## ChannelLoader

The channel loader is responsible for:

1. load all inputs that go into channel
2. scale each input according to x-section, luminosity and number of processed
   events
3. merge loaded inputs into channel
4. style plots, e.g. change color, fill, line, rebin, set title axis, etc.

The channel loader uses input and plot configurations.
