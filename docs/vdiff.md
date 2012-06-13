## vdiff.py

Compare two ROOT files (top level only), compare common histograms and plot
the ones that are different. The
[TH1::Integral](http://root.cern.ch/root/html/TH1.html#TH1:Integral)
is used to check if histograms are the same.

## Example

```python
# default use
different = vdiff("file1.root", "file2.root")
if different:
    print("files are different and comparison plots are saved")
```

the function may also be run in verbose mode and report if files are different

```python
# verbose mode
vdiff("file1.root", "file2.root", verbose=True)
```
