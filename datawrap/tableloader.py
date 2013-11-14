import xlrd
import re
import csv
import os
from StringIO import StringIO

# Used throughout -- never changed
XLSX_EXT_REGEX = re.compile(r'(\.xlsx)\s*$')
XLS_EXT_REGEX = re.compile(r'(\.xls)\s*$')
CSV_EXT_REGEX = re.compile(r'(\.csv)\s*$')

def read(file_name, file_contents=None):
    '''
    Loads an arbitrary file type (xlsx, xls, or csv like) and returns
    a list of 2D tables. For csv files this will be a list of one table,
    but excel formats can have many tables/worksheets.
    
    Args:
        file_name: The name of the local file, or the holder for the 
            extension type when the file_contents are supplied.
        file_contents: The file-like object holding contents of file_name.
            If left as None, then file_name is directly loaded.
    '''
    if re.search(XLSX_EXT_REGEX, file_name):
        return get_data_xlsx(file_name, file_contents=file_contents)
    elif re.search(XLS_EXT_REGEX, file_name):
        return get_data_xls(file_name, file_contents=file_contents)
    elif re.search(CSV_EXT_REGEX, file_name):
        return get_data_csv(file_name, file_contents=file_contents)
    else:
        try:
            return get_data_csv(file_name, file_contents=file_contents)
        except:
            raise ValueError("Unable to load file '"+file_name+"' as csv")
        
def get_data_xlsx(file_name, file_contents=None):
    '''
    Loads the new excel format files. Old format files will automatically
    get loaded as well.
    
    Args:
        file_name: The name of the local file, or the holder for the 
            extension type when the file_contents are supplied.
        file_contents: The file-like object holding contents of file_name.
            If left as None, then file_name is directly loaded.
    '''
    return get_data_xls(file_name, file_contents)

def get_data_xls(file_name, file_contents=None):
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
            A list of sheets; each sheet is a dict containing
            { sheet_name: unicode string naming that sheet,
              sheet_data: 2-D table holding the converted cells of that sheet }
        '''   
        book      = xlrd.open_workbook(file_name, file_contents=file_contents)
        sheets    = []
        formatter = lambda(t, v): format_excel_val(book, t, v, False)
        
        for sheet_name in book.sheet_names():
            raw_sheet = book.sheet_by_name(sheet_name)
            data      = []
            for row in range(raw_sheet.nrows):
                (types, values) = (raw_sheet.row_types(row), raw_sheet.row_values(row))
                data.append(map(formatter, zip(types, values)))
            sheets.append({'sheet_name': sheet_name, 'sheet_data': data})
        return sheets
    
    data = []
    
    for ws in xlrd_xsl_to_array(file_name, file_contents):
        data.append(ws['sheet_data'])
    return data

def get_data_csv(file_name, load_as_unicode=True, file_contents=None):
    '''
    Gets good old csv data from a file.
    
    Args:
        file_name: The name of the local file, or the holder for the
            extension type when the file_contents are supplied.
        load_as_unicode: Loads the file as a unicode object.
        file_contents: The file-like object holding contents of file_name.
            If left as None, then file_name is directly loaded.
    '''
    table = []
    
    def process_csv(csv_file):
        for line in csv_file:
            if load_as_unicode:
                table.append([unicode(cell, 'utf-8') for cell in line])
            else:
                table.append(line)
    
    if file_contents:
        csv_file = StringIO(file_contents)
        process_csv(csv.reader(csv_file, dialect=csv.excel))
    else:
        with open(file_name, "rb") as csv_file:
            process_csv(csv.reader(csv_file, dialect=csv.excel))
    
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
    