## root.template

This is the plots loader. It recursively scans ROOT file and processed
each and every found plot or directory. All other objects are skipped.

The user class(es) should inherit this back-end to process histograms and
folders. These are skipped by default.

## How it works

The Loader class entry method is ```Loader::load("filename.root")```. It will
open file and scan over all keys found at the top level.

There are two outlets in the class that are called if TH1 or TDirectory like
object is found:

* process_plot
* process_dir

## Example

Consider the case when all plots need to be loaded up to one level deep

```python
from root import template

class PlotLoader(Loader):
    def __init__(self):
        self._plots = []
        self._depth = 0

    def process_dir(self, dir_):
        if 1 < self._depth:
            continue

        self._depth += 1
        self._load(dir_)
        self._depth -= 1

    def process_plot(self, hist):
        self._plots.append(hist.Clone())
```
