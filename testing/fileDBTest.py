# This import triggers the __init__.py code regardless of how this file is called
import testing
from datawrap import filedbwrap
import unittest
import os

'''
NOTE this testing library needs more tests for changing
wrapper attributes -- for now it's stable but future
changes could disrupt these.

@author Joe Maguire
@author Matt Seal
'''

'''
Used to track work on a non primitive with no methods
defined.
'''
class FakeObj():
    def __init__(self,value):
        self.value = int(value)
        
'''
Gets the first alpha character in a string
'''
def firstAlphaChar(word):
    for c in word: 
        if c.isalpha():
            return c
    # Default to z if necessary
    return "z"

'''
The lower case alphabet
'''
def getBaseAlphabet():
    return "abcdefghijklmnopqrstuvwxyz"

'''
Base class used to define DBWrap tests.

@author Joe Maguire
@author Matt Seal
'''
class DBWrapTest(object):
    def setUp(self):
        self.dirname = 'fileDB'
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)
        
        self.testDict = self.createDictionary()

        self.size = 20
        #self.testDict =  self.fileDict
        for i in range(self.size):
                self.testDict[str(i)] = int(i)
        if(self.clearCache()):
            self.testDict.reopen(cacheSize = 0)
    def tearDown(self):
        self.testDict.close()
      
    def testDefaultFunc(self):
        self.assertEqual(self.testDict['50'], None)
       
    def testDefaultFuncReopen(self):       
        keyerror = False
        self.testDict.reopen(databaseDefaultFunc=None)
        try:
            self.testDict['50']
        except KeyError:
            keyerror = True
        self.assertTrue(keyerror)
    
    def testContains(self):
        # Do we contain all the values we entered?    
        result = 0;
        for i in range(20):
            if str(i) in self.testDict:
                result += 1
        self.assertEqual(result,self.size)
        self.testDict.syncWrites()
    
    def testCheckValues(self):
        # Check the values?
        result = 0
        for i in range(20):
            if self.testDict[str(i)] == i:
                result += 1
        self.assertEqual(result,self.size)
        self.testDict.syncWrites()
    
    def testReadWrite(self):
        result = 0
        # Altering values
        # Double even values
        for i in range(20):
            if i%2 == 0:
                self.testDict[str(i)] += self.testDict[str(i)]
        for i in range(20):
            if i%2 == 0:
                if self.testDict[str(i)] == 2*i:
                    result += 1
            else:
                if self.testDict[str(i)] == i:
                    result += 1
        # Checking new values
        self.assertEqual(result,self.size)
        # Restoring values
        # Undo
        for i in range(20):
            if i%2 == 0:
                self.testDict[str(i)] -= i
        self.testCheckValues()
        self.testDict.syncWrites()

    def testDelete(self):
        self.testDict['100'] = 'kid0'
        self.assertEqual(self.testDict['100'],'kid0')
        del self.testDict['100']
        self.assertFalse('100' in self.testDict)
        self.testDict.syncWrites()
  
    def testStringify(self):
        result = 0
       
        for i in range(20):
            if self.testDict[i] == i:
                result += 1
        self.assertEqual(result,self.size)
        self.testDict.syncWrites()
    
    def testObjNamed(self): 
        # Key is not a string, value is a test FakeObject
        w = FakeObj(1)
        y = FakeObj(2)
        z = FakeObj(3)
        self.testDict[w] = w
        self.testDict[y] = y
        self.testDict[z] = z
        self.assertTrue(self.testDict[w].value == w.value)
        self.assertTrue(self.testDict[y].value == y.value)
        self.assertTrue(self.testDict[z].value == z.value)
        self.testDict.syncWrites()
            
    def testReopen(self):
            # Reopening read only
            self.testDict.reopen(readOnly = True);
            self.testCheckValues()
            self.testDict.syncWrites()

    def testWriteFlush(self):
            # Flush then check values
            self.testDict.syncWrites()
            result = 0
            for i in range(20):
                if self.testDict[str(i)] == i:
                    result += 1
            self.assertEqual(result,self.size)
            # Edit values, flush then check
            for i in range(20):
                    self.testDict[str(i)] *= 2
            self.testDict.syncWrites()
            result = 0
            for i in range(20):
                if(self.testDict[str(i)] ==  i*2):
                    result += 1
            self.assertEqual(len(self.testDict),result)    
            self.testDict.syncWrites()
    
    def testWriteToReadOnly(self):
        prevent_write = False
        # Attempt to write to read only
        self.testDict.reopen(readOnly = True)
        self.assertRaises(AttributeError, self.testDict.__setitem__, '0', 7)
        self.testDict.syncWrites()

