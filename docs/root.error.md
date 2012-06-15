## error.py

Modify the error in the histogram. One of the examples is to add error due
to luminosity or trigger to all the Monte-Carlo plots.

## Example

```python
from root import error
error.add(h1, 4.5) # add 4.5% to the first histogram
# the errors can be chained
error.add(h2, 4) # add 4% to the h2
error.add(h2, 5) # add 5% on top to the h2
```
