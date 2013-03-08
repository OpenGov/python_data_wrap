import collections, shelve, os

'''
Helper function for all file wrappers to identify
standard extension.
'''
def getDefaultFileExt():
    return "fd"

'''
An unordered block cache with full reject upon overflow. Since
LRU style caches require much more overhead in software over
hardware, this naive block rejection is one of the fastest solutions.

The Cache is constructed with a database object behind it so that
missed requests fall through to the full database. Thus this object
wraps the full database as a cached database.

The database must implement __getitem__, __setitem__, __iter__, 
__len__, __contains__, __delitem__ and (optional) close.

Cache Size is defined as number of elements, not size of elements,
so caches with many large elements might take more memory than 
expected.

NOTE: Pushing None values into the dictionary will cause an exception
and getting an item with None value is considered to be an entry for
no item present.

@author Matt Seal
'''
class UnorderedCachedDict(collections.MutableMapping):
    def __init__(self, database, cacheSize, readOnly=False, 
                 immutableVals=False, stringifyKeys=False,
                 cacheMisses=True, databaseDefaultFunc=None,
                 readPoolSize=0, **kwargs):
        self.cacheSize = cacheSize
        self.readOnly = readOnly
        self.stringifyKeys = stringifyKeys
        self.closed = False
        
        self._immutableVals = immutableVals
        self._cacheMisses = cacheMisses
        self._cache = {}
        self._curSize = 0
        self._readPoolSize = readPoolSize
        self._wqueue = set()
        self._database = database
        self._databaseDefaultFunc = databaseDefaultFunc
        
    def _addInitKwargs(self, kwargs):
        # These can be changed by caller
        if 'cacheSize' not in kwargs:
            kwargs['cacheSize'] = self.cacheSize
        if 'readOnly' not in kwargs:
            kwargs['readOnly'] = self.readOnly
        if 'cacheMisses' not in kwargs:
            kwargs['cacheMisses'] = self._cacheMisses
        if 'databaseDefaultFunc' not in kwargs:
            kwargs['databaseDefaultFunc'] = self._databaseDefaultFunc
        if 'readPoolSize' not in kwargs:
            kwargs['readPoolSize'] = self._readPoolSize
        if 'immutableVals' not in kwargs:
            kwargs['immutableVals'] = self._immutableVals
        if 'stringifyKeys' not in kwargs:
            kwargs['stringifyKeys'] = self.stringifyKeys
        
    def _reinit(self, **kwargs):
        self._addInitKwargs(kwargs)
        
        # If we're not overwritten, pass this
        kwargs['database'] = self._database
        
        # Call __init__ again
        self.close()
        self.__init__(**kwargs)
        
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self.close()
        
    def _checkCacheSize(self):
        if self._curSize > self.cacheSize:
            if self.readOnly:
                self.dropCache()
            else:
                self.syncCache()
    
    '''
    Gets the cache as a stand-alone object -- updates
    directly to this cache will not be reflected/registered 
    with the core database.
    '''
    def getCache(self):
        return self._cache
    
    '''
    Checks cache for entry, then database for entry.
    '''
    def __getitem__(self, key):
        val = None
        if key != None and self.stringifyKeys:
            key = str(key)
        try:
            val = self._cache.__getitem__(key)
        except KeyError:
            try:
                val = self._database.__getitem__(key)
            except KeyError: pass
            if val != None or self._cacheMisses:
                self._insertCache(key, val, True)
                self._checkCacheSize()
        if val == None: 
            if self._databaseDefaultFunc:
                val = self._databaseDefaultFunc()
            else:
                raise KeyError(key)
        return val
    
    def __iter__(self):
        self.syncWrites()
        return self._database.__iter__()
    
    '''
    Does an insert into the cache such that the cache
    will have an updated entry for the key,value,read
    tuple. Any changes to those values will both update
    the local cache and queue any required writes to the
    database.
    '''
    def _insertCache(self, key, val, read):
        if key != None and self.stringifyKeys:
            key = str(key)
        cval = self._cache.get(key)
        if cval == None:
            self._curSize += 1
        if cval == None or val != cval:
            self._cache[key] = val
            # Force a write if it's a write or if it's
            # unclear that the item was modified
            if not self.readOnly and (not self._immutableVals or not read):
                self._wqueue.add(key)
    
    '''
    This might take a very long time if the db doesn't
    have a good __len__ implementation.
    '''
    def __len__(self):
        # Need to sync before we know our true size
        self.syncWrites()
        return len(self._database)
    
    '''
    Checks cache for entry, then database for entry.
    '''
    def __contains__(self, key):
        if key != None and self.stringifyKeys:
            key = str(key)
        try:
            cont = (self._cache.__getitem__(key) != None)
        except KeyError:
            try:
                val = self._database.__getitem__(key)
                cont = True
            except KeyError:
                val = None
                cont = False
            # Store if it's a value or if we store missed checks
            if val != None or self._cacheMisses:
                self._insertCache(key, val, True)
            self._checkCacheSize()
        return cont
        
    def __setitem__(self, key, val):
        if val == None:
            raise AttributeError("Attempted to set a key value to None")
        if self.readOnly:
            raise AttributeError("Attempted to set in readOnly mode")
        if key != None and self.stringifyKeys:
            key = str(key)
        self._insertCache(key, val, False)
        self._checkCacheSize()
           
    '''
    Deletes from both the cache, write queues and the database
    ''' 
    def __delitem__(self, key):
        if self.readOnly:
            raise AttributeError("Attempted to delete in readOnly mode")
        if key != None and self.stringifyKeys:
            key = str(key)
            
        if self._cacheMisses:
            self._insertCache(key, None, True)
        elif key in self._cache:
            del self._cache[key]
        if key in self._wqueue:
            self._wqueue.discard(key)
        # We don't know if the database has this item or not
        if key in self._database:
            self._database.__delitem__(key)
          
    '''
    Flushes the write queue
    '''  
    def syncWrites(self):
        for key in self._wqueue:
            val = self._cache[key]
            self._database[key] = val
        del self._wqueue
        self._wqueue = set()
        self._database.sync()
            
    '''
    Flushes the write queue to the database
    '''
    def syncCache(self):
        self.syncWrites()
        self.dropCache()
        
    '''
    Drops all changes in the cache
    '''
    def dropCache(self):
        del self._cache
        self._cache  = {}
        del self._wqueue
        self._wqueue = set()
        self._curSize = 0
        
    def close(self, **kwargs):
        if not self.closed:
            self.syncCache()
            # This will barf if the database doesn't have a close operator,
            # so check for close first
            if hasattr(self._database, 'close'):
                self._database.close(**kwargs)
        self.closed = True
        
    def __del__(self):
        # Close if we're being collected
        self.close()
        
