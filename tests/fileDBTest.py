'''
NOTE this testing library needs more tests for changing
wrapper attributes -- for now it's stable but future
changes could disrupt these.

@author Joe Maguire
@author Matt Seal
'''

# This import fixes sys.path issues
import bootstrap
from datawrap import filedbwrap
import unittest
import os
from os.path import dirname

class FakeObj():
    '''
    Used to track work on a non primitive with no methods
    defined.
    '''
    def __init__(self,value):
        self.value = int(value)
        
def firstAlphaChar(word):
    '''
    Gets the first alpha character in a string
    '''
    for c in word: 
        if c.isalpha():
            return c
    # Default to z if necessary
    return "z"

def getBaseAlphabet():
    '''The lower case alphabet'''
    return "abcdefghijklmnopqrstuvwxyz"

class DBWrapTest(object):
    '''
    Base class used to define DBWrap tests.
    
    @author Joe Maguire
    @author Matt Seal
    '''
    def setUp(self):
        self.datadir = os.path.join(dirname(__file__), 'fileDB')
        if not os.path.exists(self.datadir):
            os.makedirs(self.datadir)
        
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
        # Attempt to write to read only
        self.testDict.reopen(readOnly = True)
        self.assertRaises(AttributeError, self.testDict.__setitem__, '0', 7)
        self.testDict.syncWrites()

class MemFromFileTest(DBWrapTest, unittest.TestCase):
    '''
    Tests MemFromFileDict basic functionality.
    
    @author Joe Maguire
    @author Matt Seal
    '''
    def createDictionary(self):
        return filedbwrap.MemFromFileDict(os.path.join(self.datadir, '01'),
                                          readOnly=False,
                                          clear=True,
                                          stringifyKeys=True,
                                          databaseDefaultFunc=lambda: None)
    def clearCache(self):
        return False
     
class FileTest(DBWrapTest, unittest.TestCase):
    '''
    Tests FileDict basic functionality.
    
    @author Joe Maguire
    @author Matt Seal
    '''
    def createDictionary(self):
        return filedbwrap.FileDict(os.path.join(self.datadir, '02'),
                                   readOnly=False,
                                   clear=True,
                                   stringifyKeys=True,
                                   databaseDefaultFunc=lambda: None)
    def clearCache(self):
        return False   
    
class SplitFileTest(DBWrapTest, unittest.TestCase):
    '''
    Tests SplitFileDict basic functionality.
    
    @author Joe Maguire
    @author Matt Seal
    '''
    def createDictionary(self):
        return filedbwrap.SplitFileDict(os.path.join(self.datadir, '03'),
                                        splitKeys=tuple(getBaseAlphabet()),
                                        splitFunc = firstAlphaChar,
                                        readOnly=False,
                                        stringifyKeys=True,
                                        clear=True,
                                        databaseDefaultFunc=lambda: None)  
    def clearCache(self):
        return False 
    
class MemFromFileTestCacheZero(DBWrapTest, unittest.TestCase):
    '''
    Tests MemFromFileDict with 0 size cache.
    
    @author Joe Maguire
    @author Matt Seal
    '''
    def createDictionary(self):
        return filedbwrap.MemFromFileDict(os.path.join(self.datadir, '01'),
                                          readOnly=False,
                                          clear=True,
                                          stringifyKeys=True,
                                          cacheSize = 0,
                                          databaseDefaultFunc=lambda: None)
    def clearCache(self):
        return False
     
class FileTestCacheZero(DBWrapTest, unittest.TestCase):
    '''
    Tests FileDict with 0 size cache.
    
    @author Joe Maguire
    @author Matt Seal
    '''
    def createDictionary(self):
        return filedbwrap.FileDict(os.path.join(self.datadir, '02'),
                                   readOnly=False,
                                   clear=True,
                                   stringifyKeys=True,
                                   cacheSize = 0,
                                   databaseDefaultFunc=lambda: None)
    def clearCache(self):
        return False   
    
class SplitFileTestCacheZero(DBWrapTest, unittest.TestCase):
    '''
    Tests SplitFileDict with 0 size cache.
    
    @author Joe Maguire
    @author Matt Seal
    '''
    def createDictionary(self):
        return filedbwrap.SplitFileDict(os.path.join(self.datadir, '03'),
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
