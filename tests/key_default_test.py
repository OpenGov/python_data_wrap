# This import fixes sys.path issues
from . import parentpath

import unittest
from past.builtins import basestring
from datawrap.keydefaultdict import KeyDefaultDict

class KeyDefaultDictTest(unittest.TestCase):
    '''
    Performs basic KeyDefaultDict tests where the default function
    takes the key as an argument to generate new values.
    '''
    def test_key_defaults(self):
        inputs = { k : k*2 for k in range(100)}
        for k in list(inputs.keys()):
            inputs[str(k)] = str(k*2)

        repeatkey = KeyDefaultDict(lambda k: k)
        for k in inputs:
            self.assertEqual(repeatkey[k], k)

        # Reset
        repeatkey = KeyDefaultDict(lambda k: k)
        for k, v in inputs.items():
            repeatkey[k] = v

        for k in inputs:
            if isinstance(k, basestring):
                self.assertEqual(repeatkey[k], str(int(k)*2))
            else:
                self.assertEqual(repeatkey[k], k*2)

        for k in list(range(-200, 0)) + list(range(1000, 2000)):
            self.assertEqual(repeatkey[k], k)

if __name__ == "__main__":
    unittest.main()