'''
Acts much like an UnorderedCachedDict except it stores key existence
instead of key value pairs. Thus the data is still stored in the
database as a dictionary, but treated as a set on the external
interface.

@author Matt Seal
'''
class UnorderedCachedSet(collections.MutableSet, UnorderedCachedDict):
    def __init__(self, database, cacheSize, readOnly=False, cacheMisses=True, 
                 immutableVals=False, stringifyKeys=False, readPoolSize=0, **kwargs):
        UnorderedCachedDict.__init__(self, database, cacheSize=cacheSize, 
                                     cacheMisses=cacheMisses, readOnly=readOnly, 
                                     immutableVals=immutableVals, readPoolSize=readPoolSize, 
                                     stringifyKeys=stringifyKeys, **kwargs)
        
    '''
    These allow for direct access to the dictionary holding
    the set under a different naming convention (to prevent
    dictionary like syntax from working on external interface).
    '''
    def _dictSet(self, key, val):
        # Call UnorderedCachedDict's version of setitem since we've disabled it
        # No need to check stringifyKeys, as it will be checked in the next setitem
        UnorderedCachedDict.__setitem__(self, key, val)
        
    def _dictGet(self, key):
        # Call UnorderedCachedDict's version of setitem since we've disabled it
        # No need to check stringifyKeys, as it will be checked in the next setitem
        return UnorderedCachedDict.__getitem__(self, key)
        
    def add(self, elem):
        self._dictSet(elem, True)

    def discard(self, elem):
        self.__delitem__(elem)
    
    def __getitem__(self, elem):
        raise AttributeError( "'Set' object has no attribute '__getitem__'" )
    
    def __setitem__(self, key, val):
        raise AttributeError( "'Set' object has no attribute '__setitem__'" )
    
    '''
    Updates the set to include all arguments passed in.
    If the keyword argument preprocess is passed, then
    each element is preprocessed before being added.
    '''
    def update(self, *args, **kwargs):
        preprocess = kwargs.get('preprocess')
        for s in args:
            for e in s:
                self._dictSet(preprocess(e) if preprocess else e, True)

