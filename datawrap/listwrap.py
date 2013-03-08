import collections

'''
Helper function for checking non-string item length
'''
def nonStrLen(item):
    if isinstance(item, basestring):
        raise TypeError()
    return len(item)

'''
Helper function for determining if object has __len__ defined
'''
def hasLen(item):
    try:
        len(item)
        return True
    except:
        return False

'''
Helper function for checking non-string item length.
Returns None on failure instead of throwing a TypeError.
'''
def nonStrLenNoThrow(item):
    try:
        return nonStrLen(item)
    except TypeError:
        return 0
    
'''
Converts negative indices to positive ones
'''
def getNonNegativeIndex(index, length):
    while index < 0:
        # Catch the 0 length case
        if length > 0:
            index += length
        else:
            index = 0
    return index

'''
Checks if a particular key is a slice or DimensionRange
'''
def isSliceOrDimRange(key):
    return isinstance(key, (slice, DimensionRange))

'''
Checks if a particular key is a slice, DimensionRange or
list of those types
'''
def isSliceOrDimRangeRequest(key, depth=0):
    # Slice, DimensionRange, or list of those elements
    return (isSliceOrDimRange(key) or
            # Don't check more than the first depth
            (depth == 0 and nonStrLenNoThrow(key) > 0 and 
             all(isSliceOrDimRangeRequest(subkey, depth+1) for subkey in key)))

'''
Converts negative indicies to positive ones and
indicies above length to length or length-1 depending
on lengthAllowed.
'''
def getRestrictedIndex(index, length, lengthIndexAllowed=True):
    if index and index >= length:
        index = length if lengthIndexAllowed else length-1
    return getNonNegativeIndex(index, length)

'''
Converts various size tuples or slices representing 
data ranges returns a new slice with all non-negative 
(or None) values.
'''
def getTrueSlice(dims, dataLen):
    rangeLen = nonStrLenNoThrow(dims)
    
    # Get the range qualifier for length
    if isinstance(dims, slice):
        start = getRestrictedIndex(int(dims.start), dataLen) if dims.start != None else dims.start
        stop = getRestrictedIndex(int(dims.stop), dataLen) if dims.stop != None else dims.stop
        step = getRestrictedIndex(int(dims.step), dataLen) if dims.step != None else dims.step
    elif rangeLen > 3:
        raise AttributeError(str(dims)+' length is > 3')
    elif rangeLen == 3:
        start = getRestrictedIndex(int(dims[0]), dataLen) if dims[0] != None else dims[0]
        stop = getRestrictedIndex(int(dims[1]), dataLen) if dims[1] != None else dims[1]
        step = getRestrictedIndex(int(dims[2]), dataLen) if dims[2] != None else dims[2]
    elif rangeLen == 2:
        start = getRestrictedIndex(int(dims[0]), dataLen) if dims[0] != None else dims[0]
        stop = getRestrictedIndex(int(dims[1]), dataLen) if dims[1] != None else dims[1]
        step = None
    elif rangeLen == 1:
        start = getRestrictedIndex(int(dims[0]), dataLen) if dims[0] != None else dims[0]
        stop = getRestrictedIndex(int(dims[0]), dataLen)+1 if dims[0] != None else dims[0]
        step = None
    elif dims != None:
        start = getRestrictedIndex(int(dims), dataLen) if dims != None else dims
        stop = getRestrictedIndex(int(dims), dataLen)+1 if dims != None else dims
        step = None
    else:
        start = None
        stop = None
        step = None
        
    return slice(start, stop, step)

