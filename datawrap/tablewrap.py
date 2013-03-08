import sys
import collections
from listwrap import ListIter

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
Generates a Transpose Wrapper of a 2D table. The original
table is not copied. Accesses to rows map to columns and
columns to rows.

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
            #TODO splices
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
        #TODO splices
        return self.TableTransposeRow(self, index)
    
    def __iter__(self):
        return ListIter(self)
    