'''
This is a standard dictionary, with some additional functions
for syntax compatability with other DB wrappers. This is slower
than a normal dictionary and should only be used to keep syntax
standardized among several databases

@author Matt Seal
'''
class MemDict(collections.MutableMapping):
    # Careful with changing __init__ params and forgetting them in _reinit
    def __init__(self, dbname, readOnly=False, databaseDefaultFunc=None, 
                 stringifyKeys=False, **kwargs):
        self._dbname = dbname
        self.readOnly = readOnly
        self.stringifyKeys = stringifyKeys
        self._databaseDefaultFunc = databaseDefaultFunc
        self._database = {}
        self._resetDatabase()
        
    def _addInitKwargs(self, kwargs):
        # These can be changed by caller
        if 'readOnly' not in kwargs:
            kwargs['readOnly'] = self.readOnly
        if 'stringifyKeys' not in kwargs:
            kwargs['stringifyKeys'] = self.stringifyKeys
        if 'databaseDefaultFunc' not in kwargs:
            kwargs['databaseDefaultFunc'] = self._databaseDefaultFunc
        
        # This stays the same
        kwargs['dbname'] = self._dbname
        
    def _reinit(self, **kwargs):
        self._addInitKwargs(kwargs)
        
        # Call __init__ again
        self.close()
        self.__init__(**kwargs)
        
    def _resetDatabase(self):
        del self._database
        self._database = {}
        
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self.close()
                
    def getCache(self):
        return self._database
    
    def __getitem__(self, key):
        if key != None and self.stringifyKeys:
            key = str(key)
        try:
            return self._database.__getitem__(key)
        except KeyError: 
            if self._databaseDefaultFunc != None:
                return self._databaseDefaultFunc()
            else:
                raise
    
    def __iter__(self):
        return self._database.__iter__()
            
    def __len__(self):
        return self._database.__len__()
    
    def __contains__(self, key):
        if key != None and self.stringifyKeys:
            key = str(key)
        return self._database.__contains__(key)
        
    def __setitem__(self, key, val):
        if self.readOnly:
            raise AttributeError("Attempted to set in readOnly mode")
        if key != None and self.stringifyKeys:
            key = str(key)
        self._database.__setitem__(key, val)
            
    def __delitem__(self, key):
        if self.readOnly:
            raise AttributeError("Attempted to delete in readOnly mode")
        if key != None and self.stringifyKeys:
            key = str(key)
        self._database.__delitem__(key)
            
    def syncWrites(self):
        pass # No-op
            
    def syncCache(self):
        pass # No-op
        
    def dropCache(self):
        pass # No-op
        
    def close(self, **kwargs):
        self._resetDatabase()
        
    def reopen(self, readOnly=None, **kwargs):
        self.readOnly = readOnly if readOnly != None else self.readOnly
        if 'databaseDefaultFunc' in kwargs:
            self._databaseDefaultFunc = kwargs['databaseDefaultFunc']
        if 'stringifyKeys' in kwargs:
            self.stringifyKeys = kwargs['stringifyKeys']
        # No need to re-initialize -- it's already in memory
        
    def clear(self, readOnly=None, **kwargs):
        # Careful with changing __init__ params and forgetting them here...
        if readOnly != None:
            kwargs['readOnly'] = readOnly
        self._reinit(**kwargs)
        
    def __del__(self):
        # Close if we're being collected
        self.close()
    