'''
Defines an ordered set of dimensions. These can be used to scope
and select subsets of data. These act much the same as slices
in standard list operators but can be combined easily and have
an application for a depth of dimensions.

@param orderedRanges The arguments which provide the ordered 
                     restrictions at each sub-dimension. 
@author Matt Seal
'''
class DimensionRange(collections.MutableMapping):
    def __init__(self, *orderedRanges):
        self.orderedRanges = []
        for rangeRestriction in orderedRanges:
            self.addRange(rangeRestriction)
            
    '''
    Creates a new DimensionRange object with other
    concatenated to the end of the range specifications.
    '''
    def __add__(self, other):
        if isinstance(other, DimensionRange):
            return DimensionRange(self, other)
        else:
            raise ValueError(str(other)+" is not of type DimensionRange")
    
    def __iadd__(self, other):
        self.__init__(self + other)
        
    '''
    Same as __add__(self, other)
    '''
    def getCombinedDimensionRange(self, other):
        return self + other
            
    '''
    Returns a slice representing the dimension range
    restrictions applied to a list of length dataLen.
    
    If addSlices contains additional slice requirements,
    they are processed in the order they are given.
    '''
    def sliceOnLength(self, dataLen, *addSlices):
        if len(self.orderedRanges) + len(addSlices) == 0:
            return slice(None,None,None)
        ranges = self.orderedRanges
        if len(addSlices) > 0:
            ranges = ranges + DimensionRange(*addSlices).orderedRanges
        return self._combineListsOfRangesOnLength(dataLen, *ranges)
        
    '''
    Combines a first range with a second range, where the second
    range is considered within the scope of the first.
    '''
    def _combineRangesOnLength(self, dataLen, first, second):
        first = getTrueSlice(first, dataLen)
        second = getTrueSlice(second, dataLen)
        finalStart, finalStep, finalStop = (None, None, None)
        
        # Get our start
        if first.start == None and second.start == None:
            finalStart = None
        else:
            finalStart = (first.start if first.start else 0)+(second.start if second.start else 0)
            
        # Get our stop
        if second.stop == None:
            finalStop = first.stop
        elif first.stop == None:
            finalStop = (first.start if first.start else 0) + second.stop
        else:
            finalStop = min(first.stop, (first.start if first.start else 0) + second.stop)
            
        # Get our step
        if first.step == None and second.step == None:
            finalStep = None
        else:
            finalStep = (first.step if first.step else 1)*(second.step if second.step else 1)
            
        # If we have a start above our stop, set them to be equal
        if finalStart > finalStop:
            finalStart = finalStop
        
        return slice(finalStart, finalStop, finalStep)
        
    '''
    Combines an arbitrary length list of ranges into a single slice
    '''
    def _combineListsOfRangesOnLength(self, dataLen, first, *rangelist):
        currentrange = first
        for nextrange in rangelist:
            currentrange = self._combineRangesOnLength(dataLen, currentrange, nextrange)
        return currentrange
        
    def __getitem__(self, index):
        return self.orderedRanges[index]
    
    def _slicify(self, rangeRestriction):
        if isinstance(rangeRestriction, slice):
            return rangeRestriction
        elif nonStrLenNoThrow(rangeRestriction) == 0:
            return slice(rangeRestriction, rangeRestriction+1, None)
        elif len(rangeRestriction) > 0:
            return slice(*rangeRestriction)
        else:
            return slice(None, None, None)
        
    def __str__(self):
        return "DimensionRange" + self.orderedRanges.__str__()
    
    def __repr__(self):
        return "DimensionRange" + self.orderedRanges.__repr__()
    
    def addRange(self, rangeRestriction):
        # Check for nested ranges
        if isinstance(rangeRestriction, DimensionRange):
            for rangeRestriction in rangeRestriction.orderedRanges:
                self.addRange(rangeRestriction)
        else:
            slicedRange = self._slicify(rangeRestriction)
            # If the slice is a pass all, don't bother appending
            if (slicedRange.start != None or
                slicedRange.stop != None or
                slicedRange.step != None):
                self.orderedRanges.append(slicedRange)
    
    def __setitem__(self, index, rangeRestriction):
        self.orderedRanges[index] = self._slicify(rangeRestriction)
        
    def __len__(self):
        return self.orderedRanges.__len__()
    
    def __delitem__(self, index):
        self.orderedRanges.__delitem__(index)
        
    def __iter__(self):
        return self.orderedRanges.__iter__()

'''
Defines an iterator that relies on an object's __getitem__ 
call to walk through all elements in the data object by 
index. This is useful for wrapper on datasets, which return 
new objects at each index, rather than an underlying 
database's raw information.

@author Matt Seal
'''
class ListIter(object):
    def __init__(self, iterable):
        self.data = iterable
        self._cursor = xrange(len(self.data)).__iter__()
    
    def __iter__(self):
        return self
    
    def next(self):
        return self.data[self._cursor.next()]
    
