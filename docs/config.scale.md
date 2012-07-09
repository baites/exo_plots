## [config.scale.py](https://github.com/ksamdev/exo_plots/blob/master/config/scale.py)

Load YAML configuration with channel user defined scales to be applied on to of
input normalization with cross-section, luminosity, and number of processed
events

## Configuration

The configuration file is minimalistic of dictionary type with keys being
the channel names and values are scales, e.g.:

```yaml
wlight: 500
wc: 120
ttbar: 0.023
```

## Load

Use ```config.scale.load(filename)``` function to load YAML config, e.g.:

```python
from config import scale

tau_scales = scale.load("tau.scales.yaml")
print("tau_scales", tau_scales)
```

**WARNING**: _loader does not check for channel validity_