'''
This wraps a standard dictionary with a file persistence that
allows the dictionary to be reloaded and/or saved upon closing.

@author Matt Seal
'''    
class MemFromFileDict(MemDict):
    # Careful with changing __init__ params and forgetting them in _reinit
    def __init__(self, dbname, dbext=None, readOnly=False, databaseDefaultFunc=None, 
                 clear=False, stringifyKeys=False, **kwargs):
        MemDict.__init__(self, dbname, readOnly=readOnly, 
                         stringifyKeys=stringifyKeys, 
                         databaseDefaultFunc=databaseDefaultFunc, 
                         **kwargs)
        self._dbext = dbext if dbext != None else getDefaultFileExt()
        absdirpath = os.path.dirname(os.path.abspath(dbname))
        dirpresent = os.path.exists(absdirpath)
        if not dirpresent:
            try: os.makedirs(absdirpath)
            except OSError: pass
        self._dbfullpath = '.'.join((os.path.abspath(dbname), self._dbext))
        filepresent = os.path.exists(self._dbfullpath)
        self.flag = 'n' if clear else 'r' if readOnly and filepresent else 'c'
        self.closed = False
        self._dbfile = shelve.open(self._dbfullpath, flag=self.flag)
        if not clear:
            # Copy all elements into memory dict
            for key in self._dbfile:
                self._database[key] = self._dbfile[key]
        # We're done with the file for now
        self._dbfile.close()
        
    def _addInitKwargs(self, kwargs):
        MemDict._addInitKwargs(self, kwargs)
        
        kwargs['dbname'] = self._dbname
        kwargs['dbext'] = self._dbext
        
    def _reinit(self, **kwargs):
        self._addInitKwargs(kwargs)
        self.close()
        self.__init__(**kwargs)
            
    def reopen(self, readOnly=None, **kwargs):
        kwargs['readOnly'] = readOnly if readOnly != None else self.readOnly
        kwargs['clear'] = False
        self._reinit(**kwargs)
            
    def clear(self, readOnly=None, **kwargs):
        kwargs['readOnly'] = readOnly if readOnly != None else self.readOnly
        kwargs['clear'] = True
        self._reinit(**kwargs)
        
    def close(self, deleteFile=False, **kwargs):
        if deleteFile:
            # Security vulnerability if file is accessible by 3rd party
            # as there is a time gap between closing and deleting
            try: os.remove(self._dbfullpath)
            except: pass
        elif not self.closed:
            self.syncCache()
        self._resetDatabase()
        self.closed = True
        
    def syncWrites(self):
        if not self.readOnly:
            self._dbfile = shelve.open(self._dbfullpath, flag='n')
            for key in self._database:
                self._dbfile[key] = self._database[key]
            self._dbfile.sync()
            # We're done with the file for now
            self._dbfile.close()
            
    def syncCache(self):
        self.syncWrites()
        self.dropCache()

'''
Defines a dictionary based on a file, with an unordered
memory cache. The database is saved to file when the cache
gets too large or it is synced. This allows for very large
databases to be stored in the filesystem without consuming
all available memory.

@author Matt Seal
'''
class FileDict(UnorderedCachedDict):
    # Careful with changing __init__ params and forgetting them in _reinit
    def __init__(self, dbname, dbext=None, readOnly=False, clear=False, cacheSize=10*1024, 
                 immutableVals=False, stringifyKeys=False, cacheMisses=True,
                 databaseDefaultFunc=None, readPoolSize=0, **kwargs):
        self._dbname = dbname
        self._dbext = dbext if dbext != None else getDefaultFileExt()
        absdirpath = os.path.dirname(os.path.abspath(dbname))
        dirpresent = os.path.exists(absdirpath)
        if not dirpresent:
            try: os.makedirs(absdirpath)
            except OSError: pass
        self._dbfullpath = '.'.join((os.path.abspath(dbname), self._dbext))
        filepresent = os.path.exists(self._dbfullpath)
        self.flag = 'n' if clear else 'r' if readOnly and filepresent else 'c'
        self._database = shelve.open(self._dbfullpath, flag=self.flag)
        self.closed = False
        UnorderedCachedDict.__init__(self, self._database, cacheSize=cacheSize, 
                                     databaseDefaultFunc=databaseDefaultFunc, readOnly=readOnly, 
                                     immutableVals=immutableVals, stringifyKeys=stringifyKeys,
                                     cacheMisses=cacheMisses, readPoolSize=readPoolSize, **kwargs)
    
    def _addInitKwargs(self, kwargs):
        kwargs['dbname'] = self._dbname
        kwargs['dbext'] = self._dbext
        UnorderedCachedDict._addInitKwargs(self, kwargs)
        
    def _reinit(self, **kwargs):
        self._addInitKwargs(kwargs)
        self.close()
        self.__init__(**kwargs)
        
    def reopen(self, readOnly=None, cacheSize=None, **kwargs):
        if readOnly != None:
            kwargs['readOnly'] = readOnly
        if cacheSize != None:
            kwargs['cacheSize'] = cacheSize
        kwargs['clear'] = False
        self._reinit(**kwargs)
        
    def clear(self, readOnly=None, cacheSize=None, **kwargs):
        if readOnly != None:
            kwargs['readOnly'] = readOnly
        if cacheSize != None:
            kwargs['cacheSize'] = cacheSize
        kwargs['clear'] = True
        self._reinit(**kwargs)
        
    def close(self, deleteFile=False, **kwargs):
        if deleteFile:
            # Security vulnerability if file is accessible by 3rd party
            # as there is a time gap between closing and deleting
            if not self.closed:
                self._database.close()
            try: os.remove(self._dbfullpath)
            except: pass
        elif not self.closed:
            self.syncCache()
            self._database.close()
        self.closed = True
        
