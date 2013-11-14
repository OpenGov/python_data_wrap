import filedbwrap

class AttributeSavable(object):
    '''
    Defines a object which can save attributes to a file and load those attributes 
    upon initialization. This allows for easy persistent storing of object 
    characteristics.
    
    Args:
        file_name: The file_name used to store the attributes without an extension.
        attributes: An iterable of all the attributes from attr_obj to be saved.
        db_ext: The extension on the file_name to be used 
            (default filedbwrap.get_default_file_ext()).
        attr_obj: The object whose attributes are being saved.
            (default self -- inheritance assumed).
        read_only: Determines if settings are saved on deconstruction/save_attributes().
    '''
    def __init__(self, file_name, attributes, db_ext=None, attr_obj=None, read_only=False):
        self._file_name = file_name
        self._db_ext = db_ext
        self._target = attr_obj if attr_obj != None else self
        self._read_only = read_only
        
        # We need to 'close' the file for the open to work
        self._db_closed = True
        if self.saveable():
            self.open_attributes_file()
        
            self._saved_attrs = attributes
            for attr_name in self._fd:
                if attr_name in self._saved_attrs:
                    setattr(self._target, attr_name, self._fd[attr_name])
    
    def __del__(self):
        if self.saveable() and not self._read_only:
            # Save if we're garbage collected
            self.save_and_close_attributes()
          
    def saveable(self):
        '''
        Used to determine if the attributes are saveable. Giving an 
        empty file_name results in attributes being unsaveable.
        '''
        return bool(self._file_name)
        
    def open_attributes_file(self):
        '''
        Called during initialization. Only needs to be explicitly
        called if save_and_close_attributes is explicitly called
        beforehand.
        '''
        if not self.saveable():
            raise AttributeError("Cannot open attribute file without a valid file")
        if self._db_closed:
            self._fd = filedbwrap.FileDict(self._file_name, db_ext=self._db_ext, 
                                           read_only=self._read_only, clear=False, cache_size=0, 
                                           immutable_vals=False, stringify_keys=False, 
                                           cache_misses=False)
            self._db_closed = False
            
    def save_attributes(self):
        '''
        Saves the attributes without closing the attributes file.
        This should probably be called after the attribute holder
        sets/overrides the attributes in initialization as the del
        method is not guaranteed to be called.
        '''
        if not self.saveable():
            raise AttributeError("Cannot save attribute file without a valid file")
        if self._read_only:
            raise AttributeError("Cannot save read-only data")
        if not self._db_closed:
            self._fd.clear()
            for attr_name in self._saved_attrs:
                self._fd[attr_name] = getattr(self._target, attr_name)
    
    def save_and_close_attributes(self):
        '''
        Performs the same function as save_attributes but also closes
        the attribute file.
        '''
        if not self.saveable():
            raise AttributeError("Cannot save attribute file without a valid file")
        if not self._db_closed:
            self._db_closed = True
            if not self._read_only:
                self.save_attributes()
            self._fd.close()
    