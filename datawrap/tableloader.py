import xlrd
import xlwt
import re
import unicodecsv as csv
import os
from external import xmlparse
from StringIO import StringIO

# Used throughout -- never changed
XML_EXT_REGEX = re.compile(r'(\.xml)\s*$')
XLSX_EXT_REGEX = re.compile(r'(\.xlsx)\s*$')
XLS_EXT_REGEX = re.compile(r'(\.xls)\s*$')
CSV_EXT_REGEX = re.compile(r'(\.csv)\s*$')

def read(file_name, file_contents=None, on_demand=False):
    '''
    Loads an arbitrary file type (xlsx, xls, or csv like) and returns
    a list of 2D tables. For csv files this will be a list of one table,
    but excel formats can have many tables/worksheets.

    TODO:
        Add wrapper which can be closed/exited on each file type which cleans
        up the file handler.

    Args:
        file_name: The name of the local file, or the holder for the
            extension type when the file_contents are supplied.
        file_contents: The file-like object holding contents of file_name.
            If left as None, then file_name is directly loaded.
        on_demand: Requests that a yielder be used in place of a full data
            copy.
    '''
    try:
        if re.search(XML_EXT_REGEX, file_name):
            return get_data_excel_xml(file_name, file_contents=file_contents, on_demand=on_demand)
        if re.search(XLSX_EXT_REGEX, file_name):
            return get_data_xlsx(file_name, file_contents=file_contents, on_demand=on_demand)
        elif re.search(XLS_EXT_REGEX, file_name):
            return get_data_xls(file_name, file_contents=file_contents, on_demand=on_demand)
        elif re.search(CSV_EXT_REGEX, file_name):
            return get_data_csv(file_name, file_contents=file_contents, on_demand=on_demand)
        else:
            try:
                return get_data_csv(file_name, file_contents=file_contents, on_demand=on_demand)
            except:
                raise ValueError("Unable to load file '{}' as csv".format(file_name))
    except xlrd.XLRDError, e:
        if "<?xml" in str(e):
            return get_data_excel_xml(file_name, file_contents=file_contents, on_demand=on_demand)
        raise

def get_data_xlsx(file_name, file_contents=None, on_demand=False):
    '''
    Loads the new excel format files. Old format files will automatically get loaded as well.

    Args:
        file_name: The name of the local file, or the holder for the
            extension type when the file_contents are supplied.
        file_contents: The file-like object holding contents of file_name.
            If left as None, then file_name is directly loaded.
        on_demand: Requests that a yielder be used in place of a full data
            copy.
    '''
    return get_data_xls(file_name, file_contents=file_contents, on_demand=on_demand)


class SheetYielder(object):
    '''
    Provides an abstraction which yeilds individual sheets for iterable consumption.
    Unfortunately the sheet abstraction in xlrd doesn't accomodate yield patterns, so
    once a single row is yielded by this generator the entire sheet has been loaded.
    This loading will not happen until the iterator is triggered however, so unused
    sheets will remain unused.
    '''
    def __init__(self, book, sheet_index, row_builder):
        self.book = book
        self.sheet_index = sheet_index
        self.row_builder = row_builder
        self.sheet = None
        self.rows = None  # This is utilized only if load() is invoked

    @property
    def name(self):
        self._instantiate_sheet()
        return self.sheet.name

    def load(self):
        if self.rows is not None:
            return self.rows

        self._instantiate_sheet()
        self.rows = [self._build_row(row) for row in xrange(self.sheet.nrows)]
        return self.rows

    def __iter__(self):
        if self.rows is not None:
            for row in self.rows:
                yield row
            return

        self._instantiate_sheet()
        for i in xrange(self.sheet.nrows):
            yield self[i]

    def __len__(self):
        self._instantiate_sheet()
        return self.sheet.nrows

    def __getitem__(self, key):
        self._instantiate_sheet()

        if self.rows is not None:
            return self.rows.__getitem__(key)
        elif isinstance(key, slice):
            rows = []

            start = 0 if key.start is None else key.start
            stop = len(self) if key.stop is None else key.stop
            step = 1 if key.step is None else key.step

            i = start
            while i < stop:
                rows.append(self._build_row(i))
                i += step

            return rows
        else:
            return self._build_row(key)

    def _instantiate_sheet(self):
        if not self.sheet:
            self.sheet = self.book.sheet_by_index(self.sheet_index)

    def _build_row(self, i):
        return self.row_builder(self.sheet, i)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "SheetYielder({})".format(list(self).__repr__())


