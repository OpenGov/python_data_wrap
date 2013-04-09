import filedbwrap

class AttributeSavable(object):
    '''
    Defines a object which can save attributes to a file and
    load those attributes upon initialization. This allows
    for easy persistent storing of object characteristics.
    
    @param filename The filename used to store the attributes
                    without an extension.
    @param attributes An iterable of all the attributes from
                      attrObj to be saved.
    @param dbext The extension on the filename to be used
                 (default filedbwrap.getDefaultFileExt()).
    @param attrObj The object whose attributes are being saved
                   (default self -- inheritance assumed).
    @param readOnly Determines if settings are saved on 
                    deconstruction / saveAttributes().
    @author Matt Seal
    '''
    def __init__(self, filename, attributes, dbext=None, attrObj=None, readOnly=False):
        self._filename = filename
        self._dbext = dbext
        self._target = attrObj if attrObj != None else self
        self._readOnly = readOnly
        
        # We need to 'close' the file for the open to work
        self._dbclosed = True
        if self.saveable():
            self.openAttributesFile()
        
            self._savedAttr = attributes
            for attrName in self._fd:
                if attrName in self._savedAttr:
                    setattr(self._target, attrName, self._fd[attrName])
    
    def __del__(self):
        if self.saveable() and not self._readOnly:
            # Save if we're garbage collected
            self.saveAndCloseAttributes()
          
    def saveable(self):
        '''
        Used to determine if the attributes are saveable. Giving an 
        empty filename results in attributes being unsaveable.
        '''
        return bool(self._filename)
        
    def openAttributesFile(self):
        '''
        Called during initialization. Only needs to be explicitly
        called if saveAndCloseAttributes is explicitly called
        beforehand.
        '''
        if not self.saveable():
            raise AttributeError("Cannot open attribute file without a valid file")
        if self._dbclosed:
            self._fd = filedbwrap.FileDict(self._filename, dbext=self._dbext, 
                                           readOnly=self._readOnly, 
                                           clear=False, cacheSize=0, immutableVals=False, 
                                           stringifyKeys=False, cacheMisses=False)
            self._dbclosed = False
            
    def saveAttributes(self):
        '''
        Saves the attributes without closing the attributes file.
        This should probably be called after the attribute holder
        sets/overrides the attributes in initialization as the del
        method is not guaranteed to be called.
        '''
        if not self.saveable():
            raise AttributeError("Cannot save attribute file without a valid file")
        if self._readOnly:
            raise AttributeError("Cannot save read-only data")
        if not self._dbclosed:
            self._fd.clear()
            for attrName in self._savedAttr:
                self._fd[attrName] = getattr(self._target, attrName)
    
    def saveAndCloseAttributes(self):
        '''
        Performs the same function as saveAttributes but also closes
        the attribute file.
        '''
        if not self.saveable():
            raise AttributeError("Cannot save attribute file without a valid file")
        if not self._dbclosed:
            self._dbclosed = True
            if not self._readOnly:
                self.saveAttributes()
            self._fd.close()
    