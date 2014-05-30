# This import fixes sys.path issues
import parentpath

from datawrap import tableloader
import csv
import unittest
import os
from os.path import dirname

def compare_to_csv(file_name, check_table, row_slice=None):
    '''
    Helper function which compares the loaded data against another csv.
    '''
    with open(file_name,"r") as mfile:
        # Squash iterators and generate full tables
        master = [line for line in csv.reader(mfile)]
        check = [line for line in check_table]

        if row_slice:
            master = master[row_slice]
            check = check[row_slice]

        if len(master) != len(check):
            return False
        for master_line, check_line in zip(master, check):
            if len(master_line) != len(check_line):
                return False
            for master_elem, check_elem in zip(master_line, check_line):
                if master_elem != check_elem:
                    try:
                        if isinstance(check_elem, int):
                            master_elem = int(float(master_elem))
                        else:
                            # XLS & XLSX modules add extra digits for calculated cells.
                            check_elem = round(float(check_elem), 8)
                            master_elem = round(float(master_elem), 8)
                        if master_elem != check_elem:
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
    
    def test_csv(self, data=None, on_demand=False):
        if data == None:
            data = tableloader.read(self.csv_test, on_demand=on_demand)
        self.assertTrue(compare_to_csv(self.csv_master, data[0]))

    def test_on_demand_csv(self, data=None):
        self.test_csv(data, True)
    
    def test_content_csv(self, on_demand=False):
        fname = self.csv_test
        with open(fname, "rb") as dfile:
            name, ext = os.path.splitext(fname)
            self.test_csv(tableloader.read(ext, dfile.read()), on_demand)

    def test_on_demand_content_csv(self):
        self.test_content_csv(True)
       
    def test_xls(self, data=None, on_demand=False):
        if data == None:
            data = tableloader.read(self.xls_test, on_demand=on_demand)
        self.assertTrue(compare_to_csv(self.excel_master1, data[0]))
        self.assertTrue(compare_to_csv(self.excel_master2, data[1]))
        self.assertTrue(compare_to_csv(self.excel_master3, data[2]))
        self.assertEqual(data[2].name, '3rd Sheet')

    def test_on_demand_xls(self, data=None):
        self.test_xls(data, True)
        
    def test_content_xls(self, on_demand=False):
        fname = self.xls_test
        with open(fname, "rb") as dfile:
            name, ext = os.path.splitext(fname)
            self.test_xls(tableloader.read(ext, dfile.read()), on_demand)

    def test_on_demand_content_xls(self):
        self.test_content_xls(True)
        
    def test_xlsx(self, data=None, on_demand=False):
        if data == None:
            data = tableloader.read(self.xlsx_test, on_demand=on_demand)
        self.assertTrue(compare_to_csv(self.excel_master1, data[0]))
        self.assertTrue(compare_to_csv(self.excel_master2, data[1]))
        self.assertTrue(compare_to_csv(self.excel_master3, data[2]))

    def test_on_demand_xlsx(self, data=None):
        self.test_xlsx(data, True)
        
    def test_content_xlsx(self, on_demand=False):
        fname = self.xlsx_test
        with open(fname, "rb") as dfile:
            name, ext = os.path.splitext(fname)
            self.test_xlsx(tableloader.read(ext, dfile.read()), on_demand)

    def test_on_demand_content_xlsx(self):
        self.test_content_xlsx(True)
        
    def test_sheet_yielder_slicing(self):
        data = tableloader.read(self.xls_test)
        self.assertTrue(compare_to_csv(self.excel_master1, data[0], slice(1,None)))
        data = tableloader.read(self.xls_test, on_demand=True)
        self.assertTrue(compare_to_csv(self.excel_master1, data[0], slice(None,3)))

    def test_function_xls(self, data=None, on_demand=False):
        if data == None:
            data = tableloader.read(self.xls_formula_test, on_demand=on_demand)
        self.assertTrue(compare_to_csv(self.formula_master, data[0]))

    def test_on_demand_function_xls(self, data=None):
        self.test_function_xls(data, True)
        
    def test_content_function_xls(self, on_demand=False):
        fname = self.xls_formula_test
        with open(fname, "rb") as dfile:
            name, ext = os.path.splitext(fname)
            self.test_function_xls(tableloader.read(ext, dfile.read()), on_demand)

    def test_on_demand_content_function_xls(self):
        self.test_content_function_xls(True)
       
    def test_function_xlsx(self, data=None, on_demand=False):
        if data == None:
            data = tableloader.read(self.xlsx_formula_test, on_demand=on_demand)
        self.assertTrue(compare_to_csv(self.formula_master, data[0]))

    def test_on_demand_function_xlsx(self, data=None):
        self.test_function_xlsx(data, True)
        
    def test_content_function_xlsx(self, on_demand=False):
        fname = self.xlsx_formula_test
        with open(fname, "rb") as dfile:
            name, ext = os.path.splitext(fname)
            self.test_function_xlsx(tableloader.read(ext, dfile.read()), on_demand)

    def test_on_demand_content_function_xlsx(self):
        self.test_content_function_xlsx(True)

if __name__ == '__main__': 
    unittest.main()
