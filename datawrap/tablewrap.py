import sys
import collections
from listwrap import ListIter, MutableListSubset

'''
Updates a table so that all rows are the same length by
filling smaller rows with 'None' objects up to the length
of the largest row.

@author Matt Seal
'''
def squarifyTable(table):
    maxLength = 0
    minLength = sys.maxint
    for row in table:
        rowLen = len(row)
        if rowLen > maxLength:
            maxLength = rowLen
        if rowLen < minLength:
            minLength = rowLen
    if maxLength != minLength:
        for row in table:
            rowLen = len(row)
            if rowLen < maxLength:
                row.extend([None]*(maxLength-rowLen))

'''
Wraps a 2D table with a basic object. This difference between
this object and the underlying list of lists is that this table
slices and indexes by reference. Any changes to a slice of the
table also changes the original table.

@author Matt Seal
'''
class Table(collections.Sequence):
    '''
    @param table A 2D table, usually a list of lists.
    @param verify Flag for verifying that the table is complete 
                  (all rows have same width).
    '''
    def __init__(self, table, verify=True):
        self._table = table
        self._length = len(table) if table else 0
        self._width = len(table[0]) if table and table[0] else 0
        if verify:
            for row in self._table:
                if len(row) != self._width:
                    raise ValueError("Non-rectangular table passed to TableTranpose")
                
    '''
    Gets a transpose reference to this table.
    '''
    def transpose(self):
        return TableTranpose(self, False)
        
    def __len__(self):
        return self._length
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return MutableListSubset(self, index)
        else:
            return MutableListSubset(self._table[index])
    
    def __iter__(self):
        return ListIter(self)

'''
Generates a Transpose Wrapper of a 2D table. The original
table is not copied. Accesses to rows map to columns and
columns to rows.

NOTE: all slice requests are by reference instead of by copy!
This means changes to slice elements change the transpose
table and consequentially the original table. This is done
for performance reasons, as copying columns is expensive.

@param table 2D table of data (must be rectangular)
@author Matt Seal
'''
class TableTranpose(collections.Sequence):
    '''
    Represents a Row of the transpose which is equivalent
    to a Column of the original table.
    '''
    class TableTransposeRow(collections.MutableSequence):
        def __init__(self, tableTranspose, rowIndex):
            self._transpose = tableTranspose
            self._rowIndex = rowIndex
            
        def __len__(self):
            return self._transpose._width
        
        def __getitem__(self, index):
            if isinstance(index, slice):
                return MutableListSubset(self, index)
            else:
                return self._transpose._table[index][self._rowIndex]
        
        def __setitem__(self, index, value):
            self._transpose._table[index][self._rowIndex] = value
            
        def insert(self, index, value):
            raise NotImplementedError("Cannot insert into a Table Transpose")
        
        def __delitem__(self, index):
            raise NotImplementedError("Cannot delete from a Table Transpose")
        
        def __iter__(self):
            return ListIter(self)
    
    def __init__(self, table, verify=True):
        self._table = table
        self._width = len(table) if table else 0
        self._length = len(table[0]) if table and table[0] else 0
        if verify:
            for row in self._table:
                if len(row) != self._length:
                    raise ValueError("Non-rectangular table passed to TableTranpose")
        
    def __len__(self):
        return self._length
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return MutableListSubset(self, index)
        else:
            return self.TableTransposeRow(self, index)
    
    def __iter__(self):
        return ListIter(self)
    