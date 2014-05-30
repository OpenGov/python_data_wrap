import xlrd
import re
import csv
import os
from StringIO import StringIO

# Used throughout -- never changed
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
    '''
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
            raise ValueError("Unable to load file '"+file_name+"' as csv")
        
def get_data_xlsx(file_name, file_contents=None, on_demand=False):
    '''
    Loads the new excel format files. Old format files will automatically get loaded as well.

    Args:
        file_name: The name of the local file, or the holder for the 
            extension type when the file_contents are supplied.
        file_contents: The file-like object holding contents of file_name.
            If left as None, then file_name is directly loaded.
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
            return
            
        self._instantiate_sheet()
        self.rows = [self._build_row(row) for row in xrange(self.sheet.nrows)]

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

        if isinstance(key, slice):
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

def get_data_xls(file_name, file_contents=None, on_demand=False):
    '''
    Loads the old excel format files. New format files will automatically
    get loaded as well.
    
    Args:
        file_name: The name of the local file, or the holder for the
            extension type when the file_contents are supplied.
        file_contents: The file-like object holding contents of file_name.
            If left as None, then file_name is directly loaded.
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
        ''''Cleans up the incoming excel data'''
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

def get_data_csv(file_name, load_as_unicode=True, file_contents=None, on_demand=False):
    '''
    Gets good old csv data from a file.
    
    Args:
        file_name: The name of the local file, or the holder for the
            extension type when the file_contents are supplied.
        load_as_unicode: Loads the file as a unicode object.
        file_contents: The file-like object holding contents of file_name.
            If left as None, then file_name is directly loaded.
    '''
    def yield_csv(csv_contents, csv_file):
        try:
            for line in csv_contents:
                if load_as_unicode:
                    yield [unicode(cell, 'utf-8') for cell in line]
                else:
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
        csv_file = open(file_name, "rb")
    reader = csv.reader(csv_file, dialect=csv.excel)

    if on_demand:
        table = yield_csv(reader, csv_file)
    else:
        table = process_csv(reader, csv_file)
    
    return [table]

def write(data, file_name):
    '''
    Writes 2D tables to file.
    
    Args:
        data: 2D list of tables/worksheets.
        file_name: Name of the output file (determines type).
    '''
    if re.search(XLSX_EXT_REGEX, file_name):
        return write_xlsx(data, file_name)
    elif re.search(XLS_EXT_REGEX, file_name):
        return write_xls(data, file_name)
    elif re.search(CSV_EXT_REGEX, file_name):
        return write_csv(data, file_name)
    else:
        return write_csv(data, file_name)
      
def write_xlsx(data, file_name):
    '''
    Writes out to new excel format.
    
    Args:
        data: 2D list of tables/worksheets.
        file_name: Name of the output file.
    '''
    raise NotImplementedError("Xlsx writing not implemented")

def write_xls(data, file_name):
    '''
    Writes out to old excel format.
    
    Args:
        data: 2D list of tables/worksheets.
        file_name: Name of the output file.
    '''
    raise NotImplementedError("Xls writing not implemented")
 
def write_csv(data, file_name):
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
            csv_file = csv.writer(date_file)
            for line in sheet:
                csv_file.writerow(line)
    
