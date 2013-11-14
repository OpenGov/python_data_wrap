import collections

def non_str_len(item):
    '''
    Helper function for checking non-string item length
    '''
    if isinstance(item, basestring):
        raise TypeError('String passed to non_str_len')
    return len(item)

def has_len(item):
    '''
    Helper function for determining if object has __len__ defined
    '''
    try:
        len(item)
        return True
    except:
        return False

def non_str_len_no_throw(item):
    '''
    Helper function for checking non-string item length.
    Returns None on failure instead of throwing a TypeError.
    '''
    try:
        return non_str_len(item)
    except TypeError:
        return 0
    
def get_non_negative_index(index, length):
    '''
    Converts negative indices to positive ones
    '''
    while index < 0:
        # Catch the 0 length case
        if length > 0:
            index += length
        else:
            index = 0
    return index

def is_slice_or_dim_range(key):
    '''
    Checks if a particular key is a slice or DimensionRange
    '''
    return isinstance(key, (slice, DimensionRange))

def is_slice_or_dim_range_request(key, depth=0):
    '''
    Checks if a particular key is a slice, DimensionRange or
    list of those types
    '''
    # Slice, DimensionRange, or list of those elements
    return (is_slice_or_dim_range(key) or
            # Don't check more than the first depth
            (depth == 0 and non_str_len_no_throw(key) > 0 and 
             all(is_slice_or_dim_range_request(subkey, depth+1) for subkey in key)))

def get_restricted_index(index, length, length_index_allowed=True):
    '''
    Converts negative indices to positive ones and indices above length to length or 
    length-1 depending on lengthAllowed.
    '''
    if index and index >= length:
        index = length if length_index_allowed else length-1
    return get_non_negative_index(index, length)

def get_true_slice(dims, data_len):
    '''
    Converts various size tuples or slices representing data ranges returns a 
    new slice with all non-negative (or None) values.
    '''
    rangeLen = non_str_len_no_throw(dims)
    
    # Get the range qualifier for length
    if isinstance(dims, slice):
        start = get_restricted_index(int(dims.start), data_len) if dims.start != None else dims.start
        stop = get_restricted_index(int(dims.stop), data_len) if dims.stop != None else dims.stop
        step = get_restricted_index(int(dims.step), data_len) if dims.step != None else dims.step
    elif rangeLen > 3:
        raise AttributeError(str(dims)+' length is > 3')
    elif rangeLen == 3:
        start = get_restricted_index(int(dims[0]), data_len) if dims[0] != None else dims[0]
        stop = get_restricted_index(int(dims[1]), data_len) if dims[1] != None else dims[1]
        step = get_restricted_index(int(dims[2]), data_len) if dims[2] != None else dims[2]
    elif rangeLen == 2:
        start = get_restricted_index(int(dims[0]), data_len) if dims[0] != None else dims[0]
        stop = get_restricted_index(int(dims[1]), data_len) if dims[1] != None else dims[1]
        step = None
    elif rangeLen == 1:
        start = get_restricted_index(int(dims[0]), data_len) if dims[0] != None else dims[0]
        stop = get_restricted_index(int(dims[0]), data_len)+1 if dims[0] != None else dims[0]
        step = None
    elif dims != None:
        start = get_restricted_index(int(dims), data_len) if dims != None else dims
        stop = get_restricted_index(int(dims), data_len)+1 if dims != None else dims
        step = None
    else:
        start = None
        stop = None
        step = None
        
    return slice(start, stop, step)

