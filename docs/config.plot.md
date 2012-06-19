## [config.plot.py](https://github.com/ksamdev/exo_plots/blob/master/config/plot.py)

Load YAML configuration for plots that defines plot rebinning, units, titles,
etc.

## Configuration

The required sections in the configuration file are:

* **plot** define all the information about each histogram

Depending on the distributions dimention different set of values is supported.
For the 1D plots next items are used:

* _name_ the plot name with full path with respect to filename in TFile, e.g.:
/mass or /cuts/two_leptons
* _rebin_ set rebinning for the histogram. Allowed values are: null or numbe
* _units_ x-axis units that are automatically added to the axis title
* _title_ x-axis title

2D plots supporte similar items but prefixed with **x** or **y** depending on
the axis. These include:

* _name_ is the plot name and follows the same convention as the 1D plot key
* _xrebin_ and _yrebin_ define how to rebin the plot in X- and Y-dimentions
* _xunits_ and _yunits_ specify the units of X- an Y- axis
* _xtitle_ and _ytitle_ follow the same convention as in the 1D case

**warning**: _all the template names should be unique_

The loader code will convert list of dictionaries into dictionary with keys
equal to plot names, e.g.:

```yamld
# consider yaml input
plot:
    - name: /abc
      rebin: 2
      units: GeV
      title: momentum
    _ name: /bac/tar
      rebin: null
      ujnits: null
      title: !!str "number of jets"
```

it will be converted to (in Python):

```python
{
    "plot": {
        "/abc": {
            "rebin": 2,
            "units": "GeV",
            "title": "momentum" 
        },
        "/bac/tar": {
            "rebin": None,
            "units": None,
            "title": "number of jets"
        }
    }
}
```

## Load

Use ```config.plot.load(filename)``` function to load YAML config,
e.g.:

```python
from config import plot

plot_cfg = plot.load("plot_config.yaml")
print("plot_cfg", plot_cfg)
```

The function will raise RuntimeError if input file does not exist, loading
data failed.

It will also convert list of inputs (channels) into dictionary with keys
equal to names (as described above).
