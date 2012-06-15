## template.input_config.py

Load YAML configuration that defines: input normalizations, channels and styles.

## Configuration

The configuration file should contain at least next items:

* **luminosity** that all inputs will be normalized to [in 1/pb units]
* **input** is a list of dictionary objects. Each item represents separate input
type with:
    * _name_ this defines input filename suffix
    * _events_ number of processed events in the input
    * _xsection_ to be used for the input normalization [in pb units]
    * _enable_ switch to turn OFF or ON input: input is **not** loaded if
      switched off
* **channel** is a list of channels that combine inputs, e.g.:
all **stop_X** and **satop_X** go into **stop** channel. Each channel must
host next information:
    * _name_ the channel ID
    * _inputs_ list of inputs that are allowed to be added into given channel
    * _legend_ string that is going to show up in the TLegend
    * _color_ color of the channel that will be applied to line, marker and fill
    * _fill_ True or False value, which indicates if plots will be filled
    * _line_ define line style

User may add more information to the config but all top-level keys are removed
from loaded configuration except:

* luminosity
* input
* channel

## Example

The most basic example is given below.

**Warning**: _all the numbers are miningless_

```yaml
luminosity: 10.20 # in 1/pico-barns [pb-1]
# Define inputs to be loaded (if enabled)
#
input:
    - name: ttbar
      events: 10200300 
      xsection: 54321
      enable: True
    - name: vv
      events: 10200
      xsection: 12345
      enable: False
    - name: stop_t
      events: 20100
      xsection: 135
      enable: True
    - name: satop_s
      events: 30200
      xsection: 246
      enable: True
# Define policy on how inputs can be grouped into channels
#
channel:
    - name: ttbar
      inputs: [ttbar]
      legend: !!str "QCD t#bar{t}"
      # color is specified by [base, shift] and will be converted on load to
      # color: base + shift, e.g.:
      #
      # yaml:   color: [10, 4]
      # load:   color: 14
      #
      color: [632, 1] # Red
      fill: True
      line: null
    - name: vv
      inputs: [vv]
      legend: !!str "VV"
      color: [416, 1] # Green
      fill: True
      line: null
    - name: stop
      inputs: [stop_t, satop_s]
      legend: !!str "Single-Top"
      color: [616, 1] # Magenta
      fill: True
      line: null
```