'''
Wraps list-style data with an iterator and getters 
which only return a subset of the original data.

ListSubset([(1,2,3), (4,5,6)], 2) would effectively
represent the list [2, 5]

ListSubset([(1,2,3), (4,5,6)], (1,3)) => [(1,2), (4,5)]

dataRange of 0 on a non-iterable sublists will
return the non-iterable element as though it were
a tuple of one element.

@param data Fixed length list of arbitrary data
@param dimensionRanges An arbitrary number of dimension
                       restrictions that are combined to
                       form the subset.
@author Matt Seal
'''
class FixedListSubset(collections.Sequence):
    '''
    Assumes data is of fixed length.
    The parameter dataRange can be an Integer or
    a tuple of Integers (or None for full range)
    representing the sub
    '''
    def __init__(self, data, *dimensionRanges):
        # Used later for constructing new FixedLists, this
        # can be replaced by subclasses that want to create
        # a new type of list when returning sublists.
        self.builder = type(self)
        # Check for assignment from another FixedListSubset
        if isinstance(data, FixedListSubset):
            self._dimRanges = self._combineDimensionLists(data._dimRanges, dimensionRanges)
            self._data = data._data
        # Otherwise construct our dimRanges
        else:
            self._data = data
            self._dimRanges = []
            # Convert the dimension inputs into DimensionRange objects
            for dimrange in dimensionRanges:
                self._dimRanges.append(DimensionRange(dimrange))
        dataLen = len(self._data)
        
        if len(self._dimRanges) > 0:
            self.range = self._dimRanges[0].sliceOnLength(dataLen)
        else:
            self.range = slice(None, None, None)
            
        # Get the length of the data
        start = self.range.start if self.range.start != None else 0
        # Check stop
        stop = self.range.stop if self.range.stop != None else dataLen
        # Check step
        step = self.range.step if self.range.step != None else 1
        # Store our length, add step-1 to account for rounding
        self._length = (stop - start + step-1) / step
        
    def __len__(self):
        return self._length
    
    def _combineDimensionLists(self, firstDims, secondDims):
        # Format firstDims and secondDims as lists
        firstDimsLen = nonStrLenNoThrow(firstDims)
        if not hasLen(firstDims) or isSliceOrDimRange(firstDims):
            firstDims = [firstDims]
            firstDimsLen = 1
        secondDimsLen = nonStrLenNoThrow(secondDims)
        if not hasLen(firstDims) or isSliceOrDimRange(secondDims):
            secondDims = [secondDims]
            secondDimsLen = 1
        
        # Our new list of dimension ranges
        constructedDims = []
        
        # Rebuild the dimensions list for each dimension
        for i in xrange(max(firstDimsLen, secondDimsLen)):
            updatedDims = None
            if i < firstDimsLen:
                if i < secondDimsLen:
                    updatedDims = DimensionRange(firstDims[i]) + DimensionRange(secondDims[i])
                else:
                    updatedDims = DimensionRange(firstDims[i])
            elif i < secondDimsLen:
                updatedDims = DimensionRange(secondDims[i])
            else:
                # Impossible scenario
                # So just stop if this happens somehow
                break
            constructedDims.append(updatedDims)
            
        return constructedDims
    
    '''
    Helper method for determining how many single
    index entries there are in a particular multi-index
    '''
    def _getSingleDepth(self, multiIndex):
        singleDepth = 0
        for subind in multiIndex:
            if isSliceOrDimRange(subind):
                break
            singleDepth += 1
        return singleDepth
    
    '''
    Helper function which implements multi index requests
    for __getitem__
    '''
    def _getSliceRequestData(self, index):
        # Do a check on list indices for early error detection
        if not isSliceOrDimRange(index):
            singleDepth = self._getSingleDepth(index)
            # Single value indices for first singleDepth values
            if singleDepth > 0:
                # We have integer request first
                subindicies = index[:singleDepth]
                sublist = self
                # Use the other side of __getitem__ to grab subindices
                for sind in subindicies:
                    sublist = sublist[sind]
                # If we still have some index requests left or dimension
                # restrictions, then return a FixedListSubset
                if singleDepth < len(index) or isinstance(sublist, FixedListSubset):
                    newDimRanges = self._combineDimensionLists(self._dimRanges, index)
                    return self.builder(sublist, *newDimRanges[singleDepth:])
                # Otherwise our sublist is actually an element of the
                # original data, so just return it
                else:
                    return sublist
        newDimRanges = self._combineDimensionLists(self._dimRanges, index)
        return self.builder(self._data, *newDimRanges)
    
    '''
    Helper function which implements single index requests
    for __getitem__
    '''
    def _getSingleIndexRequest(self, index):
        adjustedIndex = index
        # Multiply by step length
        if self.range.step:
            step = self.range.step
            adjustedIndex *= self.range.step
        else:
            step = 1
            
        # Adjust for negative indicies
        adjustedIndex = getNonNegativeIndex(adjustedIndex, self._length)
        # Push forward by start length
        if self.range.start != None:
            adjustedIndex += self.range.start
        # Push forward by start length
        stopIndex = self.range.stop if self.range.stop != None else self._length*step
        if adjustedIndex > stopIndex:
            raise IndexError(index)
        elem = self._data[adjustedIndex]
        # Check if we have further dimension requirements
        # NOTE: if we're given dimensions for non-dimensional data, 
        # this will blow up with an IndexError -- user should
        # not define this dimension with any restrictions
        if len(self._dimRanges) > 1:
            if not hasLen(elem):
                # We throw an IndexError instead of an AttributeError
                # because if can be caused by either sublist requests
                # or a bad constructor, and it's usually the former.
                raise IndexError("Element restricted by DimensionRanges "+
                                 str(self._dimRanges[1:])+" is not subscriptable: "+
                                 "Dimension cannot be applied to elements with no len()")
            return self.builder(elem, *self._dimRanges[1:])
        else:
            return elem
        
    '''
    Handles an arbitrary number of dimensional definitions as
    well as the standard index requests. This getter can be
    treated as a list and will return the correct object or
    object wrapper for a particular index request.
    '''
    def __getitem__(self, index):
        # Check if we have a list of dimensions or a slice request
        if nonStrLenNoThrow(index) > 0 or isSliceOrDimRange(index):
            return self._getSliceRequestData(index)
        # Do a normal get request on an index
        else:
            return self._getSingleIndexRequest(index)
    
    '''
    Default iterator doesn't work
    '''
    def __iter__(self):
        return ListIter(self)
    
    
    '''
    This can be expensive for high dimension lists.
    '''
    def __str__(self):
        if self._length <= 100:
            return str(self.compressRangesToLists())
        else:
            listString = str(self[:100].compressRangesToLists())
            return listString[:-1] + ", ... ]"
        
    '''
    This can be expensive for high dimension lists.
    '''
    def __repr__(self):
        return repr(self.compressRangesToLists())
    
    '''
    Converts the internal dimension ranges on lists into
    list of the restricted size. Thus all dimension rules
    are applied to all dimensions of the list wrapper
    and returned as a list (of lists).
    '''
    def compressRangesToLists(self):
        clist = []
        for elem in self:
            if isinstance(elem, FixedListSubset):
                clist.append(elem.compressRangesToLists())
            else:
                clist.append(elem)
        return clist
    
    '''
    Acts much like compressRangesToLists except it also
    performs a deepcopy on the underlying data. Thus the
    return value is a true copy of original data.
    ''' 
    def deepCopyAsList(self, memo=None):
        import copy
        if memo == None:
            memo = {}
        clist = []
        for elem in self:
            if isinstance(elem, FixedListSubset):
                clist.append(elem.deepCopyAsList(memo))
            else:
                clist.append(copy.deepcopy(elem, memo))
        return clist
    
    def __copy__(self):
        return self.builder(self.compressRangesToLists())
    
    def __deepcopy__(self, memo):
        return self.builder(self.deepCopyAsList(memo))
    
