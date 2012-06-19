## [tmplate.options](https://github.com/ksamdev/exo_plots/blob/master/template/options.py)

The module defines default options that should be present in all plotting
tools. These include:

* **-v, --verbose** run application in verbose mode with debug info printed
out
* **-b, --batch** do not enter interactive mode and do the plotting in batch
* **--config** use different application configuration file than
default, e.g.: ~/.exo/template.yaml
* **--channel-config** use cutom channel/input definition configuration file
* **--plot-config** load user-defined plots configuration
* **--channels** channels to be loaded

The last options accepts abbreviations as described in the
[Channel Config](https://github.com/ksamdev/exo_plots/blob/master/docs/config.channel.md#expand-channels). 

## Example

Consider a tool which compares the same distribution amond different channels.
User creates a new module for the task and defines new options parser that is
based on the default one:

```python
from template import options

def parser():
    parser_ = options.parser()

    parser_.add_option(
        "--legend-header",
        action="store", default=None,
        "User defined legend header on plots")

    return parser_
```
