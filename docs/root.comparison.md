## [root.comparison.py](https://github.com/ksamdev/exo_plots/blob/master/root/comparison.py)

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

## Canvas

This is constructor of the Canvas which is automatically divided into N pads
with first pad being the main one and the rest are small pads used for ratio
histograms.

All plots should be drawn in the main pad. THStack is used for this.

The Canvas can be used as base class for user canvases that calculate ratio
plots on fly, e.g.:

```python
class ComparePlots(Canvas):                                                                  
    @compare                                                                                 
    def ratio(self, first, second):                                                          
        '''calculate ratio of two plots'''

        ratio = first.Clone()                                                                
        ratio.SetDirectory(0)                                                                
        ratio.Reset()                                                                        
        ratio.Divide(first, second)                                                          

        return ratio                                                                         

    def __call__(self, first, second):                                                       
        '''Plot histograms including the ratio in the bottom pad'''

        # Draw histograms in the main pad
        canvas = self.canvas                                                                 
        canvas.cd(1)

        # Stack plots for axis auto scale
        stack = ROOT.THStack()                                                               
        stack.Add(first)                                                                     
        stack.Add(second)                                                                    
        stack.Draw("nostack hist 9")                                                         

        # Draw ratio in the bottom pad
        canvas.cd(2)                                                                         
        self.ratio(first, second).Draw("e 9")

        canvas.Update()                                                                      
```
