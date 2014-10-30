# This import fixes sys.path issues
import parentpath

import unittest
import os
import copy
import shutil
from os.path import dirname
from datawrap import tableloader

# TODO implement
class DataLoadTest(unittest.TestCase):
    def setUp(self):
        self.dummy_data = [
            [
                [u'Testing', 123, None, u'Testing'],
                [u'Various Lengths'],
            ],
            [
                [u'Testing Page 2', u'Testing'],
                [u'Various Lengths', None, 42, u'Check', None],
            ],
        ]
        self.data_dir = os.path.join(dirname(__file__), 'write_tmp')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def blank_to_none(self, worksheet):
        worksheet = copy.deepcopy(worksheet)
        for row_index, row in enumerate(worksheet):
            for col_index, elem in enumerate(row):
                if elem == '':
                    worksheet[row_index][col_index] = None
        return worksheet

    def numerics_to_string(self, worksheet):
        worksheet = copy.deepcopy(worksheet)
        for row_index, row in enumerate(worksheet):
            for col_index, elem in enumerate(row):
                if isinstance(elem, (int, float, long)):
                    worksheet[row_index][col_index] = unicode(elem)
        return worksheet

    def chop_extra_nones(self, worksheet):
        worksheet = copy.deepcopy(worksheet)
        max_col = 0
        for row in worksheet:
            last_value = 0
            for col_index, elem in enumerate(row):
                if elem is not None:
                    last_value = col_index
            max_col = max(last_value, max_col)

        for row_index, row in enumerate(worksheet):
            if len(row) > max_col + 1:
                worksheet[row_index] = row[:max_col + 1]
        return worksheet

    def missing_fill(self, worksheet):
        worksheet = copy.deepcopy(worksheet)
        max_col = max(len(row) for row in worksheet)
        for row in worksheet:
            if len(row) < max_col:
                row.extend([None]*(max_col - len(row)))
        return worksheet

    def test_csv_write_read(self):
        csv_file_name = os.path.join(self.data_dir, 'test_csv.csv')
        csv_worksheet_file_names = [os.path.join(self.data_dir, 'test_csv_0.csv'), os.path.join(self.data_dir, 'test_csv_1.csv')]

        # Read/Write each sheet individually
        for writer in [tableloader.write_csv, tableloader.write]:
            for sheet in self.dummy_data:
                writer([sheet], csv_file_name)
                written_content = tableloader.read(csv_file_name)[0]
                self.assertListEqual(self.blank_to_none(written_content), self.numerics_to_string(sheet))

        # Write all sheets at once, read each resulting file once
        for writer in [tableloader.write_csv, tableloader.write]:
            writer(self.dummy_data, csv_file_name)
            for sheet, file_name in zip(self.dummy_data, csv_worksheet_file_names):
                written_content = tableloader.read(file_name)[0]
                self.assertListEqual(self.blank_to_none(written_content), self.numerics_to_string(sheet))

    def test_xls_write_read(self):
        xls_file_name = os.path.join(self.data_dir, 'test_csv.xls')

        # Read/Write dummy data
        for writer in [tableloader.write_xls, tableloader.write]:
            writer(self.dummy_data, xls_file_name)
            written_content = tableloader.read(xls_file_name)
            # Check that same number of worksheets were written
            self.assertEqual(len(self.dummy_data), len(written_content))
            for dummy_sheet, written_sheet in zip(self.dummy_data, written_content):
                self.assertListEqual(self.blank_to_none(written_sheet.load()),
                        self.missing_fill(self.chop_extra_nones(dummy_sheet)))

    def test_xlsx_write_read(self):
        xlsx_file_name = os.path.join(self.data_dir, 'test_csv.xlsx')

        # Read/Write dummy data
        for writer in [tableloader.write_xlsx, tableloader.write]:
            # Implement when xlsx writing is finished
            self.assertRaises(NotImplementedError, lambda: writer(self.dummy_data, xlsx_file_name))

if __name__ == "__main__":
    unittest.main()
