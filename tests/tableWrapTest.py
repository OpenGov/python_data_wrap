# This import triggers the __init__.py code regardless of how this file is called
import tests
from datawrap import tablewrap
import unittest

class TableWrapTest(unittest.TestCase):
    def setUp(self):
        self.table = [[1,2,3,4,5], [6,7,8,9,10], ['a','b','c','d','e']]
        self.transpose = tablewrap.TableTranpose(self.table)

    def testTableTranpose(self):
        self.assertEqual(self.transpose[0][0], self.table[0][0])
        self.assertEqual(self.transpose[4][0], self.table[0][4])
        self.assertEqual(self.transpose[0][2], self.table[2][0])
        self.assertEqual(self.transpose[4][2], self.table[2][4])
        self.assertEqual(self.transpose[-1][-1], self.table[-1][-1])
        self.assertEqual(self.transpose[-2][-3], self.table[-3][-2])
        
        for c,col in enumerate(self.transpose):
            for r,elem in enumerate(col):
                self.assertEqual(elem, self.table[r][c])
                
    def testTableSlice(self):
        # Try copy slice requests
        self.assertEqual(self.transpose[:][0][0], self.table[0][0])
        self.assertEqual(self.transpose[:][4][0], self.table[0][4])
        self.assertEqual(self.transpose[:][0][2], self.table[2][0])
        self.assertEqual(self.transpose[:][4][2], self.table[2][4])
        
        # Make a change
        self.transpose[:][0][2] = 'new'
        self.assertEqual(self.transpose[0][2], 'new')
        self.assertEqual(self.table[2][0], 'new')
        
        # Try some different slices
        tslice = slice(1, None, 2)
        translice = self.transpose[tslice]
        self.assertEqual(len(translice), 2)
        self.assertEqual(len(translice[0]), 3)
        translice[0][0] = 'new2'
        self.assertEqual(translice[0][0], self.table[0][tslice][0])
        self.assertEqual(translice[1][0], self.table[0][tslice][1])
        self.assertEqual(translice[0][2], self.table[2][tslice][0])
        self.assertEqual(translice[1][2], self.table[2][tslice][1])
        
        tslice = slice(None, 1, None)
        translice = self.transpose[tslice]
        self.assertEqual(len(translice), 1)
        self.assertEqual(len(translice[0]), 3)
        translice[0][0] = 'new3'
        self.assertEqual(translice[0][0], self.table[0][tslice][0])
        self.assertEqual(translice[0][2], self.table[2][tslice][0])
    
    def testTableTransposeExceptions(self):
        # Check that valid finds bad tables
        badTable = [[1, 2, 3], ['a', 'b'], [4, 5, 6]]
        self.assertRaises(ValueError, lambda: tablewrap.TableTranpose(badTable))
        
        badTable = [[1], ['a', 'b'], [4, 5, 6]]
        self.assertRaises(ValueError, lambda: tablewrap.TableTranpose(badTable))
        
        badTable = [[1, 2], ['a'], [4]]
        self.assertRaises(ValueError, lambda: tablewrap.TableTranpose(badTable))
        
        badTable = [[1, 2], ['a'], [4]]
        noCheck = tablewrap.TableTranpose(badTable, False)
        # If we don't do validity checks and instead access a bad index...
        self.assertRaises(IndexError, lambda: noCheck[2][1])

if __name__ == '__main__': 
    unittest.main()
