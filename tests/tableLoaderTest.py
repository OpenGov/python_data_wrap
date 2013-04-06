# This import triggers the __init__.py code regardless of how this file is called
import tests
from datawrap import tableloader
import hashlib
import csv
import unittest
import os
from os.path import dirname

'''
Helper function which compares the loaded data against
another csv

@author Joe Maguire
@author Matt Seal
'''
def compareToCSV(filename, array):
    with open(filename,"r") as mfile:
        master = csv.reader(mfile)
        for i, line in enumerate(master):
            for j, word in enumerate(line):
                if(word != array[i][j]):
                    try: # Check if same number (0.00 vs 0)
                        # XLS & XLSX modules add extra digits for calculated cells.
                        if round(float(word),8) != round(float(array[i][j]),8):  
                            #print "Row:",i,"Column:",j,"Master:",word,"Test:",array[i][j],"END"
                            return False
                    except:
                        return False
   
    return True

'''
Tests the capabilities to load tables from csv, xls and xlsx
formats.

@author Joe Maguire
@author Matt Seal
'''
class TableLoaderTest(unittest.TestCase):
    def setUp(self):
        self.datadir = os.path.join(dirname(__file__), 'tableLoadData')
        self.csv_test = os.path.join(self.datadir, 'raw', 'csv_test.csv')
        self.csv_master = os.path.join(self.datadir, 'master', 'csv_master.csv')
        
        self.xls_test = os.path.join(self.datadir, 'raw', 'xls_test.xls')
        self.xlsx_test = os.path.join(self.datadir, 'raw', 'xlsx_test.xlsx')
        
        self.xls_formula_test = os.path.join(self.datadir, 'raw', 'formulas_xls.xls')
        self.xlsx_formula_test = os.path.join(self.datadir, 'raw', 'formulas_xlsx.xlsx')
        
        self.formula_master = os.path.join(self.datadir, 'master', 'formulas_master.csv')
        self.excel_master1 = os.path.join(self.datadir, 'master', 'excel_sheet1_master.csv')
        self.excel_master2 = os.path.join(self.datadir, 'master', 'excel_sheet2_master.csv')
        self.excel_master3 = os.path.join(self.datadir, 'master', 'excel_sheet3_master.csv')
    
    def testCSV(self):
        data = tableloader.read(self.csv_test)
        self.assertTrue(compareToCSV(self.csv_master,data[0]))
    
    def testContentCSV(self):
        fname = self.csv_test
        with open(fname, "r") as dfile:
            name, ext = os.path.splitext(fname)
            data = tableloader.read(ext, dfile.read())
            self.assertTrue(compareToCSV(self.csv_master, data[0]))
       
    def testXLS(self):
        data = tableloader.read(self.xls_test)      
        self.assertTrue(compareToCSV(self.excel_master1,data[0]))
        self.assertTrue(compareToCSV(self.excel_master2,data[1]))
        self.assertTrue(compareToCSV(self.excel_master3,data[2]))
        
    def testContentXLS(self):
        fname = self.xls_test
        with open(fname, "r") as dfile:
            name, ext = os.path.splitext(fname)
            data = tableloader.read(ext, dfile.read())
            self.assertTrue(compareToCSV(self.excel_master1,data[0]))
            self.assertTrue(compareToCSV(self.excel_master2,data[1]))
            self.assertTrue(compareToCSV(self.excel_master3,data[2]))
        
    def testXLSX(self):
        data = tableloader.read(self.xlsx_test) 
        self.assertTrue(compareToCSV(self.excel_master1,data[0]))
        self.assertTrue(compareToCSV(self.excel_master2,data[1]))
        self.assertTrue(compareToCSV(self.excel_master3,data[2]))
        
    def testContentXLXS(self):
        fname = self.xlsx_test
        with open(fname, "r") as dfile:
            name, ext = os.path.splitext(fname)
            data = tableloader.read(ext, dfile.read())
            self.assertTrue(compareToCSV(self.excel_master1,data[0]))
            self.assertTrue(compareToCSV(self.excel_master2,data[1]))
            self.assertTrue(compareToCSV(self.excel_master3,data[2]))
        
    def testFunctionsXLS(self):
        data = tableloader.read(self.xls_formula_test)
        self.assertTrue(compareToCSV(self.formula_master,data[0]))
        
    def testContentFunctionsXLS(self):
        fname = self.xls_formula_test
        with open(fname, "r") as dfile:
            name, ext = os.path.splitext(fname)
            data = tableloader.read(ext, dfile.read())
            self.assertTrue(compareToCSV(self.formula_master,data[0]))
       
    def testFunctionsXLSX(self):
        data = tableloader.read(self.xlsx_formula_test)
        self.assertTrue(compareToCSV(self.formula_master,data[0]))
        
    def testContentFunctionsXLSX(self):
        fname = self.xlsx_formula_test
        with open(fname, "r") as dfile:
            name, ext = os.path.splitext(fname)
            data = tableloader.read(ext, dfile.read())
            self.assertTrue(compareToCSV(self.formula_master,data[0]))

if __name__ == '__main__': 
    unittest.main()
