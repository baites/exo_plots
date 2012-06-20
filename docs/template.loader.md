## [template.loader.py](https://github.com/ksamdev/exo_plots/blob/master/template/loader.py)

Load template histograms for specified channels, normalize each histogram, and
apply styles. All the loaded plots are stored in a dictionary with structure:

* key is being the plot path with name in the ROOT file with respect to the
file top level, e.g.: /mass_cut/jet_pt or /mass
* the value is the dictinary of channel <> histogram, e.g.: channel is the key
and histogram is the value

## InputLoader

The InputLoader is a base class that loads ROOT file with plots from all the
folders. This class should be overriden to extend the loading behavior.

**warning**: _only 1D plots are loaded. Extend Loader for 2D plots_

## ChannelLoader

Base loader for all the channels. It utilizes the InputLoader to load all
the inputs that go into the channel.
