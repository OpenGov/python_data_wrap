# This import triggers the __init__.py code regardless of how this file is called
import testing
import unittest
from datawrap import fileloader

# TODO implement
class DataLoadTest(unittest.TestCase):


    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()