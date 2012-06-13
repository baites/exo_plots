## timer.py

Timer class is a function or method decorator to measure the performance of the
wrapped object. It tracks number of calls made to the object and how much time
it took to execute it.

Such decorator has ```__str__``` method implemented for pretty print with all
of the above information displayed. The total elapsed time is shown as well as
average run time.

## Basic usage

In the example below the number of calls to function are trackedn and elapsed
time is measured:

```python
@Timer
def calculator(day):
    return weather(day)

calculator(today)
calculator(tomorrow)

print(calculator)
calls = calculator.calls
elapsed = calculator.elapsed
```

The Timer decorator can also be used with methods:

```python
class Weather(object):
    @Timer
    def forecast(self, day):
        return get_forcast(day)

source = Weather()
source.forecast(today)
source.forecast(tomorrow)

print(source.forecast)
calls = source.forecast.calls
elapsed = source.forecast.elapsed
```

## Advanced usage

The Timer can be made to be verbose and print itself every time the call to the
wrapped object is made:

```python
@Timer(verbose=True)
def calculator(day):
    pass
```

The print function may also use custom label to prefix all prints

```python
@Timer(label='[test]')
def calculator(day):
    pass
```
