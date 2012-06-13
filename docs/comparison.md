## comparison.py

This is the collection of different 1D histogram ratio calculators and
implementation of Canvas with two or more pads:

* **(top)** the main  pad where histograms should be drawn
* **(bottom)** the ratio of the plots should go here

The module also holds _compare_ decorator that should be used to wrap the
ratio calculators to make ratio plots in the same style

## Compare Decorator Example

Wrap ratio calculator with _compare_ decorator and use the wrapped object
as if it were the original function, e.g.:

```python
@compare
def custom_ratio(a, b):
    h = a.Clone()
    h.Divide()

    return h

hist_r = custom_ratio(hist_a, hist_b)
hist_r.Draw("9 hist")
```

## Ratio calculators

The most basic ratio calculators are available in the module. Consider two
histograms A and B. The calculators are as follows:

* **ratio** simple ratio of two plots A / B
* **data_mins_bg_over_bg** calculate difference between the two histograms
normalized to the second plot (A - B) / B
