## tfile.py

tfile is a ROOT.TFile _context manager_. The Python _with_ statement can be
used to open TFile in write or read mode.

## Example

```python
# read only
with tfile("input.root") as input_:
    plot = input_.Get("age")

# write
with tfile("output.root", "write") as output_:
    output_.WriteObject(plot)
```