class DimensionRange(collections.MutableMapping):
    '''
    Defines an ordered set of dimensions. These can be used to scope
    and select subsets of data. These act much the same as slices
    in standard list operators but can be combined easily and have
    an application for a depth of dimensions.
    
    Args:
        ordered_ranges: The arguments which provide the ordered 
            restrictions at each sub-dimension. 
    '''
    def __init__(self, *ordered_ranges):
        self.ordered_ranges = []
        for range_restriction in ordered_ranges:
            self.add_range(range_restriction)
            
    def __add__(self, other):
        '''
        Creates a new DimensionRange object with other
        concatenated to the end of the range specifications.
        '''
        if isinstance(other, DimensionRange):
            return DimensionRange(self, other)
        else:
            raise ValueError(str(other)+" is not of type DimensionRange")
    
    def __iadd__(self, other):
        self.__init__(self + other)
        
    def get_combined_dimension_range(self, other):
        '''Same as __add__(self, other)'''
        return self + other
            
    def slice_on_length(self, data_len, *addSlices):
        '''
        Returns a slice representing the dimension range
        restrictions applied to a list of length data_len.
        
        If addSlices contains additional slice requirements,
        they are processed in the order they are given.
        '''
        if len(self.ordered_ranges) + len(addSlices) == 0:
            return slice(None,None,None)
        ranges = self.ordered_ranges
        if len(addSlices) > 0:
            ranges = ranges + DimensionRange(*addSlices).ordered_ranges
        return self._combine_lists_of_ranges_on_length(data_len, *ranges)
        
    def _combine_ranges_on_length(self, data_len, first, second):
        '''
        Combines a first range with a second range, where the second
        range is considered within the scope of the first.
        '''
        first = get_true_slice(first, data_len)
        second = get_true_slice(second, data_len)
        final_start, final_step, final_stop = (None, None, None)
        
        # Get our start
        if first.start == None and second.start == None:
            final_start = None
        else:
            final_start = (first.start if first.start else 0)+(second.start if second.start else 0)
            
        # Get our stop
        if second.stop == None:
            final_stop = first.stop
        elif first.stop == None:
            final_stop = (first.start if first.start else 0) + second.stop
        else:
            final_stop = min(first.stop, (first.start if first.start else 0) + second.stop)
            
        # Get our step
        if first.step == None and second.step == None:
            final_step = None
        else:
            final_step = (first.step if first.step else 1)*(second.step if second.step else 1)
            
        # If we have a start above our stop, set them to be equal
        if final_start > final_stop:
            final_start = final_stop
        
        return slice(final_start, final_stop, final_step)
        
    def _combine_lists_of_ranges_on_length(self, data_len, first, *range_list):
        '''
        Combines an arbitrary length list of ranges into a single slice.
        '''
        current_range = first
        for next_range in range_list:
            current_range = self._combine_ranges_on_length(data_len, current_range, next_range)
        return current_range
        
    def __getitem__(self, index):
        return self.ordered_ranges[index]
    
    def _slicify(self, range_restriction):
        if isinstance(range_restriction, slice):
            return range_restriction
        elif non_str_len_no_throw(range_restriction) == 0:
            return slice(range_restriction, range_restriction+1, None)
        elif len(range_restriction) > 0:
            return slice(*range_restriction)
        else:
            return slice(None, None, None)
        
    def __str__(self):
        return "DimensionRange" + self.ordered_ranges.__str__()
    
    def __repr__(self):
        return "DimensionRange" + self.ordered_ranges.__repr__()
    
    def add_range(self, range_restriction):
        # Check for nested ranges
        if isinstance(range_restriction, DimensionRange):
            for range_restriction in range_restriction.ordered_ranges:
                self.add_range(range_restriction)
        else:
            sliced_range = self._slicify(range_restriction)
            # If the slice is a pass all, don't bother appending
            if (sliced_range.start != None or
                sliced_range.stop != None or
                sliced_range.step != None):
                self.ordered_ranges.append(sliced_range)
    
    def __setitem__(self, index, range_restriction):
        self.ordered_ranges[index] = self._slicify(range_restriction)
        
    def __len__(self):
        return self.ordered_ranges.__len__()
    
    def __delitem__(self, index):
        self.ordered_ranges.__delitem__(index)
        
    def __iter__(self):
        return self.ordered_ranges.__iter__()

class ListIter(object):
    '''
    Defines an iterator that relies on an object's __getitem__ 
    call to walk through all elements in the data object by 
    index. This is useful for wrapper on datasets, which return 
    new objects at each index, rather than an underlying 
    database's raw information.
    '''
    def __init__(self, iterable):
        self.data = iterable
        self._cursor = xrange(len(self.data)).__iter__()
    
    def __iter__(self):
        return self
    
    def next(self):
        return self.data[self._cursor.next()]
    