'''
Much like a FileDict, except treated as a Set instead.

@author Matt Seal
'''
class FileSet(UnorderedCachedSet):
    # Careful with changing __init__ params and forgetting them in reopen/clear
    def __init__(self, dbname, dbext=None, readOnly=False, clear=False, cacheSize=10*1024, 
                 immutableVals=False, stringifyKeys=False, cacheMisses=True, 
                 readPoolSize=0, **kwargs):
        self._dbname = dbname
        self._dbext = dbext if dbext != None else getDefaultFileExt()
        absdirpath = os.path.dirname(os.path.abspath(dbname))
        dirpresent = os.path.exists(absdirpath)
        if not dirpresent:
            try: os.makedirs(absdirpath)
            except OSError: pass
        self._dbfullpath = '.'.join((os.path.abspath(dbname), self._dbext))
        filepresent = os.path.exists(self._dbfullpath)
        self.flag = 'n' if clear else 'r' if readOnly and filepresent else 'c'
        self._database = shelve.open(self._dbfullpath, flag=self.flag)
        self.closed = False
        UnorderedCachedSet.__init__(self, self._database, cacheSize=cacheSize, 
                                    readOnly=readOnly, immutableVals=immutableVals,
                                    stringifyKeys=stringifyKeys, 
                                    cacheMisses=cacheMisses, 
                                    readPoolSize=readPoolSize, **kwargs)
        
    def _addInitKwargs(self, kwargs):
        kwargs['dbname'] = self._dbname
        kwargs['dbext'] = self._dbext
        UnorderedCachedSet._addInitKwargs(self, kwargs)
        
    def _reinit(self, **kwargs):
        self._addInitKwargs(kwargs)
        self.close()
        self.__init__(**kwargs)
        
    def reopen(self, readOnly=None, cacheSize=None, **kwargs):
        if readOnly != None:
            kwargs['readOnly'] = readOnly
        if cacheSize != None:
            kwargs['cacheSize'] = cacheSize
        kwargs['clear'] = False
        self._reinit(**kwargs)
        
    def clear(self, readOnly=None, cacheSize=None, **kwargs):
        if readOnly != None:
            kwargs['readOnly'] = readOnly
        if cacheSize != None:
            kwargs['cacheSize'] = cacheSize
        kwargs['clear'] = True
        self._reinit(**kwargs)
        
    def close(self, deleteFile=False, **kwargs):
        if deleteFile:
            # Security vulnerability if file is accessible by 3rd party
            # as there is a time gap between closing and deleting
            if not self.closed:
                self._database.close()
            try: os.remove(self._dbfullpath)
            except: pass
        elif not self.closed:
            self.syncCache()
            self._database.close()
        self.closed = True
        
