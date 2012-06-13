#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Feb 28, 2012
Copyright 2011, All rights reserved
'''

from __future__ import division, print_function

import time

class Timer(object):
    '''
    Function(method) decorator to count number of times function is called and
    calculate total elapsed time. Timer can be used as decorator with and
    without arguments, e.g.:

        @Timer
        def function1(...):
            ...

        @Timer(verbose = True)
        def function2(...):
            ...

    the same is applied to methods, e.g.:

        class Test(...):
            ...

            @Timer
            def function1(...):
                ...

            @Timer(verbose = True)
            def function2(...):
                ...

    Timer will print number of calls and elapsed time if configured to be
    verbose.
    
    The values of calls and time elapsed can be accessed for functions in
    a straight-forward way, e.g.:

        print(function1.calls)

    However, methods require a direct extraction of the Timer object from
    dictionary, e.g.:

        obj = Timer.__get__(Test.__dict__["function1"], None, None)
        print(obj.calls)

    '''

    def __init__(self, wrapped = None, label = '', verbose = False):
        '''
        Initialize timer with wrapped function or arguments if used
        '''

        self.__calls = 0
        self.__elapsed = 0
        self.__wrapped = wrapped
        self.__verbose = verbose
        self.__label = label

    def __get__(self, instance, owner):
        '''
        Called for instance/class attribute fetch and return wrapper with
        object instance passed as first argument
        '''

        # support interactive help
        if not instance:
            return self

        def wrapper(*parg, **karg):
            return self(instance, *parg, **karg)

        return wrapper

    def __call__(self, *parg, **karg):
        '''
        Call timer wrapper around wrapped function/method. A wrapped object is
        passed if Timer was used with arguments, e.g.:

            @Timer
            def function(...):
                ...

        in this case wrapped object is stored and Timer instance is returned.
        Otherwise wrapped object is called and elapsed time is measured
        '''

        # store wrapped object if Timer instance with arguments was constructed
        if not self.__wrapped:
            self.__wrapped = parg[0]

            return self
        else:
            # wrapped object exists and can be called
            self.__calls += 1

            start = time.clock()
            result = self.__wrapped(*parg, **karg)
            self.__elapsed += time.clock() - start

            if self.__verbose:
                print(self)

            return result

    @property
    def calls(self):
        '''
        Access number of calls made to function
        '''

        return self.__calls

    @property
    def elapsed(self):
        '''
        Get total elapsed time for all function calls
        '''

        return self.__elapsed

    def __str__(self):
        '''
        Verbose print
        '''

        return (("{label} " if self.__label else "{wrapped} ") +
                "calls: {calls:<3} "
                "elapsed: {elapsed:<6.4f} "
                "average: {average:<6.4f}").format(
                    label = self.__label,
                    wrapped = self.__wrapped,
                    calls = self.calls,
                    elapsed = self.elapsed,
                    average = self.elapsed / self.calls)



if "__main__" == __name__:
    @Timer
    def list_comprehension_silent_timer(size):
        return [x ** 2 for x in range(size)]

    @Timer(verbose = True)
    def list_comprehension_verbose_timer(size):
        return [x ** 2 for x in range(size)]

    @Timer(label = "[List Comprehension]", verbose = True)
    def list_comprehension_verbose_timer_with_label(size):
        return [x ** 2 for x in range(size)]

    class ListComprensionSilent(object):
        @Timer
        def __call__(self, size):
            return [x ** 2 for x in range(size)]

        def __str__(self):
            obj = Timer.__get__(ListComprensionSilent.__dict__["__call__"], None, None)
            return "<{Class} at 0x{ID:x}> {info}".format(
                        Class = self.__class__.__name__,
                        ID = id(self),
                        info = str(obj).rsplit('>')[1])

    class ListComprensionVerbose(object):
        @Timer(verbose = True)
        def __call__(self, size):
            return [x ** 2 for x in range(size)]

        def __str__(self):
            obj = Timer.__get__(ListComprensionSilent.__dict__["__call__"], None, None)
            return "<{Class} at 0x{ID:x}> {info}".format(
                        Class = self.__class__.__name__,
                        ID = id(self),
                        info = str(obj).rsplit('>')[1])

    class ListComprensionVerboseWithLabel(object):
        @Timer(verbose = True, label = "[ListComprensionVerboseWithLabel]")
        def __call__(self, size):
            return [x ** 2 for x in range(size)]

        def __str__(self):
            obj = Timer.__get__(ListComprensionSilent.__dict__["__call__"], None, None)
            return str(obj)



    for function in [list_comprehension_silent_timer,
                     list_comprehension_verbose_timer,
                     list_comprehension_verbose_timer_with_label,
                     ListComprensionSilent(),
                     ListComprensionVerbose(),
                     ListComprensionVerboseWithLabel()]:

        for size in 1, 10, 100, 1000, 10000, 100000:
            function(size)
            print(function)
            print("{0:^9}".format("-+-"))

        print("-" * 50)