'''
Tests MemFromFileDict basic functionality.

@author Joe Maguire
@author Matt Seal
'''
class MemFromFileTest(DBWrapTest, unittest.TestCase):
    def createDictionary(self):
        return filedbwrap.MemFromFileDict(os.path.join(self.dirname, '01'),
                                          readOnly=False,
                                          clear=True,
                                          stringifyKeys=True,
                                          databaseDefaultFunc=lambda: None)
    def clearCache(self):
        return False
     
'''
Tests FileDict basic functionality.

@author Joe Maguire
@author Matt Seal
'''
class FileTest(DBWrapTest, unittest.TestCase):
    def createDictionary(self):
        return filedbwrap.FileDict(os.path.join(self.dirname, '02'),
                                   readOnly=False,
                                   clear=True,
                                   stringifyKeys=True,
                                   databaseDefaultFunc=lambda: None)
    def clearCache(self):
        return False   
    
'''
Tests SplitFileDict basic functionality.

@author Joe Maguire
@author Matt Seal
'''
class SplitFileTest(DBWrapTest, unittest.TestCase):
    def createDictionary(self):
        return filedbwrap.SplitFileDict(os.path.join(self.dirname, '03'),
                                        splitKeys=tuple(getBaseAlphabet()),
                                        splitFunc = firstAlphaChar,
                                        readOnly=False,
                                        stringifyKeys=True,
                                        clear=True,
                                        databaseDefaultFunc=lambda: None)  
    def clearCache(self):
        return False 
    
'''
Tests MemFromFileDict with 0 size cache.

@author Joe Maguire
@author Matt Seal
'''
class MemFromFileTestCacheZero(DBWrapTest, unittest.TestCase):
    def createDictionary(self):
        return filedbwrap.MemFromFileDict(os.path.join(self.dirname, '01'),
                                          readOnly=False,
                                          clear=True,
                                          stringifyKeys=True,
                                          cacheSize = 0,
                                          databaseDefaultFunc=lambda: None)
    def clearCache(self):
        return False
     
'''
Tests FileDict with 0 size cache.

@author Joe Maguire
@author Matt Seal
'''
class FileTestCacheZero(DBWrapTest, unittest.TestCase):
    def createDictionary(self):
        return filedbwrap.FileDict(os.path.join(self.dirname, '02'),
                                   readOnly=False,
                                   clear=True,
                                   stringifyKeys=True,
                                   cacheSize = 0,
                                   databaseDefaultFunc=lambda: None)
    def clearCache(self):
        return False   
    
'''
Tests SplitFileDict with 0 size cache.

@author Joe Maguire
@author Matt Seal
'''
class SplitFileTestCacheZero(DBWrapTest, unittest.TestCase):
    def createDictionary(self):
        return filedbwrap.SplitFileDict(os.path.join(self.dirname, '03'),
                                  splitKeys=tuple(getBaseAlphabet()),
                                  splitFunc = firstAlphaChar,
                                  readOnly=False,
                                  stringifyKeys=True,
                                  clear=True,
                                  cacheSize = 0,
                                  databaseDefaultFunc=lambda: None)  
    def clearCache(self):
        return False 
        
    
if __name__ == '__main__': 
    unittest.main()
