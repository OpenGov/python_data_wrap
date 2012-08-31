# Import this to be able to load parent directory modules
from initSubdir import checkSubdirPath; checkSubdirPath(__name__)
import listwrap
import unittest

class ListWrapTest(unittest.TestCase):
    def testNonStrLen(self):
        testItem = []
        self.assertEqual(listwrap.nonStrLen(testItem), 0)
        testItem.append(1)
        self.assertEqual(listwrap.nonStrLen(testItem), 1)
        self.assertRaises(TypeError, listwrap.nonStrLen, 1)
        self.assertRaises(TypeError, listwrap.nonStrLen, "")
        self.assertRaises(TypeError, listwrap.nonStrLen, "a longer string")
        self.assertRaises(TypeError, listwrap.nonStrLen, None)

    def testNonStrLenNoThrow(self):
        testItem = []
        self.assertEqual(listwrap.nonStrLenNoThrow(testItem), 0)
        testItem.append(1)
        self.assertEqual(listwrap.nonStrLenNoThrow(testItem), 1)
        
        self.assertEqual(listwrap.nonStrLenNoThrow(1), 0)
        self.assertEqual(listwrap.nonStrLenNoThrow(""), 0)
        self.assertEqual(listwrap.nonStrLenNoThrow("a longer string"), 0)
        self.assertEqual(listwrap.nonStrLenNoThrow(None), 0)
        
    def testGetNonNegativeIndex(self):
        self.assertEqual(listwrap.getNonNegativeIndex(0, 2), 0)
        self.assertEqual(listwrap.getNonNegativeIndex(1, 2), 1)
        self.assertEqual(listwrap.getNonNegativeIndex(2, 2), 2)
        self.assertEqual(listwrap.getNonNegativeIndex(3, 2), 3)
        self.assertEqual(listwrap.getNonNegativeIndex(-1, 2), 1)
        self.assertEqual(listwrap.getNonNegativeIndex(-2, 2), 0)
        self.assertEqual(listwrap.getNonNegativeIndex(-3, 2), 1)
        self.assertEqual(listwrap.getNonNegativeIndex(-13, 4), 3)
        
        # Ensure 0's don't blow up the calls
        self.assertEqual(listwrap.getNonNegativeIndex(0, 0), 0)
        self.assertEqual(listwrap.getNonNegativeIndex(10, 0), 10)
        self.assertEqual(listwrap.getNonNegativeIndex(-1, 0), 0)
        
    def testGetRestrictedIndex(self):
        self.assertEqual(listwrap.getRestrictedIndex(0, 2), 0)
        self.assertEqual(listwrap.getRestrictedIndex(1, 2), 1)
        self.assertEqual(listwrap.getRestrictedIndex(2, 2), 2)
        self.assertEqual(listwrap.getRestrictedIndex(3, 2), 2)
        self.assertEqual(listwrap.getRestrictedIndex(-1, 2), 1)
        self.assertEqual(listwrap.getRestrictedIndex(-2, 2), 0)
        self.assertEqual(listwrap.getRestrictedIndex(-3, 2), 1)
        self.assertEqual(listwrap.getRestrictedIndex(-13, 4), 3)
        
        # Ensure 0's don't blow up the calls
        self.assertEqual(listwrap.getRestrictedIndex(0, 0), 0)
        self.assertEqual(listwrap.getRestrictedIndex(10, 0), 0)
        self.assertEqual(listwrap.getRestrictedIndex(-1, 0), 0)
        
        # Check with lengthIndexAllowed False
        self.assertEqual(listwrap.getRestrictedIndex(0, 2, False), 0)
        self.assertEqual(listwrap.getRestrictedIndex(1, 2, False), 1)
        self.assertEqual(listwrap.getRestrictedIndex(2, 2, False), 1)
        self.assertEqual(listwrap.getRestrictedIndex(3, 2, False), 1)
        self.assertEqual(listwrap.getRestrictedIndex(0, 0, False), 0)
        self.assertEqual(listwrap.getRestrictedIndex(10, 0, False), 0)
        self.assertEqual(listwrap.getRestrictedIndex(-1, 0, False), 0)
        
        
    def testGetPosSlice(self):
        dataLen = 10
        # Check slices
        self.assertEqual(listwrap.getTrueSlice(slice(None,None,None), dataLen), slice(None,None,None))
        self.assertEqual(listwrap.getTrueSlice(slice(1,None,None), dataLen), slice(1,None,None))
        self.assertEqual(listwrap.getTrueSlice(slice(None,2,None), dataLen), slice(None,2,None))
        self.assertEqual(listwrap.getTrueSlice(slice(None,None,3), dataLen), slice(None,None,3))
        self.assertEqual(listwrap.getTrueSlice(slice(1,2,None), dataLen), slice(1,2,None))
        self.assertEqual(listwrap.getTrueSlice(slice(1,None,3), dataLen), slice(1,None,3))
        self.assertEqual(listwrap.getTrueSlice(slice(None,2,3), dataLen), slice(None,2,3))
        self.assertEqual(listwrap.getTrueSlice(slice(1,2,3), dataLen), slice(1,2,3))
        
        # Check tuples of length 3
        self.assertEqual(listwrap.getTrueSlice((None,None,None), dataLen), slice(None,None,None))
        self.assertEqual(listwrap.getTrueSlice((1,None,None), dataLen), slice(1,None,None))
        self.assertEqual(listwrap.getTrueSlice((None,2,None), dataLen), slice(None,2,None))
        self.assertEqual(listwrap.getTrueSlice((None,None,3), dataLen), slice(None,None,3))
        self.assertEqual(listwrap.getTrueSlice((1,2,None), dataLen), slice(1,2,None))
        self.assertEqual(listwrap.getTrueSlice((1,None,3), dataLen), slice(1,None,3))
        self.assertEqual(listwrap.getTrueSlice((None,2,3), dataLen), slice(None,2,3))
        self.assertEqual(listwrap.getTrueSlice((1,2,3), dataLen), slice(1,2,3))
        
        # Check all other valid inputs
        self.assertEqual(listwrap.getTrueSlice((1,None), dataLen), slice(1,None,None))
        self.assertEqual(listwrap.getTrueSlice((None,None), dataLen), slice(None,None,None))
        self.assertEqual(listwrap.getTrueSlice((None,2), dataLen), slice(None,2,None))
        self.assertEqual(listwrap.getTrueSlice((1,None), dataLen), slice(1,None,None))
        self.assertEqual(listwrap.getTrueSlice((1,2), dataLen), slice(1,2,None))
        self.assertEqual(listwrap.getTrueSlice((1,), dataLen), slice(1,2,None))
        self.assertEqual(listwrap.getTrueSlice(1, dataLen), slice(1,2,None))
        
        # Check values outside range
        self.assertEqual(listwrap.getTrueSlice(slice(1,dataLen+2), dataLen), slice(1,dataLen,None))
        self.assertEqual(listwrap.getTrueSlice(slice(-1,dataLen+2), dataLen), slice(dataLen-1,dataLen,None))
        self.assertEqual(listwrap.getTrueSlice(slice(-1*dataLen,dataLen+2), dataLen), slice(0,dataLen,None))
        self.assertEqual(listwrap.getTrueSlice(slice(-10*dataLen,0,0), dataLen), slice(0,0,0))
    
    def testListIter(self):
        test = []
        iter = listwrap.ListIter(test)
        self.assertRaises(StopIteration, iter.next)
        # Check that it iterates in the correct order
        test = [1,2,3,4,5,6]
        count = 0
        iter = listwrap.ListIter(test)
        for i,val in enumerate(iter):
            self.assertEqual(i+1, val)
            count += 1
        # Ensure we saw all items in test
        self.assertEqual(len(test), count)
        # Check __iter__
        iter = iter.__iter__()
        for i,val in enumerate(iter):
            self.assertEqual(i+1, val)
            
    def testDimensionRange(self):
        dimrange = listwrap.DimensionRange()
        self.assertEqual(len(dimrange), 0)
        
        # Check if the tuple gets converted to a slice
        dimrange.addRange((1,2))
        self.assertEqual(len(dimrange), 1)
        self.assertEqual(type(dimrange[0]), slice)
        self.assertEqual(dimrange[0], slice(1,2,None))
        
        # Check ordering of slice
        dimrange.addRange((1,2,3))
        self.assertEqual(len(dimrange), 2)
        self.assertEqual(type(dimrange[1]), slice)
        self.assertEqual(dimrange[1], slice(1,2,3))
        
        # Check pushing a slice
        dimrange.addRange(slice(1,2,3))
        self.assertEqual(len(dimrange), 3)
        self.assertEqual(type(dimrange[2]), slice)
        self.assertEqual(dimrange[2], slice(1,2,3))
        
        # Make sure the constructor works as well
        dimrange = listwrap.DimensionRange((1,2,3), (4,5), slice(6))
        self.assertEqual(len(dimrange), 3)
        self.assertEqual(type(dimrange[0]), slice)
        self.assertEqual(dimrange[0], slice(1,2,3))
        self.assertEqual(type(dimrange[1]), slice)
        self.assertEqual(dimrange[1], slice(4,5,None))
        self.assertEqual(type(dimrange[2]), slice)
        self.assertEqual(dimrange[2], slice(None,6,None))
        
        # Try copying the Range
        dimrange = listwrap.DimensionRange(dimrange)
        self.assertEqual(len(dimrange), 3)
        self.assertEqual(type(dimrange[0]), slice)
        self.assertEqual(dimrange[0], slice(1,2,3))
        self.assertEqual(type(dimrange[1]), slice)
        self.assertEqual(dimrange[1], slice(4,5,None))
        self.assertEqual(type(dimrange[2]), slice)
        self.assertEqual(dimrange[2], slice(None,6,None))
        
    def testSliceOnLength(self):
        dimrange = listwrap.DimensionRange((0,4), (1,6), slice(7))
        self.assertEqual(dimrange.sliceOnLength(10), slice(1,4))
        self.assertEqual(dimrange.sliceOnLength(4), slice(1,4))
        self.assertEqual(dimrange.sliceOnLength(3), slice(1,3))
        self.assertEqual(dimrange.sliceOnLength(1), slice(1,1))
        
        dimrange = listwrap.DimensionRange((1,10), slice(6))
        # yes, this should be slice(1,7) as slice(6) is applied After (1,10)
        self.assertEqual(dimrange.sliceOnLength(10), slice(1,7))
        self.assertEqual(dimrange.sliceOnLength(7), slice(1,7))
        self.assertEqual(dimrange.sliceOnLength(6), slice(1,6))
        
        dimrange = listwrap.DimensionRange((5,10), slice(6))
        self.assertEqual(dimrange.sliceOnLength(10), slice(5,10))
        self.assertEqual(dimrange.sliceOnLength(7), slice(5,7))
        self.assertEqual(dimrange.sliceOnLength(6), slice(5,6))
        self.assertEqual(dimrange.sliceOnLength(5), slice(5,5))
        self.assertEqual(dimrange.sliceOnLength(4), slice(4,4))
        self.assertEqual(dimrange.sliceOnLength(1), slice(1,1))
        self.assertEqual(dimrange.sliceOnLength(0), slice(0,0))
        
        # Check negative lengths
        self.assertEqual(dimrange.sliceOnLength(-1), slice(0,0))
        
        # Second slice outside of first slice range
        dimrange = listwrap.DimensionRange((2,4), slice(3,5))
        self.assertEqual(dimrange.sliceOnLength(10), slice(4,4))
        dimrange = listwrap.DimensionRange(*[slice(3,5), (2,4)])
        self.assertEqual(dimrange.sliceOnLength(10), slice(5,5))
        
        # Check step size assignments
        dimrange = listwrap.DimensionRange((1,5), (2,4,2))
        self.assertEqual(dimrange.sliceOnLength(10), slice(3,5,2))
        dimrange = listwrap.DimensionRange(*[(1,12,2), (1,12,3)])
        self.assertEqual(dimrange.sliceOnLength(10), slice(2,10,6))
        self.assertEqual(dimrange.sliceOnLength(12), slice(2,12,6))
        
    def testCombinedDimensionRange(self):
        firstDimrange = listwrap.DimensionRange((0,4))
        secondDimrange = listwrap.DimensionRange((1,6), slice(7))
        dimrange = firstDimrange + secondDimrange
        self.assertEqual(dimrange.sliceOnLength(10), slice(1,4))
        self.assertEqual(dimrange.sliceOnLength(4), slice(1,4))
        self.assertEqual(dimrange.sliceOnLength(3), slice(1,3))
        self.assertEqual(dimrange.sliceOnLength(1), slice(1,1))
        
        # Should be the same as __add__
        dimrange = firstDimrange.getCombinedDimensionRange(secondDimrange)
        self.assertEqual(dimrange.sliceOnLength(10), slice(1,4))
        self.assertEqual(dimrange.sliceOnLength(4), slice(1,4))
        self.assertEqual(dimrange.sliceOnLength(3), slice(1,3))
        self.assertEqual(dimrange.sliceOnLength(1), slice(1,1))
        
        # Make sure we throw an exception if the wrong type is passed
        self.assertRaises(ValueError, 
                          firstDimrange.getCombinedDimensionRange, 
                          [(1,6), slice(7)])
            
    def testListSubsetBasics(self):
        test = range(1,9)
        wrap = listwrap.FixedListSubset(test)
        
        # Check that we can iterate over the list
        count = 0
        for i,val in enumerate(wrap):
            self.assertEqual(i+1, val)
            count += 1
            
        # Ensure we saw all items in test
        self.assertEqual(len(test), count)
        
        # Ensure our wrapper has the same length
        self.assertEqual(len(test), len(wrap))
        
        # Try restricting our range
        wrap = listwrap.FixedListSubset(test, slice(1,4))
        self.assertEqual(len(wrap), 3)
        count = 0
        for i,val in enumerate(wrap):
            self.assertEqual(i+2, val)
            count += 1
            
        # Ensure our wrapper has the same length
        self.assertEqual(count, len(wrap))
        
        wrap = listwrap.FixedListSubset(wrap)
        self.assertEqual(len(wrap), 3)
        wrap = listwrap.FixedListSubset(wrap, slice(1,3))
        self.assertEqual(len(wrap), 2)
        
    def testListSubsetGetter(self):
        test = range(1,9)
        wrap = listwrap.FixedListSubset(test, (2,6))
        
        # Check that we can iterate over the list
        count = 0
        for i,val in enumerate(wrap):
            self.assertEqual(i+3, val)
            count += 1
            
        # Ensure we saw all items in test
        self.assertEqual(len(wrap), count)
        
        # Check a direct get requst
        self.assertEqual(wrap[0], test[2])
        
        # Try a single range request
        wrapSub = wrap[1:3]
        self.assertEqual(len(wrapSub), 2)
        self.assertEqual(wrapSub[0], test[3])
        
        # Try operators on multi-dimension lists
        test = [[1,2,3],[4,5],[6,7,8],9]
        wrap = listwrap.FixedListSubset(test)
        wrapSub = wrap[1:3]
        self.assertEqual(len(wrapSub), 2)
        self.assertEqual(wrapSub[0], test[1])
        
        # Check a multi-dimension subselection definition
        wrapSub = wrap[0:2, 1:]
        self.assertEqual(len(wrapSub), 2)
        for dimension in xrange(len(wrapSub)):
            self.assertEqual(len(wrapSub[dimension]), len(test[dimension][1:]))
            for elemIndex in xrange(len(wrapSub[dimension])):
                self.assertEqual(wrapSub[dimension][elemIndex], test[dimension][1+elemIndex])
                
        # Make sure we can select an element at a dimensional depth
        self.assertEqual(wrapSub[1][0], test[1][1])
        
    def testListSubsetIters(self):
        test = range(1,11,3)
        wrap = listwrap.FixedListSubset(test, (0,4,2))
        self.assertEqual(len(wrap), len(range(1,11,6)))
        for elem,match in zip(wrap, range(1,11,6)):
            self.assertEqual(match, elem)
            
    '''
    This is a difficult test with many dimensions. The 
    subindices and subsplices should all behave like
    normal multi-dimension lists.
    '''
    def testListSubsetSubSlices(self):
        test = [[1,2,3,4,5,6,7,8], [5,4,3,2,1,0]]
        wrap = listwrap.FixedListSubset(test)
        self.assertEqual(wrap[0, 0], 1)
        self.assertEqual(wrap[0, :1].compressRangesToLists(), [1])
        self.assertEqual(list(wrap[0, :1]), [1])
        
        test = [[[0,1,2],['a','b','c']],[[3,4,5]],[6,7,8]]
        wrap = listwrap.FixedListSubset(test)
        self.assertEqual(wrap[0, 0], [0,1,2])
        self.assertEqual(wrap[0, 1:2, 1:3].compressRangesToLists(), [['b','c']])
        self.assertEqual(wrap[0, 1, 1:3].compressRangesToLists(), ['b','c'])
        self.assertEqual(wrap[0, 0, 1:3].compressRangesToLists(), [1,2])
        self.assertEqual(wrap[1, 0, 1:3].compressRangesToLists(), [4,5])
        self.assertEqual(wrap[0:2, :, :2].compressRangesToLists(), [[[0,1],['a','b']],[[3,4]]])
        
        # These access non-existent elements in the last sublist
        self.assertRaises(IndexError, wrap.__getitem__, [(3, 0, slice(1,3))])
        badwrap = wrap[:,:,1:3]
        self.assertRaises(IndexError, badwrap.compressRangesToLists)
        
        
    def testSublistCopy(self):
        test = range(1,9)
        wrap = listwrap.FixedListSubset(test, (2,6))
        testsub = wrap.compressRangesToLists()
        
        self.assertEqual(type(testsub), type([]))
        self.assertEqual(len(testsub), 4)
        self.assertEqual(testsub, test[2:6])
            
        test = [[1,2],[3,4,5],[6,7,8]]
        wrap = listwrap.FixedListSubset(test)
        wrapsub = wrap[:, 1:]
        #wrapsub = listwrap.FixedListSubset(test, slice(None), (1,None))
        testsub = wrapsub.compressRangesToLists()
        self.assertEqual(testsub, [[2],[4,5],[7,8]])
        
        test = [[1,2],[3,4,5],[6,7,8],9]
        wrap = listwrap.FixedListSubset(test)
        wrapsub = wrap[:, 1:]
        # The 9 should blow up when we try to index it
        self.assertRaises(IndexError, wrapsub.compressRangesToLists)
        
        # Try deep copy
        test = [[1,2],[3,4,5],[6,7,8]]
        wrap = listwrap.FixedListSubset(test)
        wrapsub = wrap[:, 1:]
        testsub = wrapsub.deepCopyAsList()
        # Check that all values are present
        for i in xrange(len(testsub)):
            for j in xrange(len(testsub[i])):
                self.assertEqual(testsub[i][j], test[i][j+1])
                
        # Increment all of test's values by 1
        for i in xrange(len(test)):
            for j in xrange(len(test[i])):
                test[i][j] += 1
        
        # Check that the copy didn't update
        for i in xrange(len(testsub)):
            for j in xrange(len(testsub[i])):
                self.assertEqual(testsub[i][j], test[i][j+1]-1)
                
        # Check that shallow copy keeps references when it should
        import copy
        wrapsub = listwrap.FixedListSubset(test)[1:]
        wrapcpy = copy.copy(wrapsub)
        self.assertEqual(type(wrapcpy), type(wrapsub))
        wrapcpy[1][1] = 10
        self.assertEqual(wrapcpy[1][1], wrapsub[1][1])
        
        # Check that deep copy keeps no references
        test = [[1,2],[3,4,5],[6,7,8]]
        wrapsub = listwrap.FixedListSubset(test)[1:]
        wrapcpy = copy.deepcopy(wrapsub)
        self.assertEqual(type(wrapcpy), type(wrapsub))
        test[1][1] = 10
        # wrapsub should reference test, and wrapcpy should have
        # its own copy of the data
        self.assertNotEqual(wrapcpy[0][1], wrapsub[0][1])
        
    def testZeroList(self):
        dataLen = 10
        zlist = listwrap.ZeroList(dataLen)
        self.assertEqual(len(zlist), dataLen)
        self.assertRaises(IndexError, zlist.__getitem__, dataLen)
        
        # Try iterating
        for i in xrange(dataLen):
            self.assertEqual(zlist[i], 0)
        for z in zlist:
            self.assertEqual(z, 0)
            
        zsublist = zlist[1:dataLen]
        self.assertEqual(len(zsublist), dataLen-1)
        for i in xrange(dataLen-1):
            self.assertEqual(zlist[i], 0)
            
        zsublist = zlist[:]
        self.assertEqual(len(zsublist), dataLen)
        zsublist = zlist[0:]
        self.assertEqual(len(zsublist), dataLen)
        zsublist = zlist[:dataLen]
        self.assertEqual(len(zsublist), dataLen)
        zsublist = zlist[0:dataLen:2]
        self.assertEqual(len(zsublist), dataLen/2)
        
        # Check negative indicies
        self.assertEqual(zlist[-1], 0)
        zsublist = zlist[-1:]
        self.assertEqual(len(zsublist), 1)

if __name__ == "__main__":
    unittest.main()