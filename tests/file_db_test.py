'''
NOTE this testing library needs more tests for changing
wrapper attributes -- for now it's stable but future
changes could disrupt these.
'''

# This import fixes sys.path issues
import parentpath

from datawrap import filedbwrap
import unittest
import os
import string
from os.path import dirname

class FakeObj():
    '''
    Used to track work on a non primitive with no methods
    defined.
    '''
    def __init__(self,value):
        self.value = int(value)

def first_alpha_char(word):
    '''
    Gets the first alpha character in a string
    '''
    for c in word:
        if c.isalpha():
            return c.lower()
    # Default to z if necessary
    return "z"

class DBWrapTest(object):
    '''
    Base class used to define DBWrap tests.
    '''
    def setUp(self):
        self.data_dir = os.path.join(dirname(__file__), 'file_db')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.test_dict = self.create_dictionary()

        self.size = 20
        #self.test_dict =  self.fileDict
        for i in range(self.size):
                self.test_dict[str(i)] = int(i)
        if self.clear_cache():
            self.test_dict.reopen(cache_size=0)

    def tearDown(self):
        self.test_dict.close()

    def test_default_func(self):
        self.assertEqual(self.test_dict['50'], None)

    def test_default_func_reopen(self):
        keyerror = False
        self.test_dict.reopen(database_default_func=None)
        try:
            self.test_dict['50']
        except KeyError:
            keyerror = True
        self.assertTrue(keyerror)

    def test_contains(self):
        # Do we contain all the values we entered?
        result = 0;
        for i in range(20):
            if str(i) in self.test_dict:
                result += 1
        self.assertEqual(result,self.size)
        self.test_dict._sync_writes()

    def test_check_values(self):
        # Check the values?
        result = 0
        for i in range(20):
            if self.test_dict[str(i)] == i:
                result += 1
        self.assertEqual(result,self.size)
        self.test_dict._sync_writes()

    def test_read_write(self):
        result = 0
        # Altering values
        # Double even values
        for i in range(20):
            if i%2 == 0:
                self.test_dict[str(i)] += self.test_dict[str(i)]
        for i in range(20):
            if i%2 == 0:
                if self.test_dict[str(i)] == 2*i:
                    result += 1
            else:
                if self.test_dict[str(i)] == i:
                    result += 1
        # Checking new values
        self.assertEqual(result,self.size)
        # Restoring values
        # Undo
        for i in range(20):
            if i%2 == 0:
                self.test_dict[str(i)] -= i
        self.test_check_values()
        self.test_dict._sync_writes()

    def test_delete(self):
        self.test_dict['100'] = 'kid0'
        self.assertEqual(self.test_dict['100'],'kid0')
        del self.test_dict['100']
        self.assertFalse('100' in self.test_dict)
        self.test_dict._sync_writes()

    def test_stringify(self):
        result = 0

        for i in range(20):
            if self.test_dict[i] == i:
                result += 1
        self.assertEqual(result,self.size)
        self.test_dict._sync_writes()

    def test_obj_named(self):
        # Key is not a string, value is a test FakeObject
        w = FakeObj(1)
        y = FakeObj(2)
        z = FakeObj(3)
        self.test_dict[w] = w
        self.test_dict[y] = y
        self.test_dict[z] = z
        self.assertTrue(self.test_dict[w].value == w.value)
        self.assertTrue(self.test_dict[y].value == y.value)
        self.assertTrue(self.test_dict[z].value == z.value)
        self.test_dict._sync_writes()

    def test_reopen(self):
        # Reopening read only
        self.test_dict.reopen(read_only=True);
        self.test_check_values()
        self.test_dict._sync_writes()

    def test_write_flush(self):
        # Flush then check values
        self.test_dict._sync_writes()
        result = 0
        for i in range(20):
            if self.test_dict[str(i)] == i:
                result += 1
        self.assertEqual(result,self.size)
        # Edit values, flush then check
        for i in range(20):
                self.test_dict[str(i)] *= 2
        self.test_dict._sync_writes()
        result = 0
        for i in range(20):
            if(self.test_dict[str(i)] ==  i*2):
                result += 1
        self.assertEqual(len(self.test_dict),result)
        self.test_dict._sync_writes()

    def test_write_to_read_only(self):
        # Attempt to write to read only
        self.test_dict.reopen(read_only=True)
        self.assertRaises(AttributeError, self.test_dict.__setitem__, '0', 7)
        self.test_dict._sync_writes()

class MemFromFileTest(DBWrapTest, unittest.TestCase):
    '''
    Tests MemFromFileDict basic functionality.
    '''
    def create_dictionary(self):
        return filedbwrap.MemFromFileDict(os.path.join(self.data_dir, '01'),
                                          read_only=False,
                                          clear=True,
                                          stringify_keys=True,
                                          database_default_func=lambda: None)
    def clear_cache(self):
        return False

class FileTest(DBWrapTest, unittest.TestCase):
    '''
    Tests FileDict basic functionality.
    '''
    def create_dictionary(self):
        return filedbwrap.FileDict(os.path.join(self.data_dir, '02'),
                                   read_only=False,
                                   clear=True,
                                   stringify_keys=True,
                                   database_default_func=lambda: None)
    def clear_cache(self):
        return False

class SplitFileTest(DBWrapTest, unittest.TestCase):
    '''
    Tests SplitFileDict basic functionality.
    '''
    def create_dictionary(self):
        return filedbwrap.SplitFileDict(os.path.join(self.data_dir, '03'),
                                        split_keys=tuple(string.ascii_lowercase),
                                        split_func = first_alpha_char,
                                        read_only=False,
                                        stringify_keys=True,
                                        clear=True,
                                        database_default_func=lambda: None)
    def clear_cache(self):
        return False

class MemFromFileTestCacheZero(DBWrapTest, unittest.TestCase):
    '''
    Tests MemFromFileDict with 0 size cache.
    '''
    def create_dictionary(self):
        return filedbwrap.MemFromFileDict(os.path.join(self.data_dir, '01'),
                                          read_only=False,
                                          clear=True,
                                          stringify_keys=True,
                                          cache_size = 0,
                                          database_default_func=lambda: None)
    def clear_cache(self):
        return False

class FileTestCacheZero(DBWrapTest, unittest.TestCase):
    '''
    Tests FileDict with 0 size cache.
    '''
    def create_dictionary(self):
        return filedbwrap.FileDict(os.path.join(self.data_dir, '02'),
                                   read_only=False,
                                   clear=True,
                                   stringify_keys=True,
                                   cache_size = 0,
                                   database_default_func=lambda: None)
    def clear_cache(self):
        return False

class SplitFileTestCacheZero(DBWrapTest, unittest.TestCase):
    '''
    Tests SplitFileDict with 0 size cache.
    '''
    def create_dictionary(self):
        return filedbwrap.SplitFileDict(os.path.join(self.data_dir, '03'),
                                  split_keys=tuple(string.ascii_lowercase),
                                  split_func = first_alpha_char,
                                  read_only=False,
                                  stringify_keys=True,
                                  clear=True,
                                  cache_size = 0,
                                  database_default_func=lambda: None)
    def clear_cache(self):
        return False


if __name__ == '__main__':
    unittest.main()
