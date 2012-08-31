import csv, re, os

'''
Gets the extension from a file name
'''
def getExtension(filename):
    name, extension = os.path.splitext(filename)
    return extension[1:]

'''
Loads arbitrary data from a specified file. The data is
returned as a list of lines unless the delimiter is 
specified or the file extension is a csv, in which case 
a list of lists of tokens is returned. Each sublist of
tokens represents a single line.

Return Format:
    list[ ('line as string' or 'list[ tokens ]') ]
'''
class FileDataLoader(object):
    def __init__(self, filename, filedir='', delimiter=None):
        self.filename = filename
        self.filedir = filedir
        self.delim = delimiter
        self._file = None
        self._reader = None
        
    def _getDelim(self):
        return "," if self.delim == None else self.delim
    
    def _getFullPath(self):
        if self.filedir and not os.path.isabs(self.filename):
            return os.path.join(self.filedir, self.filename)
        else:
            return self.filename
        
    def _loadCSV(self):
        fullname = self._getFullPath()
        delimiter = self._getDelim()
        with open(fullname, 'rb') as file:
            reader = csv.reader(file, delimiter=delimiter)
            return [line for line in reader]
        
    def _loadRaw(self):
        fullname = self._getFullPath()
        with open(fullname, 'rb') as file:
            if self.delim == None:
                return file.readlines()
            else:
                return [line.split(self.delim) for line in file.readlines()]
            
    def loadData(self):
        if getExtension(self.filename) == 'csv':
            return self._loadCSV()
        else:
            return self._loadRaw()
        
    '''
    Either grab our reader's iterator, or load the data
    and return that iterator (if we're not in a with block).
    '''
    def __iter__(self):
        if self._reader != None:
            return self._reader.__iter__()
        else:
            return self.loadData().__iter__()
    
    '''
    Used to safely access the data via 'with' statements.
    Once inside the block the iterator will perform lazy
    loading on each line of the data.
    
    The file will be safely closed on exit from this block.
    '''
    def __enter__(self):
        fullname = self._getFullPath()
        # Open file gingerly
        try:
            self._file = open(fullname, 'rb')
        # Failed, close file and ignore errors
        except:
            try: self._file.close()
            except: pass
            finally: self._file = None
        # If file load is all good, set our reader
        else:
            if getExtension(self.filename) == 'csv':
                delimiter = self._getDelim()
                self._reader = csv.reader(self._file, delimiter=delimiter)
            else:
                self._reader = self._file
        return self
        
    def __exit__(self, type, value, traceback):
        try:
            if self._file != None:
                self._file.close()
        finally:
            self.file = None
            self._reader = None