class FixedListSubset(collections.Sequence):
    '''
    Wraps list-style data with an iterator and getters which only return a 
    subset of the original data.
    
    FixedListSubset([(1,2,3), (4,5,6)], 2) would effectively represent 
    the list [2, 5]
    
    FixedListSubset([(1,2,3), (4,5,6)], (1,3)) => [(1,2), (4,5)]
    
    dataRange of 0 on a non-iterable sublists will return the non-iterable 
    element as though it were a tuple of one element.
    
    Args:
        data: Fixed length list of arbitrary data.
        dimension_ranges: An arbitrary number of dimension restrictions 
            that are combined to form the subset.
    '''
    def __init__(self, data, *dimension_ranges):
        '''
        Assumes data is of fixed length. The parameter dataRange can be an 
        Integer or a tuple of Integers (or None for full range) representing 
        the sub.
        '''
        # Used later for constructing new FixedLists, this
        # can be replaced by subclasses that want to create
        # a new type of list when returning sublists.
        self.builder = type(self)
        # Check for assignment from another FixedListSubset
        if isinstance(data, FixedListSubset):
            self._dim_ranges = self._combine_dimension_lists(data._dim_ranges, dimension_ranges)
            self._data = data._data
        # Otherwise construct our dim_ranges
        else:
            self._data = data
            self._dim_ranges = []
            # Convert the dimension inputs into DimensionRange objects
            for dim_range in dimension_ranges:
                self._dim_ranges.append(DimensionRange(dim_range))
        data_len = len(self._data)
        
        if len(self._dim_ranges) > 0:
            self.range = self._dim_ranges[0].slice_on_length(data_len)
        else:
            self.range = slice(None, None, None)
            
        # Get the length of the data
        start = self.range.start if self.range.start != None else 0
        # Check stop
        stop = self.range.stop if self.range.stop != None else data_len
        # Check step
        step = self.range.step if self.range.step != None else 1
        # Store our length, add step-1 to account for rounding
        self._length = (stop - start + step-1) / step
        
    def __len__(self):
        return self._length
    
    def _combine_dimension_lists(self, first_dims, second_dims):
        # Format first_dims and second_dims as lists
        first_dims_len = non_str_len_no_throw(first_dims)
        if not has_len(first_dims) or is_slice_or_dim_range(first_dims):
            first_dims = [first_dims]
            first_dims_len = 1
        second_dims_len = non_str_len_no_throw(second_dims)
        if not has_len(first_dims) or is_slice_or_dim_range(second_dims):
            second_dims = [second_dims]
            second_dims_len = 1
        
        # Our new list of dimension ranges
        constructed_dims = []
        
        # Rebuild the dimensions list for each dimension
        for i in xrange(max(first_dims_len, second_dims_len)):
            updated_dims = None
            if i < first_dims_len:
                if i < second_dims_len:
                    updated_dims = DimensionRange(first_dims[i]) + DimensionRange(second_dims[i])
                else:
                    updated_dims = DimensionRange(first_dims[i])
            elif i < second_dims_len:
                updated_dims = DimensionRange(second_dims[i])
            else:
                # Impossible scenario
                # So just stop if this happens somehow
                break
            constructed_dims.append(updated_dims)
            
        return constructed_dims
    
    def _get_single_depth(self, multi_index):
        '''
        Helper method for determining how many single index entries there 
        are in a particular multi-index
        '''
        single_depth = 0
        for subind in multi_index:
            if is_slice_or_dim_range(subind):
                break
            single_depth += 1
        return single_depth
    
    def _get_slice_request_data(self, index):
        '''
        Helper function which implements multi index requests for __getitem__.
        '''
        # Do a check on list indices for early error detection
        if not is_slice_or_dim_range(index):
            single_depth = self._get_single_depth(index)
            # Single value indices for first single_depth values
            if single_depth > 0:
                # We have integer request first
                subindicies = index[:single_depth]
                sublist = self
                # Use the other side of __getitem__ to grab subindices
                for sind in subindicies:
                    sublist = sublist[sind]
                # If we still have some index requests left or dimension
                # restrictions, then return a FixedListSubset
                if single_depth < len(index) or isinstance(sublist, FixedListSubset):
                    new_dim_ranges = self._combine_dimension_lists(self._dim_ranges, index)
                    return self.builder(sublist, *new_dim_ranges[single_depth:])
                # Otherwise our sublist is actually an element of the
                # original data, so just return it
                else:
                    return sublist
        new_dim_ranges = self._combine_dimension_lists(self._dim_ranges, index)
        return self.builder(self._data, *new_dim_ranges)
    
    def _get_single_index_request(self, index, set_to_value=False, value=None):
        '''
        Helper function which implements single index requests for __getitem__.
        '''
        adjusted_index = index
        # Multiply by step length
        if self.range.step:
            step = self.range.step
            adjusted_index *= self.range.step
        else:
            step = 1
            
        # Adjust for negative indicies
        adjusted_index = get_non_negative_index(adjusted_index, self._length)
        # Push forward by start length
        if self.range.start != None:
            adjusted_index += self.range.start
        # Push forward by start length
        stop_index = self.range.stop if self.range.stop != None else self._length*step
        if adjusted_index > stop_index:
            raise IndexError(index)
        elem = self._data[adjusted_index]
        # Check if we have further dimension requirements
        # NOTE: if we're given dimensions for non-dimensional data, 
        # this will blow up with an IndexError -- user should
        # not define this dimension with any restrictions
        if len(self._dim_ranges) > 1:
            if not has_len(elem):
                # We throw an IndexError instead of an AttributeError
                # because if can be caused by either sublist requests
                # or a bad constructor, and it's usually the former.
                raise IndexError("Element restricted by dimension_ranges "+
                                 str(self._dim_ranges[1:])+" is not subscriptable: "+
                                 "Dimension cannot be applied to elements with no len()")
            return self.builder(elem, *self._dim_ranges[1:])
        else:
            if set_to_value:
                self._data[adjusted_index] = value
            return elem
        
    def __getitem__(self, index):
        '''
        Handles an arbitrary number of dimensional definitions as
        well as the standard index requests. This getter can be
        treated as a list and will return the correct object or
        object wrapper for a particular index request.
        '''
        # Check if we have a list of dimensions or a slice request
        if non_str_len_no_throw(index) > 0 or is_slice_or_dim_range(index):
            return self._get_slice_request_data(index)
        # Do a normal get request on an index
        else:
            return self._get_single_index_request(index)
    
    def __iter__(self):
        # Default iterator doesn't work
        return ListIter(self)
    
    def __str__(self):
        # This can be expensive for high dimension lists.
        if self._length <= 100:
            return str(self.compress_ranges_to_lists())
        else:
            listString = str(self[:100].compress_ranges_to_lists())
            return listString[:-1] + ", ... ]"
        
    def __repr__(self):
        # This can be expensive for high dimension lists.
        return repr(self.compress_ranges_to_lists())
    
    def compress_ranges_to_lists(self):
        '''
        Converts the internal dimension ranges on lists into
        list of the restricted size. Thus all dimension rules
        are applied to all dimensions of the list wrapper
        and returned as a list (of lists).
        '''
        clist = []
        for elem in self:
            if isinstance(elem, FixedListSubset):
                clist.append(elem.compress_ranges_to_lists())
            else:
                clist.append(elem)
        return clist
    
    '''
    Acts much like compress_ranges_to_lists except it also performs a deepcopy 
    on the underlying data. Thus the return value is a true copy of original data.
    ''' 
    def deep_copy_as_list(self, memo=None):
        import copy
        if memo == None:
            memo = {}
        clist = []
        for elem in self:
            if isinstance(elem, FixedListSubset):
                clist.append(elem.deep_copy_as_list(memo))
            else:
                clist.append(copy.deepcopy(elem, memo))
        return clist
    
    def __copy__(self):
        return self.builder(self.compress_ranges_to_lists())
    
    def __deepcopy__(self, memo):
        return self.builder(self.deep_copy_as_list(memo))
    