def get_data_xls(file_name, file_contents=None, on_demand=False):
    '''
    Loads the old excel format files. New format files will automatically
    get loaded as well.

    Args:
        file_name: The name of the local file, or the holder for the
            extension type when the file_contents are supplied.
        file_contents: The file-like object holding contents of file_name.
            If left as None, then file_name is directly loaded.
        on_demand: Requests that a yielder be used in place of a full data
            copy.
    '''
    def tuple_to_iso_date(tuple_date):
        '''
        Turns a gregorian (year, month, day, hour, minute, nearest_second) into a
        standard YYYY-MM-DDTHH:MM:SS ISO date.  If the date part is all zeros, it's
        assumed to be a time; if the time part is all zeros it's assumed to be a date;
        if all of it is zeros it's taken to be a time, specifically 00:00:00 (midnight).

        Note that datetimes of midnight will come back as date-only strings.  A date
        of month=0 and day=0 is meaningless, so that part of the coercion is safe.
        For more on the hairy nature of Excel date/times see
        http://www.lexicon.net/sjmachin/xlrd.html
        '''
        (y,m,d, hh,mm,ss) = tuple_date
        non_zero = lambda n: n!=0
        date = "%04d-%02d-%02d"  % (y,m,d)    if filter(non_zero, (y,m,d))                else ''
        time = "T%02d:%02d:%02d" % (hh,mm,ss) if filter(non_zero, (hh,mm,ss)) or not date else ''
        return date+time

    def format_excel_val(book, val_type, value, want_tuple_date):
        '''Cleans up the incoming excel data'''
        #  Data val_type Codes:
        #  EMPTY   0
        #  TEXT    1 a Unicode string
        #  NUMBER  2 float
        #  DATE    3 float
        #  BOOLEAN 4 int; 1 means TRUE, 0 means FALSE
        #  ERROR   5
        if   val_type == 2: # TEXT
            if value == int(value): value = int(value)
        elif val_type == 3: # NUMBER
            datetuple = xlrd.xldate_as_tuple(value, book.datemode)
            value = datetuple if want_tuple_date else tuple_to_iso_date(datetuple)
        elif val_type == 5: # ERROR
            value = xlrd.error_text_from_code[value]
        return value

    def xlrd_xsl_to_array(file_name, file_contents=None):
        '''
        Returns:
            A list of 2-D tables holding the converted cells of each sheet
        '''
        book = xlrd.open_workbook(file_name, file_contents=file_contents, on_demand=on_demand)
        formatter = lambda (t, v): format_excel_val(book, t, v, False)
        row_builder = lambda s, r: map(formatter, zip(s.row_types(r), s.row_values(r)))

        data = [SheetYielder(book, index, row_builder) for index in xrange(book.nsheets)]
        if not on_demand:
            for sheet in data:
                sheet.load()
            book.release_resources()
        return data

    return xlrd_xsl_to_array(file_name, file_contents)


class XMLSheetYielder(SheetYielder):
    class XMLSheet(object):
        def __init__(self, name, content):
            self.name = name
            self.content = content

            self.nrows = 0
            self.ncols = 0
            for row_index in range(1, content.GetMaxRow() + 1):
                for column_index in range(1, content.GetMaxColumn() + 1):
                    if self.content.GetCellValue(column_index, row_index + 1, None) is not None:
                        self.ncols = max(self.ncols, column_index)
                        self.nrows = row_index + 1

        def row_values(self, row_index):
            # The xml reader takes index+1 addressing
            for column in range(1, self.ncols + 1):
                yield self.content.GetCellValue(column, row_index + 1, None)

    def _instantiate_sheet(self):
        if not self.sheet:
            content = self.book.GetWorksheets()[self.sheet_index]
            name = content.GetName()
            self.sheet = XMLSheetYielder.XMLSheet(name, content)


