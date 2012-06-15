#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Feb 29, 2012
Copyright 2011, All rights reserved
'''

def split_use_and_ban(values):
    '''
    Put all the values starting with '-' into ban set and the rest into use
    '''

    ban = set()
    use = set()

    for value in values:
        if value.startswith('-'):
            ban.add(value[1:])
        else:
            use.add(value)

    return use, ban

if "__main__" == __name__:
    import unittest

    class TestIt(unittest.TestCase):
        '''Test function with different inputs'''

        def test_empty(self):
            '''Pass empty set on input'''

            use, ban = split_use_and_ban([])
            self.assertEqual(use, set())
            self.assertEqual(ban, set())

        def test_use_only(self):
            '''Pass set with nothing to ban'''

            input_ = list(chr(x) for x in range(ord('a'), ord('a') + 20))
            use, ban = split_use_and_ban(input_)
            self.assertEqual(use, set(input_))
            self.assertEqual(ban, set())

        def test_ban_only(self):
            '''Pass set with nothing to use'''

            input_ = ['-' + chr(x) for x in range(ord('a'), ord('a') + 20)]
            use, ban = split_use_and_ban(input_)
            self.assertEqual(use, set())
            self.assertEqual(ban, set(x[1:] for x in input_))

        def test_use_and_ban(self):
            '''Pass set with both: use and ban'''

            ban_input = ['-' + chr(x) for x in range(ord('a'), ord('a') + 5)]
            use_input = [chr(x) for x in range(ord('a') + 5, ord('a') + 10)]
            use, ban = split_use_and_ban(ban_input + use_input)
            self.assertEqual(use, set(use_input))
            self.assertEqual(ban, set(x[1:] for x in ban_input))

    unittest.main()
