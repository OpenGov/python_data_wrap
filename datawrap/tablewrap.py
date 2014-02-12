import sys
import collections
from listwrap import ListIter, MutableListSubset

def squarify_table(table):
    '''
    Updates a table so that all rows are the same length by filling smaller 
    rows with 'None' objects up to the length of the largest row.
    '''
    max_length = 0
    min_length = sys.maxint
    for row in table:
        row_len = len(row)
        if row_len > max_length:
            max_length = row_len
        if row_len < min_length:
            min_length = row_len
    if max_length != min_length:
        for row in table:
            row_len = len(row)
            if row_len < max_length:
                row.extend([None]*(max_length-row_len))

class Table(collections.Sequence):
    '''
    Wraps a 2D table with a basic object. This difference between
    this object and the underlying list of lists is that this table
    slices and indexes by reference. Any changes to a slice of the
    table also changes the original table.

    Args:
        table: 2D table of data (must be rectangular or repair=True).
        verify: Checks the length of the table's rows for consistency.
        repair: Repairs any missing elements by inserting Nones
    '''
    def __init__(self, table, verify=True, repair=False):
        '''
        Args:
            table: A 2D table, usually a list of lists.
            verify: Flag for verifying that the table is complete 
                (all rows have same width).
        '''
        if repair:
            squarify_table(table)

        self._table = table
        self._length = len(table) if table else 0
        self._width = len(table[0]) if table and table[0] else 0

        if verify and not repair:
            for row in self._table:
                if len(row) != self._width:
                    raise ValueError("Non-rectangular table passed to Table")
                
    def transpose(self):
        '''
        Gets a transpose reference to this table.
        '''
        return TableTranspose(self, False, False)
        
    def __len__(self):
        return self._length
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return MutableListSubset(self, index)
        else:
            return MutableListSubset(self._table[index])
    
    def __iter__(self):
        return ListIter(self)

class TableTranspose(collections.Sequence):
    '''
    Generates a Transpose Wrapper of a 2D table. The original
    table is not copied. Accesses to rows map to columns and
    columns to rows.
    
    NOTE: all slice requests are by reference instead of by copy!
    This means changes to slice elements change the transpose
    table and consequentially the original table. This is done
    for performance reasons, as copying columns is expensive.
    
    Args:
        table: 2D table of data (must be rectangular or repair=True).
        verify: Checks the length of the table's rows for consistency.
        repair: Repairs any missing elements by inserting Nones
    '''
    class TableTransposeRow(collections.MutableSequence):
        '''
        Represents a Row of the transpose which is equivalent
        to a Column of the original table.
        '''
        def __init__(self, table_transpose, row_index):
            self._transpose = table_transpose
            self._row_index = row_index
            
        def __len__(self):
            return self._transpose._width
        
        def __getitem__(self, index):
            if isinstance(index, slice):
                return MutableListSubset(self, index)
            else:
                return self._transpose._table[index][self._row_index]
        
        def __setitem__(self, index, value):
            self._transpose._table[index][self._row_index] = value
            
        def insert(self, index, value):
            raise NotImplementedError("Cannot insert into a Table Transpose")
        
        def __delitem__(self, index):
            raise NotImplementedError("Cannot delete from a Table Transpose")
        
        def __iter__(self):
            return ListIter(self)
    
    def __init__(self, table, verify=True, repair=False):
        if repair:
            squarify_table(table)

        self._table = table
        self._width = len(table) if table else 0
        self._length = len(table[0]) if table and table[0] else 0

        if verify and not repair:
            for row in self._table:
                if len(row) != self._length:
                    raise ValueError("Non-rectangular table passed to TableTranspose")
        
    def __len__(self):
        return self._length
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return MutableListSubset(self, index)
        else:
            return self.TableTransposeRow(self, index)
    
    def __iter__(self):
        return ListIter(self)
    