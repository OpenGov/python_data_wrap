# This import fixes sys.path issues
import bootstrap
from datawrap import tableloader
import csv
import unittest
import os
from os.path import dirname

def compare_to_csv(file_name, array):
    '''
    Helper function which compares the loaded data against another csv.
    '''
    with open(file_name,"r") as mfile:
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

class TableLoaderTest(unittest.TestCase):
    '''
    Tests the capabilities to load tables from csv, xls and xlsx
    formats.
    '''
    def setUp(self):
        self.data_dir = os.path.join(dirname(__file__), 'table_load_data')
        self.csv_test = os.path.join(self.data_dir, 'raw', 'csv_test.csv')
        self.csv_master = os.path.join(self.data_dir, 'master', 'csv_master.csv')
        
        self.xls_test = os.path.join(self.data_dir, 'raw', 'xls_test.xls')
        self.xlsx_test = os.path.join(self.data_dir, 'raw', 'xlsx_test.xlsx')
        
        self.xls_formula_test = os.path.join(self.data_dir, 'raw', 'formulas_xls.xls')
        self.xlsx_formula_test = os.path.join(self.data_dir, 'raw', 'formulas_xlsx.xlsx')
        
        self.formula_master = os.path.join(self.data_dir, 'master', 'formulas_master.csv')
        self.excel_master1 = os.path.join(self.data_dir, 'master', 'excel_sheet1_master.csv')
        self.excel_master2 = os.path.join(self.data_dir, 'master', 'excel_sheet2_master.csv')
        self.excel_master3 = os.path.join(self.data_dir, 'master', 'excel_sheet3_master.csv')
    
    def test_csv(self):
        data = tableloader.read(self.csv_test)
        self.assertTrue(compare_to_csv(self.csv_master,data[0]))
    
    def test_content_csv(self):
        fname = self.csv_test
        with open(fname, "rb") as dfile:
            name, ext = os.path.splitext(fname)
            data = tableloader.read(ext, dfile.read())
            self.assertTrue(compare_to_csv(self.csv_master, data[0]))
       
    def test_xls(self):
        data = tableloader.read(self.xls_test)      
        self.assertTrue(compare_to_csv(self.excel_master1,data[0]))
        self.assertTrue(compare_to_csv(self.excel_master2,data[1]))
        self.assertTrue(compare_to_csv(self.excel_master3,data[2]))
        
    def test_content_xls(self):
        fname = self.xls_test
        with open(fname, "rb") as dfile:
            name, ext = os.path.splitext(fname)
            data = tableloader.read(ext, dfile.read())
            self.assertTrue(compare_to_csv(self.excel_master1,data[0]))
            self.assertTrue(compare_to_csv(self.excel_master2,data[1]))
            self.assertTrue(compare_to_csv(self.excel_master3,data[2]))
        
    def test_xlsx(self):
        data = tableloader.read(self.xlsx_test) 
        self.assertTrue(compare_to_csv(self.excel_master1,data[0]))
        self.assertTrue(compare_to_csv(self.excel_master2,data[1]))
        self.assertTrue(compare_to_csv(self.excel_master3,data[2]))
        
    def test_content_xlsx(self):
        fname = self.xlsx_test
        with open(fname, "rb") as dfile:
            name, ext = os.path.splitext(fname)
            data = tableloader.read(ext, dfile.read())
            self.assertTrue(compare_to_csv(self.excel_master1,data[0]))
            self.assertTrue(compare_to_csv(self.excel_master2,data[1]))
            self.assertTrue(compare_to_csv(self.excel_master3,data[2]))
        
    def test_function_xls(self):
        data = tableloader.read(self.xls_formula_test)
        self.assertTrue(compare_to_csv(self.formula_master,data[0]))
        
    def test_content_function_xls(self):
        fname = self.xls_formula_test
        with open(fname, "rb") as dfile:
            name, ext = os.path.splitext(fname)
            data = tableloader.read(ext, dfile.read())
            self.assertTrue(compare_to_csv(self.formula_master,data[0]))
       
    def test_function_xlsx(self):
        data = tableloader.read(self.xlsx_formula_test)
        self.assertTrue(compare_to_csv(self.formula_master,data[0]))
        
    def test_content_function_xlsx(self):
        fname = self.xlsx_formula_test
        with open(fname, "rb") as dfile:
            name, ext = os.path.splitext(fname)
            data = tableloader.read(ext, dfile.read())
            self.assertTrue(compare_to_csv(self.formula_master,data[0]))

if __name__ == '__main__': 
    unittest.main()
