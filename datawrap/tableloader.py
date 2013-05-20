import xlrd
import re
import csv
import os
from StringIO import StringIO

# Used throughout -- never changed
xlsxExtRegex = re.compile(r'(\.xlsx)\s*$')
xlsExtRegex = re.compile(r'(\.xls)\s*$')
csvExtRegex = re.compile(r'(\.csv)\s*$')

def read(filename, filecontents=None):
    '''
    Loads an arbitrary file type (xlsx, xls, or csv like) and returns
    a list of 2D tables. For csv files this will be a list of one table,
    but excel formats can have many tables/worksheets.
    
    Args:
        filename: The name of the local file, or the holder for the 
            extension type when the filecontents are supplied.
        filecontents: The file-like object holding contents of filename.
            If left as None, then filename is directly loaded.
    '''
    if re.search(xlsxExtRegex, filename):
        return getDataXlsx(filename, filecontents=filecontents)
    elif re.search(xlsExtRegex, filename):
        return getDataXls(filename, filecontents=filecontents)
    elif re.search(csvExtRegex, filename):
        return getDataCsv(filename, filecontents=filecontents)
    else:
        try:
            return getDataCsv(filename, filecontents=filecontents)
        except:
            raise ValueError("Unable to load file '"+filename+"' as csv")
        
def getDataXlsx(filename, filecontents=None):
    '''
    Loads the new excel format files. Old format files will automatically
    get loaded as well.
    
    Args:
        filename: The name of the local file, or the holder for the 
            extension type when the filecontents are supplied.
        filecontents: The file-like object holding contents of filename.
            If left as None, then filename is directly loaded.
    '''
    return getDataXls(filename, filecontents)

def getDataXls(filename, filecontents=None):
    '''
    Loads the old excel format files. New format files will automatically
    get loaded as well.
    
    Args:
        filename: The name of the local file, or the holder for the
            extension type when the filecontents are supplied.
        filecontents: The file-like object holding contents of filename.
            If left as None, then filename is directly loaded.
    '''
    def tupledateToIsoDate(tupledate):
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
        (y,m,d, hh,mm,ss) = tupledate
        nonzero = lambda n: n!=0
        date = "%04d-%02d-%02d"  % (y,m,d)    if filter(nonzero, (y,m,d))                else ''
        time = "T%02d:%02d:%02d" % (hh,mm,ss) if filter(nonzero, (hh,mm,ss)) or not date else ''
        return date+time

    def formatExcelVal(book, val_type, value, wanttupledate):
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
            value = datetuple if wanttupledate else tupledateToIsoDate(datetuple)
        elif val_type == 5: # ERROR
            value = xlrd.error_text_from_code[value]
        return value
    
    def xlrdXlsToArray(filename, filecontents=None):
        '''
        Returns: 
            A list of sheets; each sheet is a dict containing
            { sheet_name: unicode string naming that sheet,
              sheet_data: 2-D table holding the converted cells of that sheet }
        '''   
        book       = xlrd.open_workbook(filename, file_contents=filecontents)
        sheets     = []
        formatter  = lambda(t,v): formatExcelVal(book,t,v,False)
        
        for sheet_name in book.sheet_names():
            raw_sheet = book.sheet_by_name(sheet_name)
            data      = []
            for row in range(raw_sheet.nrows):
                (types, values) = (raw_sheet.row_types(row), raw_sheet.row_values(row))
                data.append(map(formatter, zip(types, values)))
            sheets.append({'sheet_name': sheet_name, 'sheet_data': data})
        return sheets
    
    data = []
    
    for ws in xlrdXlsToArray(filename, filecontents):
        data.append(ws['sheet_data'])
    return data

def getDataCsv(filename, loadAsUnicode=True, filecontents=None):
    '''
    Gets good old csv data from a file.
    
    Args:
        filename: The name of the local file, or the holder for the
            extension type when the filecontents are supplied.
        loadAsUnicode: Loads the file as a unicode object.
        filecontents: The file-like object holding contents of filename.
            If left as None, then filename is directly loaded.
    '''
    table = []
    
    def processCsv(csvfile):
        for line in csvfile:
            if loadAsUnicode:
                table.append([unicode(cell, 'utf-8') for cell in line])
            else:
                table.append(line)
    
    if filecontents:
        csvfile = StringIO(filecontents)
        processCsv(csv.reader(csvfile, dialect=csv.excel))
    else:
        with open(filename, "rb") as csvfile:
            processCsv(csv.reader(csvfile, dialect=csv.excel))
    
    return [table]

def write(data, filename):
    '''
    Writes 2D tables to file.
    
    Args:
        data: 2D list of tables/worksheets.
        filename: Name of the output file (determines type).
    '''
    if re.search(xlsxExtRegex, filename):
        return writeXlsx(data, filename)
    elif re.search(xlsExtRegex, filename):
        return writeXls(data, filename)
    elif re.search(csvExtRegex, filename):
        return writeCsv(data, filename)
    else:
        return writeCsv(data, filename)
      
def writeXlsx(data, filename):
    '''
    Writes out to new excel format.
    
    Args:
        data: 2D list of tables/worksheets.
        filename: Name of the output file.
    '''
    raise NotImplementedError("Xlsx writing not implemented")

def writeXls(data, filename):
    '''
    Writes out to old excel format.
    
    Args:
        data: 2D list of tables/worksheets.
        filename: Name of the output file.
    '''
    raise NotImplementedError("Xls writing not implemented")
 
def writeCsv(data, filename):
    '''
    Writes out to csv format.
    
    Args:
        data: 2D list of tables/worksheets.
        filename: Name of the output file.
    '''   
    nameExtension = len(data) > 1
    root, ext = os.path.splitext(filename)
    
    for i, sheet in enumerate(data):
        fname = filename if not nameExtension else root+"_"+str(i)+ext
        with open(fname, "wb") as datafile:
            csvfile = csv.writer(datafile)
            for line in sheet:
                csvfile.writerow(line)
    