'''
A constant list of zeros with fixed memory footprint. 
This is useful for passing a placeholder instead of
a real list, especially when the length could be very
large.

@param length The number of 'zeros' this list represents
@author Matt Seal
'''
class ZeroList(collections.Sequence):
    def __init__(self, length):
        self._length = length
        
    def __len__(self):
        return self._length
    
    '''
    Creates a splice size version of the ZeroList
    '''
    def _generateSplice(self, sliceInd):
        stepsize = sliceInd.step if sliceInd.step else 1
        # Check for each of the four possible scenarios
        if sliceInd.start != None:
            if sliceInd.stop != None:
                newListLen = ((getNonNegativeIndex(sliceInd.stop, self._length) - 
                               getNonNegativeIndex(sliceInd.start, self._length)) / stepsize)
            else:
                newListLen = ((self._length - 
                               getNonNegativeIndex(sliceInd.start, self._length)) / stepsize)
        else:
            if sliceInd.stop != None:
                newListLen = ((getNonNegativeIndex(sliceInd.stop, self._length)) / stepsize)
            else:
                newListLen = (self._length / stepsize)
                
        return ZeroList(newListLen)
        
    def __getitem__(self, index):
        # Check for slices
        if isinstance(index, slice):
            return self._generateSplice(index)
                
        index = getNonNegativeIndex(index, self._length)
        if index >= self._length:
            raise IndexError(index)
        return 0
    
    def __iter__(self):
        return ListIter(self)
