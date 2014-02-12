# This import fixes sys.path issues
import bootstrap
from datawrap import tablewrap
import unittest

class TableWrapTest(unittest.TestCase):
    '''
    Tests the capability to wrap 2D objects in Tables and transpose them.
    '''
    def setUp(self):
        # self.table doesn't need the tablewrap.Table object to work
        # but this tests both wrappers at once
        self.table = tablewrap.Table([[1,2,3,4,5], [6,7,8,9,10], ['a','b','c','d','e']])
        self.transpose = tablewrap.TableTranspose(self.table)

    def test_table_transpose(self):
        self.assertEqual(self.transpose[0][0], self.table[0][0])
        self.assertEqual(self.transpose[4][0], self.table[0][4])
        self.assertEqual(self.transpose[0][2], self.table[2][0])
        self.assertEqual(self.transpose[4][2], self.table[2][4])
        self.assertEqual(self.transpose[-1][-1], self.table[-1][-1])
        self.assertEqual(self.transpose[-2][-3], self.table[-3][-2])
        
        for c,col in enumerate(self.transpose):
            for r,elem in enumerate(col):
                self.assertEqual(elem, self.table[r][c])

    def test_table_slice(self):
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

    def test_verify(self):
        # Check that valid finds bad tables
        bad_table = [[1, 2, 3], ['a', 'b'], [4, 5, 6]]
        self.assertRaises(ValueError, lambda: tablewrap.Table(bad_table, True, False))
        self.assertRaises(ValueError, lambda: tablewrap.TableTranspose(bad_table, True, False))

        bad_table = [[1], ['a', 'b'], [4, 5, 6]]
        self.assertRaises(ValueError, lambda: tablewrap.Table(bad_table, True, False))
        self.assertRaises(ValueError, lambda: tablewrap.TableTranspose(bad_table, True, False))

        bad_table = [[1, 2], ['a'], [4]]
        self.assertRaises(ValueError, lambda: tablewrap.Table(bad_table, True, False))
        self.assertRaises(ValueError, lambda: tablewrap.TableTranspose(bad_table, True, False))

        bad_table = [[1, 2], ['a'], [4]]
        noCheck = tablewrap.TableTranspose(bad_table, False, False)
        # If we don't do validity checks and instead access a bad index...
        self.assertRaises(IndexError, lambda: noCheck[2][1])

    def test_repair(self):
        # Check that valid finds bad tables
        bad_table = [[1, 2, 3], ['a', 'b'], [4, 5, 6]]
        self.assertRaises(ValueError, lambda: tablewrap.Table(bad_table, True, False))

        # Neither of thse should explode
        table = tablewrap.Table(bad_table, False, True)
        self.assertIsNone(table[1][2])
        self.assertIsNone(bad_table[1][2])

        bad_table = [[1, 2, 3], ['a', 'b'], [4, 5, 6]]
        table = tablewrap.Table(bad_table, True, True)
        self.assertIsNone(table[1][2])
        self.assertIsNone(bad_table[1][2])

        # Check that valid finds bad tables
        bad_table = [[1, 2, 3], ['a', 'b'], [4, 5, 6]]
        self.assertRaises(ValueError, lambda: tablewrap.TableTranspose(bad_table, True, False))

        # Neither of thse should explode
        transpose = tablewrap.TableTranspose(bad_table, False, True)
        self.assertIsNone(transpose[2][1])
        self.assertIsNone(bad_table[1][2])

        bad_table = [[1, 2, 3], ['a', 'b'], [4, 5, 6]]
        transpose = tablewrap.TableTranspose(bad_table, True, True)
        self.assertIsNone(transpose[2][1])
        self.assertIsNone(bad_table[1][2])

if __name__ == '__main__': 
    unittest.main()
