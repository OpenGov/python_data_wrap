# This import triggers the __init__.py code regardless of how this file is called
import tests
import unittest
import os
from os.path import dirname
from datawrap import fileloader

# TODO implement
class DataLoadTest(unittest.TestCase):
    def setUp(self):
        self.datadir = os.path.join(dirname(__file__), 'fileLoadData')

    def testNotImplemented(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()