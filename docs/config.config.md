## config.config.py

Application global configuration loader. The configuration file is loaded from
in ~/.exo/config.yaml if exists.

## Configuration

The most full configuration file consists of next options:

```yaml
# Core application settings
core:
    # Run in batch mode
    batch: False
    # Print extra debugging information
    verbose: True
# template related configuration
template:
    # channels configuration file
    channel: null
    # plots configuration file
    plot: null
```
