# This import fixes sys.path issues
import bootstrap
import unittest
import os
from os.path import dirname
from datawrap import fileloader

# TODO implement
class DataLoadTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(dirname(__file__), 'file_load_data')

    def test_not_implemented(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()