'''
Defines a way to split data among any number of arbitrary databases.
All arguments in kwargs are applied to each database constructor.

The default database class is baseDbClass, while key specific classes
can be defined in keyedClasses as a dictionary input. These overwrite
the default dbclass.

If the splitFunc gives an invalid key name, a KeyError will be raised,
so make sure updates to splitKeys also updates splitFunc.

If a cacheSize if passed through kwargs, it is evenly divided among all
databases.

@author Matt Seal
'''
class SplitDbDict(collections.MutableMapping):
    def __init__(self, dbname, baseDbClass, splitKeys, splitFunc, keyedClasses=None, 
                 stringifyKeys=False, **kwargs):
        self.stringifyKeys = stringifyKeys
        self.splitKeys = splitKeys
        self.splitFunc = splitFunc
        
        self._dbname = dbname
        self._keyedDb = {}
        self._baseDbClass = baseDbClass
        self._keyedClasses = keyedClasses if keyedClasses else {}
        # Force caches to be split evenly among all databases
        self.checkUpdateCacheSet(len(self.splitKeys), kwargs)
        for skey in self.splitKeys:
            if self._keyedClasses and skey in self._keyedClasses:
                dbclass = self._keyedClasses[skey]
            else:
                dbclass = self._baseDbClass
            self._keyedDb[skey] = dbclass(self._dbname+'_'+str(skey), **kwargs)
            
    def checkUpdateCacheSet(self, numKeys, kwargs):
        if "cacheSize" in kwargs:
            kwargs["cacheSize"] /= numKeys
            
    def reopen(self, **kwargs):
        # Force caches to be split evenly among all databases
        self.checkUpdateCacheSet(len(self.splitKeys), kwargs)
        for db in self._keyedDb.values():
            if hasattr(db, 'reopen'):
                db.reopen(**kwargs)
            
    def clear(self, **kwargs):
        # Force caches to be split evenly among all databases
        self.checkUpdateCacheSet(len(self.splitKeys), kwargs)
        for db in self._keyedDb.values():
            if hasattr(db, 'clear'):
                db.clear(**kwargs)
            
    def close(self, **kwargs):
        for db in self._keyedDb.values():
            if hasattr(db, 'close'):
                db.close(**kwargs)
            
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self.close()
                
    def getCache(self):
        cahces = {}
        for shortkey, db in self._keyedDb.items():
            cahces[shortkey] = db.getCache()
        return cahces
    
    def __getitem__(self, key):
        if key != None and self.stringifyKeys:
            key = str(key)
        db = self._keyedDb[self.splitFunc(key)]
        return db.__getitem__(key)
    
    '''
    The iterator for this class wraps the iterators for
    all stored DBs and throws the usual StopIteration()
    exception when all iterators have been exhausted.
    '''
    def __iter__(self):
        class MultiIter(object):
            def __init__(self, iterables):
                self.iterables = [iter.__iter__() for iter in iterables]
                self.curIter = None
            
            def __iter__(self):
                return self
            
            def next(self):
                if self.curIter == None:
                    # If we're out of iterables, then StopIteration
                    try:
                        self.curIter = self.iterables.pop()
                    except IndexError:
                        raise StopIteration()
                try:
                    return self.curIter.next()
                except StopIteration:
                    # Clear out the iterator and call next
                    self.curIter = None
                    return self.next()
        
        return MultiIter(self._keyedDb.values())
            
    def __len__(self):
        totlen = 0
        for db in self._keyedDb.values():
            totlen += db.__len__()
        return totlen
    
    def __contains__(self, key):
        if key != None and self.stringifyKeys:
            key = str(key)
        db = self._keyedDb[self.splitFunc(key)]
        return db.__contains__(key)
        
    def __setitem__(self, key, val):
        if key != None and self.stringifyKeys:
            key = str(key)
        db = self._keyedDb[self.splitFunc(key)]
        db.__setitem__(key, val)
            
    def __delitem__(self, key):
        if key != None and self.stringifyKeys:
            key = str(key)
        db = self._keyedDb[self.splitFunc(key)]
        db.__delitem__(key)
            
    def syncWrites(self):
        for db in self._keyedDb.values():
            db.syncWrites()
            
    def syncCache(self):
        for db in self._keyedDb.values():
            db.syncCache()
        
    def dropCache(self):
        for db in self._keyedDb.values():
            db.dropCache()
            
    def __del__(self):
        # Close if we're being collected
        self.close()
        
