import csv, os

def get_extension(file_name):
    '''Gets the extension from a file name'''
    name, extension = os.path.splitext(file_name)
    return extension[1:]

class FileDataLoader(object):
    '''
    Loads arbitrary data from a specified file. The data is
    returned as a list of lines unless the delimiter is 
    specified or the file extension is a csv, in which case 
    a list of lists of tokens is returned. Each sublist of
    tokens represents a single line.
    
    Args:
        file_name: The file_name being requested for loading
        file_dir: The directory of the file (optional)
        delimiter: The delimiter to split lines (default ',' for csv)
    
    Return Format:
        list[ ('line as string' or 'list[ tokens ]') ]
    '''
    def __init__(self, file_name, file_dir='', delimiter=None):
        self.file_name = file_name
        self.file_dir = file_dir
        self.delim = delimiter
        self._file = None
        self._reader = None
        
    def _get_delim(self):
        return "," if self.delim == None else self.delim
    
    def _get_full_path(self):
        if self.file_dir and not os.path.isabs(self.file_name):
            return os.path.join(self.file_dir, self.file_name)
        else:
            return self.file_name
        
    def _load_csv(self):
        full_name = self._get_full_path()
        delimiter = self._get_delim()
        with open(full_name, 'rb') as dfile:
            reader = csv.reader(dfile, delimiter=delimiter)
            return [line for line in reader]
        
    def _load_raw(self):
        full_name = self._get_full_path()
        with open(full_name, 'rb') as dfile:
            if self.delim == None:
                return dfile.readlines()
            else:
                return [line.split(self.delim) for line in dfile.readlines()]
            
    def load_data(self, force_csv=False):
        if force_csv or get_extension(self.file_name) == 'csv':
            return self._load_csv()
        else:
            return self._load_raw()
        
    def __iter__(self):
        '''
        Either grab our reader's iterator, or load the data
        and return that iterator (if we're not in a with block).
        '''
        if self._reader != None:
            return self._reader.__iter__()
        else:
            return self.load_data().__iter__()
    
    def __enter__(self):
        '''
        Used to safely access the data via 'with' statements.
        Once inside the block the iterator will perform lazy
        loading on each line of the data.
        
        The file will be safely closed on exit from this block.
        '''
        full_name = self._get_full_path()
        # Open file gingerly
        try:
            self._file = open(full_name, 'rb')
        # Failed, close file and ignore errors
        except:
            try: self._file.close()
            except: pass
            finally: self._file = None
        # If file load is all good, set our reader
        else:
            if get_extension(self.file_name) == 'csv':
                delimiter = self._get_delim()
                self._reader = csv.reader(self._file, delimiter=delimiter)
            else:
                self._reader = self._file
        return self
        
    def __exit__(self, etype, value, traceback):
        try:
            if self._file != None:
                self._file.close()
        finally:
            self.file = None
            self._reader = None
