## error.py

Modify the error in the histogram. One of the examples is to add error due
to luminosity or trigger to all the Monte-Carlo plots.

## Stand-alone Example

Use class as a stand-alone error propagator

```python
lumi_error = StatError(4.5)
# Add the error to some histogram
lumi_error.add_error(background_plot)
```

## Property Example

Consider a class that has a dedicated property to access the histogram, e.g.:

```python
class HistogramContainer(object):
    @property
    def hist(self):
        return self._hist
```

Now, user would like to be sure that certain error is automatically added to
all of these histograms.

Add class that calls the error propagator explicitly and chane the histogram
wrapper, e.g.:

```python
class CustomStatError(StatError):
    def __init__(self, percent):
        StatError.__init__(self, percent)

    def __set__(self, instance, value):
        StatError.__set__(self, instance, value)

        # Propagate the errors
        self.add_error(instance.hist)

class HistogramContainer(object):
    # Add errors here
    @CustomStatError(5)
    @property
    def hist(self):
        return self._hist
```

**Note**: _The above example adds errors to the same histogram every time it is
accessed. This can be easily fixed by adding a flag to the CustomStatError
class_