class MutableListSubset(collections.MutableSequence, FixedListSubset):
    '''
    Wraps list-style data with an iterator and getters which only return 
    a subset of the original data. This class is much like FixedListSubset, 
    except you can set the value of elements at a specific index. If you 
    replace a dimensional element (i.e. the first dimension of a 2D table) 
    you can break the object's logic if the new element is not the same 
    size/dimensionality. For this reason this class is separate from 
    FixedListSubset.
    
    MutableListSubset([(1,2,3), (4,5,6)], 2) would effectively represent 
    the list [2, 5].
    
    MutableListSubset([(1,2,3), (4,5,6)], (1,3)) => [(1,2), (4,5)].
    
    dataRange of 0 on a non-iterable sublists will return the non-iterable 
    element as though it were a tuple of one element.
    
    Args:
        data: Fixed length list of arbitrary data.
        dimension_ranges: An arbitrary number of dimension restrictions that are 
            combined to form the subset.
    '''
    def __setitem__(self, index, value):
        self._get_single_index_request(index, True, value)
    
    def insert(self, index, value):
        raise NotImplementedError("Cannot insert into a List Subset")
    
    def __delitem__(self, index):
        raise NotImplementedError("Cannot delete from a List Subset")
    
class ZeroList(collections.Sequence):
    '''
    A constant list of zeros with fixed memory footprint. This is useful for 
    passing a placeholder instead of a real list, especially when the length 
    could be very large.
    
    Args:
        length: The number of 'zeros' this list represents.
    '''
    def __init__(self, length):
        self._length = length
        
    def __len__(self):
        return self._length
    
    def _generate_splice(self, slice_ind):
        '''
        Creates a splice size version of the ZeroList
        '''
        step_size = slice_ind.step if slice_ind.step else 1
        # Check for each of the four possible scenarios
        if slice_ind.start != None:
            if slice_ind.stop != None:
                newListLen = ((get_non_negative_index(slice_ind.stop, self._length) - 
                               get_non_negative_index(slice_ind.start, self._length)) / step_size)
            else:
                newListLen = ((self._length - 
                               get_non_negative_index(slice_ind.start, self._length)) / step_size)
        else:
            if slice_ind.stop != None:
                newListLen = ((get_non_negative_index(slice_ind.stop, self._length)) / step_size)
            else:
                newListLen = (self._length / step_size)
                
        return ZeroList(newListLen)
        
    def __getitem__(self, index):
        # Check for slices
        if isinstance(index, slice):
            return self._generate_splice(index)
                
        index = get_non_negative_index(index, self._length)
        if index >= self._length:
            raise IndexError(index)
        return 0
    
    def __iter__(self):
        return ListIter(self)
