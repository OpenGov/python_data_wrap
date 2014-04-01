# This import fixes sys.path issues
import parentpath

from datawrap import listwrap
import unittest

class ListWrapTest(unittest.TestCase):
    '''
    Performs an exhaustive test suite on the ListWrap class.
    '''
    def test_non_str_len(self):
        testItem = []
        self.assertEqual(listwrap.non_str_len(testItem), 0)
        testItem.append(1)
        self.assertEqual(listwrap.non_str_len(testItem), 1)
        self.assertRaises(TypeError, listwrap.non_str_len, 1)
        self.assertRaises(TypeError, listwrap.non_str_len, "")
        self.assertRaises(TypeError, listwrap.non_str_len, "a longer string")
        self.assertRaises(TypeError, listwrap.non_str_len, None)

    def test_non_str_len_no_throw(self):
        testItem = []
        self.assertEqual(listwrap.non_str_len_no_throw(testItem), 0)
        testItem.append(1)
        self.assertEqual(listwrap.non_str_len_no_throw(testItem), 1)
        
        self.assertEqual(listwrap.non_str_len_no_throw(1), 0)
        self.assertEqual(listwrap.non_str_len_no_throw(""), 0)
        self.assertEqual(listwrap.non_str_len_no_throw("a longer string"), 0)
        self.assertEqual(listwrap.non_str_len_no_throw(None), 0)
        
    def test_get_non_negative_index(self):
        self.assertEqual(listwrap.get_non_negative_index(0, 2), 0)
        self.assertEqual(listwrap.get_non_negative_index(1, 2), 1)
        self.assertEqual(listwrap.get_non_negative_index(2, 2), 2)
        self.assertEqual(listwrap.get_non_negative_index(3, 2), 3)
        self.assertEqual(listwrap.get_non_negative_index(-1, 2), 1)
        self.assertEqual(listwrap.get_non_negative_index(-2, 2), 0)
        self.assertEqual(listwrap.get_non_negative_index(-3, 2), 1)
        self.assertEqual(listwrap.get_non_negative_index(-13, 4), 3)
        
        # Ensure 0's don't blow up the calls
        self.assertEqual(listwrap.get_non_negative_index(0, 0), 0)
        self.assertEqual(listwrap.get_non_negative_index(10, 0), 10)
        self.assertEqual(listwrap.get_non_negative_index(-1, 0), 0)
        
    def test_get_restricted_index(self):
        self.assertEqual(listwrap.get_restricted_index(0, 2), 0)
        self.assertEqual(listwrap.get_restricted_index(1, 2), 1)
        self.assertEqual(listwrap.get_restricted_index(2, 2), 2)
        self.assertEqual(listwrap.get_restricted_index(3, 2), 2)
        self.assertEqual(listwrap.get_restricted_index(-1, 2), 1)
        self.assertEqual(listwrap.get_restricted_index(-2, 2), 0)
        self.assertEqual(listwrap.get_restricted_index(-3, 2), 1)
        self.assertEqual(listwrap.get_restricted_index(-13, 4), 3)
        
        # Ensure 0's don't blow up the calls
        self.assertEqual(listwrap.get_restricted_index(0, 0), 0)
        self.assertEqual(listwrap.get_restricted_index(10, 0), 0)
        self.assertEqual(listwrap.get_restricted_index(-1, 0), 0)
        
        # Check with length_index_allowed False
        self.assertEqual(listwrap.get_restricted_index(0, 2, False), 0)
        self.assertEqual(listwrap.get_restricted_index(1, 2, False), 1)
        self.assertEqual(listwrap.get_restricted_index(2, 2, False), 1)
        self.assertEqual(listwrap.get_restricted_index(3, 2, False), 1)
        self.assertEqual(listwrap.get_restricted_index(0, 0, False), 0)
        self.assertEqual(listwrap.get_restricted_index(10, 0, False), 0)
        self.assertEqual(listwrap.get_restricted_index(-1, 0, False), 0)
        
    def test_get_pos_slice(self):
        data_len = 10
        # Check slices
        self.assertEqual(listwrap.get_true_slice(slice(None,None,None), data_len), slice(None,None,None))
        self.assertEqual(listwrap.get_true_slice(slice(1,None,None), data_len), slice(1,None,None))
        self.assertEqual(listwrap.get_true_slice(slice(None,2,None), data_len), slice(None,2,None))
        self.assertEqual(listwrap.get_true_slice(slice(None,None,3), data_len), slice(None,None,3))
        self.assertEqual(listwrap.get_true_slice(slice(1,2,None), data_len), slice(1,2,None))
        self.assertEqual(listwrap.get_true_slice(slice(1,None,3), data_len), slice(1,None,3))
        self.assertEqual(listwrap.get_true_slice(slice(None,2,3), data_len), slice(None,2,3))
        self.assertEqual(listwrap.get_true_slice(slice(1,2,3), data_len), slice(1,2,3))
        
        # Check tuples of length 3
        self.assertEqual(listwrap.get_true_slice((None,None,None), data_len), slice(None,None,None))
        self.assertEqual(listwrap.get_true_slice((1,None,None), data_len), slice(1,None,None))
        self.assertEqual(listwrap.get_true_slice((None,2,None), data_len), slice(None,2,None))
        self.assertEqual(listwrap.get_true_slice((None,None,3), data_len), slice(None,None,3))
        self.assertEqual(listwrap.get_true_slice((1,2,None), data_len), slice(1,2,None))
        self.assertEqual(listwrap.get_true_slice((1,None,3), data_len), slice(1,None,3))
        self.assertEqual(listwrap.get_true_slice((None,2,3), data_len), slice(None,2,3))
        self.assertEqual(listwrap.get_true_slice((1,2,3), data_len), slice(1,2,3))
        
        # Check all other valid inputs
        self.assertEqual(listwrap.get_true_slice((1,None), data_len), slice(1,None,None))
        self.assertEqual(listwrap.get_true_slice((None,None), data_len), slice(None,None,None))
        self.assertEqual(listwrap.get_true_slice((None,2), data_len), slice(None,2,None))
        self.assertEqual(listwrap.get_true_slice((1,None), data_len), slice(1,None,None))
        self.assertEqual(listwrap.get_true_slice((1,2), data_len), slice(1,2,None))
        self.assertEqual(listwrap.get_true_slice((1,), data_len), slice(1,2,None))
        self.assertEqual(listwrap.get_true_slice(1, data_len), slice(1,2,None))
        
        # Check values outside range
        self.assertEqual(listwrap.get_true_slice(slice(1,data_len+2), data_len), slice(1,data_len,None))
        self.assertEqual(listwrap.get_true_slice(slice(-1,data_len+2), data_len), slice(data_len-1,data_len,None))
        self.assertEqual(listwrap.get_true_slice(slice(-1*data_len,data_len+2), data_len), slice(0,data_len,None))
        self.assertEqual(listwrap.get_true_slice(slice(-10*data_len,0,0), data_len), slice(0,0,0))
    
    def test_list_iter(self):
        test = []
        test_iter = listwrap.ListIter(test)
        self.assertRaises(StopIteration, test_iter.next)
        # Check that it iterates in the correct order
        test = [1,2,3,4,5,6]
        count = 0
        test_iter = listwrap.ListIter(test)
        for i,val in enumerate(test_iter):
            self.assertEqual(i+1, val)
            count += 1
        # Ensure we saw all items in test
        self.assertEqual(len(test), count)
        # Check __iter__
        test_iter = test_iter.__iter__()
        for i,val in enumerate(test_iter):
            self.assertEqual(i+1, val)
            
    def test_dimension_range(self):
        dim_range = listwrap.DimensionRange()
        self.assertEqual(len(dim_range), 0)
        
        # Check if the tuple gets converted to a slice
        dim_range.add_range((1,2))
        self.assertEqual(len(dim_range), 1)
        self.assertEqual(type(dim_range[0]), slice)
        self.assertEqual(dim_range[0], slice(1,2,None))
        
        # Check ordering of slice
        dim_range.add_range((1,2,3))
        self.assertEqual(len(dim_range), 2)
        self.assertEqual(type(dim_range[1]), slice)
        self.assertEqual(dim_range[1], slice(1,2,3))
        
        # Check pushing a slice
        dim_range.add_range(slice(1,2,3))
        self.assertEqual(len(dim_range), 3)
        self.assertEqual(type(dim_range[2]), slice)
        self.assertEqual(dim_range[2], slice(1,2,3))
        
        # Make sure the constructor works as well
        dim_range = listwrap.DimensionRange((1,2,3), (4,5), slice(6))
        self.assertEqual(len(dim_range), 3)
        self.assertEqual(type(dim_range[0]), slice)
        self.assertEqual(dim_range[0], slice(1,2,3))
        self.assertEqual(type(dim_range[1]), slice)
        self.assertEqual(dim_range[1], slice(4,5,None))
        self.assertEqual(type(dim_range[2]), slice)
        self.assertEqual(dim_range[2], slice(None,6,None))
        
        # Try copying the Range
        dim_range = listwrap.DimensionRange(dim_range)
        self.assertEqual(len(dim_range), 3)
        self.assertEqual(type(dim_range[0]), slice)
        self.assertEqual(dim_range[0], slice(1,2,3))
        self.assertEqual(type(dim_range[1]), slice)
        self.assertEqual(dim_range[1], slice(4,5,None))
        self.assertEqual(type(dim_range[2]), slice)
        self.assertEqual(dim_range[2], slice(None,6,None))
        
    def test_slice_on_length(self):
        dim_range = listwrap.DimensionRange((0,4), (1,6), slice(7))
        self.assertEqual(dim_range.slice_on_length(10), slice(1,4))
        self.assertEqual(dim_range.slice_on_length(4), slice(1,4))
        self.assertEqual(dim_range.slice_on_length(3), slice(1,3))
        self.assertEqual(dim_range.slice_on_length(1), slice(1,1))
        
        dim_range = listwrap.DimensionRange((1,10), slice(6))
        # yes, this should be slice(1,7) as slice(6) is applied After (1,10)
        self.assertEqual(dim_range.slice_on_length(10), slice(1,7))
        self.assertEqual(dim_range.slice_on_length(7), slice(1,7))
        self.assertEqual(dim_range.slice_on_length(6), slice(1,6))
        
        dim_range = listwrap.DimensionRange((5,10), slice(6))
        self.assertEqual(dim_range.slice_on_length(10), slice(5,10))
        self.assertEqual(dim_range.slice_on_length(7), slice(5,7))
        self.assertEqual(dim_range.slice_on_length(6), slice(5,6))
        self.assertEqual(dim_range.slice_on_length(5), slice(5,5))
        self.assertEqual(dim_range.slice_on_length(4), slice(4,4))
        self.assertEqual(dim_range.slice_on_length(1), slice(1,1))
        self.assertEqual(dim_range.slice_on_length(0), slice(0,0))
        
        # Check negative lengths
        self.assertEqual(dim_range.slice_on_length(-1), slice(0,0))
        
        # Second slice outside of first slice range
        dim_range = listwrap.DimensionRange((2,4), slice(3,5))
        self.assertEqual(dim_range.slice_on_length(10), slice(4,4))
        dim_range = listwrap.DimensionRange(*[slice(3,5), (2,4)])
        self.assertEqual(dim_range.slice_on_length(10), slice(5,5))
        
        # Check step size assignments
        dim_range = listwrap.DimensionRange((1,5), (2,4,2))
        self.assertEqual(dim_range.slice_on_length(10), slice(3,5,2))
        dim_range = listwrap.DimensionRange(*[(1,12,2), (1,12,3)])
        self.assertEqual(dim_range.slice_on_length(10), slice(2,10,6))
        self.assertEqual(dim_range.slice_on_length(12), slice(2,12,6))
        
    def test_combined_dimension_range(self):
        first_dim_range = listwrap.DimensionRange((0,4))
        second_dim_range = listwrap.DimensionRange((1,6), slice(7))
        dim_range = first_dim_range + second_dim_range
        self.assertEqual(dim_range.slice_on_length(10), slice(1,4))
        self.assertEqual(dim_range.slice_on_length(4), slice(1,4))
        self.assertEqual(dim_range.slice_on_length(3), slice(1,3))
        self.assertEqual(dim_range.slice_on_length(1), slice(1,1))
        
        # Should be the same as __add__
        dim_range = first_dim_range.get_combined_dimension_range(second_dim_range)
        self.assertEqual(dim_range.slice_on_length(10), slice(1,4))
        self.assertEqual(dim_range.slice_on_length(4), slice(1,4))
        self.assertEqual(dim_range.slice_on_length(3), slice(1,3))
        self.assertEqual(dim_range.slice_on_length(1), slice(1,1))
        
        # Make sure we throw an exception if the wrong type is passed
        self.assertRaises(ValueError, 
                          first_dim_range.get_combined_dimension_range, 
                          [(1,6), slice(7)])
            
    def test_list_subset_basics(self):
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
        
    def test_list_subset_getter(self):
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
        wrap_sub = wrap[1:3]
        self.assertEqual(len(wrap_sub), 2)
        self.assertEqual(wrap_sub[0], test[3])
        
        # Try operators on multi-dimension lists
        test = [[1,2,3],[4,5],[6,7,8],9]
        wrap = listwrap.FixedListSubset(test)
        wrap_sub = wrap[1:3]
        self.assertEqual(len(wrap_sub), 2)
        self.assertEqual(wrap_sub[0], test[1])
        
        # Check a multi-dimension subselection definition
        wrap_sub = wrap[0:2, 1:]
        self.assertEqual(len(wrap_sub), 2)
        for dimension in xrange(len(wrap_sub)):
            self.assertEqual(len(wrap_sub[dimension]), len(test[dimension][1:]))
            for elemIndex in xrange(len(wrap_sub[dimension])):
                self.assertEqual(wrap_sub[dimension][elemIndex], test[dimension][1+elemIndex])
                
        # Make sure we can select an element at a dimensional depth
        self.assertEqual(wrap_sub[1][0], test[1][1])
        
    def test_list_subset_iters(self):
        test = range(1,11,3)
        wrap = listwrap.FixedListSubset(test, (0,4,2))
        self.assertEqual(len(wrap), len(range(1,11,6)))
        for elem,match in zip(wrap, range(1,11,6)):
            self.assertEqual(match, elem)
            
    def test_list_subset_subslices(self):
        '''
        This is a difficult test with many dimensions. The subindices and 
        subsplices should all behave like normal multi-dimension lists.
        '''
        test = [[1,2,3,4,5,6,7,8], [5,4,3,2,1,0]]
        wrap = listwrap.FixedListSubset(test)
        self.assertEqual(wrap[0, 0], 1)
        self.assertEqual(wrap[0, :1].compress_ranges_to_lists(), [1])
        self.assertEqual(list(wrap[0, :1]), [1])
        
        test = [[[0,1,2],['a','b','c']],[[3,4,5]],[6,7,8]]
        wrap = listwrap.FixedListSubset(test)
        self.assertEqual(wrap[0, 0], [0,1,2])
        self.assertEqual(wrap[0, 1:2, 1:3].compress_ranges_to_lists(), [['b','c']])
        self.assertEqual(wrap[0, 1, 1:3].compress_ranges_to_lists(), ['b','c'])
        self.assertEqual(wrap[0, 0, 1:3].compress_ranges_to_lists(), [1,2])
        self.assertEqual(wrap[1, 0, 1:3].compress_ranges_to_lists(), [4,5])
        self.assertEqual(wrap[0:2, :, :2].compress_ranges_to_lists(), [[[0,1],['a','b']],[[3,4]]])
        
        # These access non-existent elements in the last sublist
        self.assertRaises(IndexError, wrap.__getitem__, [(3, 0, slice(1,3))])
        badwrap = wrap[:,:,1:3]
        self.assertRaises(IndexError, badwrap.compress_ranges_to_lists)
        
        
    def test_sublist_copy(self):
        test = range(1,9)
        wrap = listwrap.FixedListSubset(test, (2,6))
        test_sub = wrap.compress_ranges_to_lists()
        
        self.assertEqual(type(test_sub), type([]))
        self.assertEqual(len(test_sub), 4)
        self.assertEqual(test_sub, test[2:6])
            
        test = [[1,2],[3,4,5],[6,7,8]]
        wrap = listwrap.FixedListSubset(test)
        wrap_sub = wrap[:, 1:]
        #wrap_sub = listwrap.FixedListSubset(test, slice(None), (1,None))
        test_sub = wrap_sub.compress_ranges_to_lists()
        self.assertEqual(test_sub, [[2],[4,5],[7,8]])
        
        test = [[1,2],[3,4,5],[6,7,8],9]
        wrap = listwrap.FixedListSubset(test)
        wrap_sub = wrap[:, 1:]
        # The 9 should blow up when we try to index it
        self.assertRaises(IndexError, wrap_sub.compress_ranges_to_lists)
        
        # Try deep copy
        test = [[1,2],[3,4,5],[6,7,8]]
        wrap = listwrap.FixedListSubset(test)
        wrap_sub = wrap[:, 1:]
        test_sub = wrap_sub.deep_copy_as_list()
        # Check that all values are present
        for i in xrange(len(test_sub)):
            for j in xrange(len(test_sub[i])):
                self.assertEqual(test_sub[i][j], test[i][j+1])
                
        # Increment all of test's values by 1
        for i in xrange(len(test)):
            for j in xrange(len(test[i])):
                test[i][j] += 1
        
        # Check that the copy didn't update
        for i in xrange(len(test_sub)):
            for j in xrange(len(test_sub[i])):
                self.assertEqual(test_sub[i][j], test[i][j+1]-1)
                
        # Check that shallow copy keeps references when it should
        import copy
        wrap_sub = listwrap.FixedListSubset(test)[1:]
        wrap_copy = copy.copy(wrap_sub)
        self.assertEqual(type(wrap_copy), type(wrap_sub))
        wrap_copy[1][1] = 10
        self.assertEqual(wrap_copy[1][1], wrap_sub[1][1])
        
        # Check that deep copy keeps no references
        test = [[1,2],[3,4,5],[6,7,8]]
        wrap_sub = listwrap.FixedListSubset(test)[1:]
        wrap_copy = copy.deepcopy(wrap_sub)
        self.assertEqual(type(wrap_copy), type(wrap_sub))
        test[1][1] = 10
        # wrap_sub should reference test, and wrap_copy should have
        # its own copy of the data
        self.assertNotEqual(wrap_copy[0][1], wrap_sub[0][1])
        
    def test_zero_list(self):
        data_len = 10
        zlist = listwrap.ZeroList(data_len)
        self.assertEqual(len(zlist), data_len)
        self.assertRaises(IndexError, zlist.__getitem__, data_len)
        
        # Try iterating
        for i in xrange(data_len):
            self.assertEqual(zlist[i], 0)
        for z in zlist:
            self.assertEqual(z, 0)
            
        zsublist = zlist[1:data_len]
        self.assertEqual(len(zsublist), data_len-1)
        for i in xrange(data_len-1):
            self.assertEqual(zlist[i], 0)
            
        zsublist = zlist[:]
        self.assertEqual(len(zsublist), data_len)
        zsublist = zlist[0:]
        self.assertEqual(len(zsublist), data_len)
        zsublist = zlist[:data_len]
        self.assertEqual(len(zsublist), data_len)
        zsublist = zlist[0:data_len:2]
        self.assertEqual(len(zsublist), data_len/2)
        
        # Check negative indicies
        self.assertEqual(zlist[-1], 0)
        zsublist = zlist[-1:]
        self.assertEqual(len(zsublist), 1)

if __name__ == "__main__":
    unittest.main()