def get_data_excel_xml(file_name, file_contents=None, on_demand=False):
    '''
    Loads xml excel format files.

    Args:
        file_name: The name of the local file, or the holder for the
            extension type when the file_contents are supplied.
        file_contents: The file-like object holding contents of file_name.
            If left as None, then file_name is directly loaded.
        on_demand: Requests that a yielder be used in place of a full data
            copy (will be ignored).
    '''
    # NOTE this method is inefficient and uses code that's not of the highest quality
    if file_contents:
        xml_file = StringIO(file_contents)
    else:
        xml_file = file_name
    book = xmlparse.ParseExcelXMLFile(xml_file)
    row_builder = lambda s, r: list(s.row_values(r))
    return [XMLSheetYielder(book, index, row_builder) for index in xrange(len(book))]

def get_data_csv(file_name, encoding='utf-8', file_contents=None, on_demand=False):
    '''
    Gets good old csv data from a file.

    Args:
        file_name: The name of the local file, or the holder for the
            extension type when the file_contents are supplied.
        encoding: Loads the file with the specified cell encoding.
        file_contents: The file-like object holding contents of file_name.
            If left as None, then file_name is directly loaded.
        on_demand: Requests that a yielder be used in place of a full data
            copy.
    '''
    def yield_csv(csv_contents, csv_file):
        try:
            for line in csv_contents:
                yield line
        finally:
            try:
                csv_file.close()
            except:
                pass

    def process_csv(csv_contents, csv_file):
        return [line for line in yield_csv(csv_contents, csv_file)]

    if file_contents:
        csv_file = StringIO(file_contents)
    else:
        # Don't use 'open as' format, as on_demand loads shouldn't close the file early
        csv_file = open(file_name, "rU")
    reader = csv.reader(csv_file, dialect=csv.excel, encoding=encoding)

    if on_demand:
        table = yield_csv(reader, csv_file)
    else:
        table = process_csv(reader, csv_file)

    return [table]

def write(data, file_name, worksheet_names=None):
    '''
    Writes 2D tables to file.

    Args:
        data: 2D list of tables/worksheets.
        file_name: Name of the output file (determines type).
        worksheet_names: A list of worksheet names (optional).
    '''
    if re.search(XML_EXT_REGEX, file_name):
        return write_xml(data, file_name, worksheet_names=worksheet_names)
    elif re.search(XLSX_EXT_REGEX, file_name):
        return write_xlsx(data, file_name, worksheet_names=worksheet_names)
    elif re.search(XLS_EXT_REGEX, file_name):
        return write_xls(data, file_name, worksheet_names=worksheet_names)
    elif re.search(CSV_EXT_REGEX, file_name):
        return write_csv(data, file_name)
    else:
        return write_csv(data, file_name)

def write_xml(data, file_name, worksheet_names=None):
    '''
    Writes out to new excel format.

    Args:
        data: 2D list of tables/worksheets.
        file_name: Name of the output file.
        worksheet_names: A list of worksheet names (optional).
    '''
    raise NotImplementedError("Xml writing not implemented")

def write_xlsx(data, file_name, worksheet_names=None):
    '''
    Writes out to new excel format.

    Args:
        data: 2D list of tables/worksheets.
        file_name: Name of the output file.
        worksheet_names: A list of worksheet names (optional).
    '''
    raise NotImplementedError("Xlsx writing not implemented")

def write_xls(data, file_name, worksheet_names=None):
    '''
    Writes out to old excel format.

    Args:
        data: 2D list of tables/worksheets.
        file_name: Name of the output file.
        worksheet_names: A list of worksheet names (optional).
    '''
    workbook = xlwt.Workbook()
    for sheet_index, sheet_data in enumerate(data):
        if worksheet_names and sheet_index < len(worksheet_names) and worksheet_names[sheet_index]:
            name = worksheet_names[sheet_index]
        else:
            name = 'Worksheet {}'.format(sheet_index)
        sheet = workbook.add_sheet(name)
        for row_index, row in enumerate(sheet_data):
            for col_index, value in enumerate(row):
                sheet.write(row_index, col_index, value)
    workbook.save(file_name)

def write_csv(data, file_name, encoding='utf-8'):
    '''
    Writes out to csv format.

    Args:
        data: 2D list of tables/worksheets.
        file_name: Name of the output file.
    '''
    name_extension = len(data) > 1
    root, ext = os.path.splitext(file_name)

    for i, sheet in enumerate(data):
        fname = file_name if not name_extension else root+"_"+str(i)+ext
        with open(fname, "wb") as date_file:
            csv_file = csv.writer(date_file, encoding=encoding)
            for line in sheet:
                csv_file.writerow(line)