'''
Defines a way to split data among any number of arbitrary databases.
All arguments in kwargs are applied to each database constructor.

The default database class is baseDbClass, while key specific classes
can be defined in keyedClasses as a dictionary input. These overwrite
the default dbclass.

If the splitFunc gives an invalid key name, a KeyError will be raised,
so make sure updates to splitKeys also updates splitFunc.

If a cacheSize if passed through kwargs, it is evenly divided among all
databases.

@author Matt Seal
'''
class SplitDbSet(collections.MutableSet, SplitDbDict):
    def __init__(self, dbname, baseDbClass, splitKeys, splitFunc, keyedClasses=None, 
                 stringifyKeys=False, **kwargs):
        self.stringifyKeys = stringifyKeys
        self.splitKeys = splitKeys
        self.splitFunc = splitFunc
        
        self._dbname = dbname
        self._keyedDb = {}
        self._baseDbClass = baseDbClass
        self._keyedClasses = keyedClasses if keyedClasses else {}
        # Force caches to be split evenly among all databases
        if "cacheSize" in kwargs:
            kwargs["cacheSize"] /= len(self.splitKeys)
        for skey in self.splitKeys:
            if self._keyedClasses and skey in self._keyedClasses:
                dbclass = self._keyedClasses[skey]
            else:
                dbclass = self._baseDbClass
            self._keyedDb[skey] = dbclass(self._dbname+'_'+str(skey), **kwargs)
            
    '''
    These allow for direct access to the dictionary holding
    the set under a different naming convention (to prevent
    dictionary like syntax from working on external interface).
    '''
    def _dictSet(self, key, val):
        if key != None and self.stringifyKeys:
            key = str(key)
        db = self._keyedDb[self.splitFunc(key)]
        db._dictSet(key, val)
        
    def _dictGet(self, key):
        if key != None and self.stringifyKeys:
            key = str(key)
        db = self._keyedDb[self.splitFunc(key)]
        return db._dictGet(key)
        
    def add(self, elem):
        self._dictSet(elem, True)

    def discard(self, elem):
        self.__delitem__(elem)
    
    def __getitem__(self, elem):
        raise AttributeError( "'Set' object has no attribute '__getitem__'" )
    
    def __setitem__(self, key, val):
        raise AttributeError( "'Set' object has no attribute '__setitem__'" )
    
    '''
    Updates the set to include all arguments passed in.
    If the keyword argument preprocess is passed, then
    each element is preprocessed before being added.
    '''
    def update(self, *args, **kwargs):
        preprocess = kwargs.get('preprocess')
        for s in args:
            for e in s:
                self._dictSet(preprocess(e) if preprocess else e, True)
        
'''
Defines a split DB (see SplitDbDict) based on separate files.
This is useful if you have a large dictionary of words and want
to store all words with the same first character together.

@author Matt Seal
'''
class SplitFileDict(SplitDbDict):
    def __init__(self, dbname, splitKeys, splitFunc, dbext=None, readOnly=False, 
                 clear=False, cacheMisses=True, cacheSize=10*1024, immutableVals=False, 
                 stringifyKeys=False, databaseDefaultFunc=None, **kwargs):
        SplitDbDict.__init__(self, dbname, FileDict, splitKeys, splitFunc, dbext=dbext,
                             readOnly=readOnly, clear=clear, cacheSize=cacheSize,
                             immutableVals=immutableVals, stringifyKeys=stringifyKeys, 
                             databaseDefaultFunc=databaseDefaultFunc, 
                             cacheMisses=cacheMisses, **kwargs)
        
'''
Much like a SplitFileDict, except treated as a Set instead.

@author Matt Seal
'''
class SplitFileSet(SplitDbSet):
    def __init__(self, dbname, splitKeys, splitFunc, dbext=None, readOnly=False, 
                 clear=False, cacheMisses=True, cacheSize=10*1024, immutableVals=False, 
                 stringifyKeys=False, **kwargs):
        SplitDbSet.__init__(self, dbname, FileSet, splitKeys, splitFunc, dbext=dbext,
                            readOnly=readOnly, clear=clear, cacheSize=cacheSize,
                            immutableVals=immutableVals, stringifyKeys=stringifyKeys, 
                            cacheMisses=cacheMisses, **kwargs)

