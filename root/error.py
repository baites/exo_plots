#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Feb 24, 2012
Copyright 2011, All rights reserved
'''

from __future__ import division,print_function

import math

class StatError(property):
    '''
    Wrapper around histogram property that acts like property but allows to
    intercept get/set operations and alter histogram errors on fly, e.g.:

        ...

        @StatError(10)
        @property
        def hist(self, *parg, **karg):
            return SuperClass.hist.__get__(self, *parg, **karg)

        @hist.setter
        def hist(self, instance, value)
            SuperClass.hist.__set__(self, instance, value)

        ...

    In the above example each histogram error is modified by adding 10% of the
    bin content.

    By default, the StatError does not add the error to the histogram. It is
    user responsibility to call add_error method for this, e.g.:

        class CustomStatError(StatError):
            def __init__(self, percent):
                StatError.__init__(self, percent)

            def __set__(self, instance, value):
                StatError.__set__(self, instance, value)

                # Change the errors in the histogram
                self.add_error(instance.hist)

    The StatError class will automatically adjust the errors of each bin
    in the histogram whenever a new plot is assigned to hist property.

    More than one error contributions can be applied to the same histogram,
    e.g.:

        ...

        @StatError(4.5)
        @StatError(5)
        @StatError(10)
        @property
        def hist(self, *parg, **karg):
            return SuperClass.hist.__get__(self, *parg, **karg)

        @hist.setter
        def hist(self, instance, value)
            SuperClass.hist.__set__(self, instance, value)

        ...

    This way 4.5% + 5% + 10% error will be added.

    The class can also be used as a Stand-alone error propagator, e.g.:

        lumi_error = StatError(5)
        lumi_error.add_error(mc_background)
    '''

    def __init__(self, percent, fget=None, fset=None, fdel=None, doc=None):
        '''
        Initialize erorr descriptor
        '''

        self.__percent = percent / 100 if percent else None
        self.__wrapped = None   # property object to be wrapped

        self.__fget = fget
        self.__fset = fset
        self.__fdel = fdel

        # Copy documentation string from property getter function
        if self.__fget and not doc:
            self.__doc__ = self.__fget.__doc__
        else:
            self.__doc__ = doc

    def __call__(self, wrapped):
        '''
        Wrap property object, e.g.:

            class Klass(object):
                ...

                @StatError(10)
                @property
                def hist(self):
                    ...

                ...

        which is equivalent to:

            class Klass(object):
                ...

                def hist(self):
                    ...

                hist = @StatError(10)(property(Klass.hist))

                ...
        '''

        if isinstance(wrapped, property):
            self.__wrapped = wrapped
            self.__fget = None
            self.__fset = None
            self.__fdel = None

        else:
            self.__fget = wrapped

            if not self.__doc__:
                self.__doc__ = wrapped.__doc__

        return self

    # Property interface
    def __get__(self, instance, owner):
        '''
        Route property get operation to property
        '''

        if None == instance:
            return self
        elif self.__wrapped:
            return self.__wrapped.__get__(instance, owner)
        elif self.__fget:
            return self.__fget(instance)
        else:
            raise AttributeError("Attribute fetch is not allowed")

    def __set__(self, instance, value):
        '''
        Route property set operation to property
        '''

        if self.__wrapped:
            self.__wrapped.__set__(instance, value)
        elif self.__fset:
            self.__fset(instance, value)
        else:
            raise AttributeError("Attribute set is not allowed")

    def __delete__(self, instance):
        '''
        Route property delete operation to property
        '''

        if self.__wrapped:
            self.__wrapped.__delete__(instance)
        elif self.__fdel:
            self.__fdel(instance)
        else:
            raise AttributeError("Attribute delete is not allowed")

    def getter(self, obj):
        '''
        Set property getter function
        '''

        if self.__wrapped:
            self.__wrapped = self.__wrapped.getter(obj)
        else:
            self.__fget = obj

        return self

    def setter(self, obj):
        '''
        Set property setter function
        '''

        if self.__wrapped:
            self.__wrapped = self.__wrapped.setter(obj)
        else:
            self.__fset = obj

        return self

    def deleter(self, obj):
        '''
        Set property remove function
        '''

        if self.__wrapped:
            self.__wrapped = self.__wrapped.deleter(obj)
        else:
            self.__fdel = obj

        return self

    def add_error(self, hist):
        '''
        Add error (custom percent of the bin content). Child classes should
        explicitly call method to adjust histogram errors
        '''

        if not self.__percent:
            return

        # Add in quadrature the % * bin_content to the bin error
        for bin in range(1, hist.GetNbinsX() + 1):
            hist.SetBinError(bin,
                             math.sqrt(hist.GetBinError(bin) ** 2 +
                                        (hist.GetBinContent(bin) *
                                            self.__percent) ** 2))

    def set_percent(self, percent):
        '''
        Let user to change the percent value after the object is created
        '''

        if percent:
            percent /= 100
            print("percent is changed to:", percent)
            self.__percent = percent
        else:
            print("percent is NOT used")
            self.__percent = None



if "__main__" == __name__:
    import unittest
    import ROOT

    class CustomStatError(StatError):
        '''
        Example of how to extend StatError and adjust histogram errors when
        new plot is assigned
        '''

        def __init__(self, percent):
            StatError.__init__(self, percent)

        def __set__(self, instance, value):
            StatError.__set__(self, instance, value)

            # Adjust errors
            self.add_error(instance.hist)

    class HistNoErrorChange(object):
        '''
        Example of the histogram continaer whith StatErorr. By default, the
        Base error class does not change the plot errors
        '''

        # Custom gaussian, which is used to randomly fill histograms
        __gaus = ROOT.TF1("custom_gaus", "gaus(0)", 0, 10)
        __gaus.SetParameters(1, 5, 1) # random normalization, mean at 5, sigma 1

        def __init__(self):
            '''
            Create random histogram and store in instance
            '''

            h = ROOT.TH1F()
            h.SetBins(10, 0, 10);
            h.FillRandom("custom_gaus", 100)

            # for simplicity make each error to be equal to One
            for bin in range(1, h.GetNbinsX() + 1):
                h.SetBinError(bin, 1)

            self.hist = h

        @StatError(10)
        @property
        def hist(self):
            return self.__hist

        @hist.setter
        def hist(self, obj):
            self.__hist = obj

    class HistWithErrorChange(HistNoErrorChange):
        '''
        Example of how to add Errors to histogram:

            - Override property
            - pass property methods to super class
        '''

        def __init__(self):
            HistNoErrorChange.__init__(self)

        @CustomStatError(10)
        @property
        def hist(self, *parg, **karg):
            '''
            Route property access to super class
            '''

            return HistNoErrorChange.hist.__get__(self, *parg, **karg)

        @hist.setter
        def hist(self, *parg, **karg):
            '''
            Forward property set to super class
            '''

            HistNoErrorChange.hist.__set__(self, *parg, **karg)

    class HistWithManyErrorChange(HistNoErrorChange):
        '''
        Example of how to apply many errors to the same histogram. As in
        the example with one source of the errors, the idea is:

            - Override property
            - Pass all accessors to super class

        '''

        def __init__(self):
            HistNoErrorChange.__init__(self)

        @CustomStatError(4.5)
        @CustomStatError(4)
        @CustomStatError(10)
        @property
        def hist(self, *parg, **karg):
            return HistNoErrorChange.hist.__get__(self, *parg, **karg)

        @hist.setter
        def hist(self, *parg, **karg):
            HistNoErrorChange.hist.__set__(self, *parg, **karg)

    class ErrorStatAsPropertyReadOnly(HistNoErrorChange):
        '''
        The read-only property does not make sence in this example because
        histogram is assigned in constructor to read-only hist
        '''

        def __init__(self):
            HistNoErrorChange.__init__(self)

        @StatError(5)
        def hist(self):
            '''
            StatError is property
            '''

            return self.__hist

    class ErrorStatAsProperty(HistNoErrorChange):
        def __init__(self):
            HistNoErrorChange.__init__(self)

        @StatError(5)
        def hist(self):
            '''
            StatError is property
            '''

            return self.__hist

        @hist.setter
        def hist(self, obj):
            self.__hist = obj

    class DoubleErrorStatAsProperty(ErrorStatAsProperty):
        def __init__(self):
            ErrorStatAsProperty.__init__(self)

        @StatError(5)
        @StatError(10)
        def hist(self):
            return ErrorStatAsProperty.hist.__get__(instance, instance.__class__)

        @hist.setter
        def hist(self, obj):
            ErrorStatAsProperty.hist.__set__(instance, obj)



    # Unit tests
    class TestHistNoErrorChange(unittest.TestCase):
        def setUp(self):
            self.__hist = HistNoErrorChange()

        def test_error(self):
            h = self.__hist.hist
            for bin in range(1, h.GetNbinsX() + 1):
                self.assertEqual(h.GetBinError(bin), 1)

    class TestHistWithErrorChange(unittest.TestCase):
        def setUp(self):
            self.__hist = HistWithErrorChange()

        def test_error(self):
            h = self.__hist.hist
            for bin in range(1, h.GetNbinsX() + 1):
                self.assertEqual("{0:.4f}".format(h.GetBinError(bin)),
                                 "{0:.4f}".format(
                                     math.sqrt(1 + (.1 * h.GetBinContent(bin)) ** 2)))

    class TestHistWithManyErrorChange(unittest.TestCase):
        def setUp(self):
            self.__hist = HistWithManyErrorChange()

        def test_error(self):
            h = self.__hist.hist
            for bin in range(1, h.GetNbinsX() + 1):
                self.assertEqual("{0:.4f}".format(h.GetBinError(bin)),
                                 "{0:.4f}".format(
                                     math.sqrt(
                                         1 + h.GetBinContent(bin) ** 2 *
                                            (0.04 ** 2 +
                                             0.045 ** 2 +
                                             0.1 ** 2))))

    class TestErrorStatAsPropertyReadOnly(unittest.TestCase):
        def test_get(self):
            self.assertRaises(AttributeError, lambda: ErrorStatAsPropertyReadOnly())

    class TestErrorStatAsProperty(unittest.TestCase):
        def setUp(self):
            self.__hist = ErrorStatAsProperty()

        def test_doc(self):
            # documentation will be accessable only to PyDoc
            self.assertEqual(self.__hist.hist.__doc__, None)

        def test_del(self):
            self.assertRaises(AttributeError, lambda obj: obj.hist.__del__(), self)

    unittest.main()
