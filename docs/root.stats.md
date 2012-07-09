## [stats.py](https://github.com/ksamdev/exo_plots/blob/master/root/stats.py)

Collection of tools useful in histogram(s) processing

## Efficiency

Calculate for given histogram efficiency as a function of X, e.g.:

    eff = Integral(hist, min, X) / Integral(hist, min, max)

or it can be integrated if *invert* flag is used:

    eff = Integral(hist, X, max) / Integral(hist, min, max)

```python
from root import stats
# efficiency calculation
efficiency = stats.efficiency(hist)
# inverted efficiency
inv_efficiency = stats.efficiency(hist, invert=True)
```

It is also possible to turn off the normalization to keep only numerator
integral, e.g.:

```python
form root import stats
integral = stats.efficiency(hist, normalize=False)
```

## Maximum

Two tools are available

* ```find_maximum(hist)``` return the maximum value in the histogram with error
added on top.<br />
**WARNING**: _the function will return approximate maximum which
is not always true, especially in bins with low stats and large errors; the
full histograms has to be manually scanned in these cases_

* ```maximum(hists, stacks)``` search for maximum value among passes histograms
and stacks of histograms. The function has same limitations as 
```find_maximum(hist)``` function (see warnings)
