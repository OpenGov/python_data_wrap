import collections

class UnorderedCachedDict(collections.MutableMapping):
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
    '''
    def __init__(self, database, cache_size, read_only=False, 
                 immutable_vals=False, stringify_keys=False,
                 cache_misses=True, database_default_func=None,
                 read_pool_size=0, value_converter=None, **kwargs):
        self.cache_size = cache_size
        self.read_only = read_only
        self.stringify_keys = stringify_keys
        self.value_converter = value_converter
        self.closed = False

        self._immutable_vals = immutable_vals
        self._cache_misses = cache_misses
        self._cache = {}
        self._cur_size = 0
        self._read_pool_size = read_pool_size
        self._wqueue = set()
        self._database = database
        self._database_default_func = database_default_func

    def _add_init_kwargs(self, kwargs):
        # These can be changed by caller
        if 'cache_size' not in kwargs:
            kwargs['cache_size'] = self.cache_size
        if 'read_only' not in kwargs:
            kwargs['read_only'] = self.read_only
        if 'cache_misses' not in kwargs:
            kwargs['cache_misses'] = self._cache_misses
        if 'database_default_func' not in kwargs:
            kwargs['database_default_func'] = self._database_default_func
        if 'read_pool_size' not in kwargs:
            kwargs['read_pool_size'] = self._read_pool_size
        if 'immutable_vals' not in kwargs:
            kwargs['immutable_vals'] = self._immutable_vals
        if 'stringify_keys' not in kwargs:
            kwargs['stringify_keys'] = self.stringify_keys
        if 'value_converter' not in kwargs:
            kwargs['value_converter'] = self.value_converter

    def _reinit(self, **kwargs):
        self._add_init_kwargs(kwargs)

        # If we're not overwritten, pass this
        kwargs['database'] = self._database

        # Call __init__ again
        self.close()
        self.__init__(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):
        self.close()

    def _check_cache_size(self):
        if self._cur_size > self.cache_size:
            if self.read_only:
                self.drop_cache()
            else:
                self.sync_cache()

    def get_cache(self):
        '''
        Gets the cache as a stand-alone object -- updates
        directly to this cache will not be reflected/registered 
        with the core database.
        '''
        return self._cache

    def _get_item_from_database(self, key):
        return self._database.__getitem__(key)

    def _get_item_from_cache(self, key):
        return self._cache.__getitem__(key)

    def __getitem__(self, key):
        '''
        Checks cache for entry, then database for entry.
        '''
        val = None
        if key != None and self.stringify_keys:
            key = str(key)
        try:
            val = self._get_item_from_cache(key)
        except KeyError:
            try:
                val = self._get_item_from_database(key)
            except KeyError: pass
            if val != None or self._cache_misses:
                self._insert_cache(key, val, True)
                self._check_cache_size()
        if val == None: 
            if self._database_default_func:
                val = self._database_default_func()
            else:
                raise KeyError(key)
        return val

    def __iter__(self):
        self._sync_writes()
        return self._database.__iter__()

    def _insert_cache(self, key, val, read):
        '''
        Does an insert into the cache such that the cache
        will have an updated entry for the key,value,read
        tuple. Any changes to those values will both update
        the local cache and queue any required writes to the
        database.
        '''
        if key != None and self.stringify_keys:
            key = str(key)
        cval = self._cache.get(key)
        if cval == None:
            self._cur_size += 1
        if cval == None or val != cval:
            self._cache[key] = val
            # Force a write if it's a write or if it's
            # unclear that the item was modified
            if not self.read_only and (not self._immutable_vals or not read):
                self._wqueue.add(key)

    def __len__(self):
        '''
        This might take a very long time if the db doesn't
        have a good __len__ implementation.
        '''
        # Need to sync before we know our true size
        self._sync_writes()
        return len(self._database)

    def __contains__(self, key):
        '''
        Checks cache for entry, then database for entry.
        '''
        if key != None and self.stringify_keys:
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
            if val != None or self._cache_misses:
                self._insert_cache(key, val, True)
            self._check_cache_size()
        return cont

    def __setitem__(self, key, val):
        if val == None:
            raise AttributeError("Attempted to set a key value to None")
        if self.read_only:
            raise AttributeError("Attempted to set in read_only mode")
        if key != None and self.stringify_keys:
            key = str(key)
        self._insert_cache(key, val, False)
        self._check_cache_size()

    def __delitem__(self, key):
        '''
        Deletes from both the cache, write queues and the database
        ''' 
        if self.read_only:
            raise AttributeError("Attempted to delete in read_only mode")
        if key != None and self.stringify_keys:
            key = str(key)

        if self._cache_misses:
            self._insert_cache(key, None, True)
        elif key in self._cache:
            del self._cache[key]
        if key in self._wqueue:
            self._wqueue.discard(key)
        # We don't know if the database has this item or not
        if key in self._database:
            self._database.__delitem__(key)

    def _sync_writes(self):
        '''
        Flushes the write queue
        '''
        for key in self._wqueue:
            val = self._cache[key]
            self._database[key] = val
        del self._wqueue
        self._wqueue = set()
        self._database.sync()

    def sync_cache(self):
        '''
        Flushes the write queue to the database.
        '''
        self._sync_writes()
        self.drop_cache()

    def drop_cache(self):
        '''
        Drops all changes in the cache.
        '''
        del self._cache
        self._cache  = {}
        del self._wqueue
        self._wqueue = set()
        self._cur_size = 0

    def close(self, **kwargs):
        if not self.closed:
            self.sync_cache()
            # This will barf if the database doesn't have a close operator,
            # so check for close first
            if hasattr(self._database, 'close'):
                self._database.close(**kwargs)
        self.closed = True

    def __del__(self):
        # Close if we're being collected
        self.close()

class UnorderedCachedSet(collections.MutableSet, UnorderedCachedDict):
    '''
    Acts much like an UnorderedCachedDict except it stores key existence
    instead of key value pairs. Thus the data is still stored in the
    database as a dictionary, but treated as a set on the external
    interface.
    '''
    def __init__(self, database, cache_size, read_only=False, cache_misses=True, 
                 immutable_vals=False, stringify_keys=False, read_pool_size=0, **kwargs):
        UnorderedCachedDict.__init__(self, database, cache_size=cache_size, 
                                     cache_misses=cache_misses, read_only=read_only, 
                                     immutable_vals=immutable_vals, read_pool_size=read_pool_size, 
                                     stringify_keys=stringify_keys, **kwargs)

    def _dict_set(self, key, val):
        '''
        These allow for direct access to the dictionary holding
        the set under a different naming convention (to prevent
        dictionary like syntax from working on external interface).
        '''
        # Call UnorderedCachedDict's version of setitem since we've disabled it
        # No need to check stringify_keys, as it will be checked in the next setitem
        UnorderedCachedDict.__setitem__(self, key, val)

    def _dict_get(self, key):
        # Call UnorderedCachedDict's version of setitem since we've disabled it
        # No need to check stringify_keys, as it will be checked in the next setitem
        return UnorderedCachedDict.__getitem__(self, key)

    def add(self, elem):
        self._dict_set(elem, True)

    def discard(self, elem):
        self.__delitem__(elem)

    def __getitem__(self, elem):
        raise AttributeError( "'Set' object has no attribute '__getitem__'" )

    def __setitem__(self, key, val):
        raise AttributeError( "'Set' object has no attribute '__setitem__'" )

    def update(self, *args, **kwargs):
        '''
        Updates the set to include all arguments passed in. If the keyword 
        argument preprocess is passed, then each element is preprocessed 
        before being added.
        '''
        preprocess = kwargs.get('preprocess')
        for s in args:
            for e in s:
                self._dict_set(preprocess(e) if preprocess else e, True)

class MemDict(collections.MutableMapping):
    '''
    This is a standard dictionary, with some additional functions
    for syntax compatability with other DB wrappers. This is slower
    than a normal dictionary and should only be used to keep syntax
    standardized among several databases
    '''
    # Careful with changing __init__ params and forgetting them in _reinit
    def __init__(self, db_name, read_only=False, database_default_func=None, 
                 stringify_keys=False, **kwargs):
        self._db_name = db_name
        self.read_only = read_only
        self.stringify_keys = stringify_keys
        self._database_default_func = database_default_func
        self._database = {}
        self._reset_database()

    def _add_init_kwargs(self, kwargs):
        # These can be changed by caller
        if 'read_only' not in kwargs:
            kwargs['read_only'] = self.read_only
        if 'stringify_keys' not in kwargs:
            kwargs['stringify_keys'] = self.stringify_keys
        if 'database_default_func' not in kwargs:
            kwargs['database_default_func'] = self._database_default_func

        # This stays the same
        kwargs['db_name'] = self._db_name

    def _reinit(self, **kwargs):
        self._add_init_kwargs(kwargs)

        # Call __init__ again
        self.close()
        self.__init__(**kwargs)

    def _reset_database(self):
        del self._database
        self._database = {}

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):
        self.close()

    def get_cache(self):
        return self._database

    def __getitem__(self, key):
        if key != None and self.stringify_keys:
            key = str(key)
        try:
            return self._database.__getitem__(key)
        except KeyError: 
            if self._database_default_func != None:
                return self._database_default_func()
            else:
                raise

    def __iter__(self):
        return self._database.__iter__()

    def __len__(self):
        return self._database.__len__()

    def __contains__(self, key):
        if key != None and self.stringify_keys:
            key = str(key)
        return self._database.__contains__(key)

    def __setitem__(self, key, val):
        if self.read_only:
            raise AttributeError("Attempted to set in read_only mode")
        if key != None and self.stringify_keys:
            key = str(key)
        self._database.__setitem__(key, val)

    def __delitem__(self, key):
        if self.read_only:
            raise AttributeError("Attempted to delete in read_only mode")
        if key != None and self.stringify_keys:
            key = str(key)
        self._database.__delitem__(key)

    def _sync_writes(self):
        pass # No-op

    def sync_cache(self):
        pass # No-op

    def drop_cache(self):
        pass # No-op

    def close(self, **kwargs):
        self._reset_database()

    def reopen(self, read_only=None, **kwargs):
        self.read_only = read_only if read_only != None else self.read_only
        if 'database_default_func' in kwargs:
            self._database_default_func = kwargs['database_default_func']
        if 'stringify_keys' in kwargs:
            self.stringify_keys = kwargs['stringify_keys']
        # No need to re-initialize -- it's already in memory

    def clear(self, read_only=None, **kwargs):
        # Careful with changing __init__ params and forgetting them here...
        if read_only != None:
            kwargs['read_only'] = read_only
        self._reinit(**kwargs)

    def __del__(self):
        # Close if we're being collected
        self.close()

class SplitDbDict(collections.MutableMapping):
    '''
    Defines a way to split data among any number of arbitrary databases.
    All arguments in kwargs are applied to each database constructor.
    
    The default database class is base_db_class, while key specific classes
    can be defined in keyed_classes as a dictionary input. These overwrite
    the default db_class.
    
    If the split_func gives an invalid key name, a KeyError will be raised,
    so make sure updates to split_keys also updates split_func.
    
    If a cache_size if passed through kwargs, it is evenly divided among all
    databases.
    '''
    def __init__(self, db_name, base_db_class, split_keys, split_func, 
                 keyed_classes=None, stringify_keys=False, **kwargs):
        self.stringify_keys = stringify_keys
        self.split_keys = split_keys
        self.split_func = split_func

        self._db_name = db_name
        self._keyed_db = {}
        self._base_db_class = base_db_class
        self._keyed_classes = keyed_classes if keyed_classes else {}
        # Force caches to be split evenly among all databases
        self.check_update_cache_set(len(self.split_keys), kwargs)
        for skey in self.split_keys:
            if self._keyed_classes and skey in self._keyed_classes:
                db_class = self._keyed_classes[skey]
            else:
                db_class = self._base_db_class
            self._keyed_db[skey] = db_class(self._db_name+'_'+str(skey), **kwargs)

    def check_update_cache_set(self, numKeys, kwargs):
        if "cache_size" in kwargs:
            kwargs["cache_size"] /= numKeys

    def reopen(self, **kwargs):
        # Force caches to be split evenly among all databases
        self.check_update_cache_set(len(self.split_keys), kwargs)
        for db in self._keyed_db.values():
            if hasattr(db, 'reopen'):
                db.reopen(**kwargs)

    def clear(self, **kwargs):
        # Force caches to be split evenly among all databases
        self.check_update_cache_set(len(self.split_keys), kwargs)
        for db in self._keyed_db.values():
            if hasattr(db, 'clear'):
                db.clear(**kwargs)

    def close(self, **kwargs):
        for db in self._keyed_db.values():
            if hasattr(db, 'close'):
                db.close(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):
        self.close()

    def get_cache(self):
        cahces = {}
        for shortkey, db in self._keyed_db.items():
            cahces[shortkey] = db.get_cache()
        return cahces

    def __getitem__(self, key):
        if key != None and self.stringify_keys:
            key = str(key)
        db = self._keyed_db[self.split_func(key)]
        return db.__getitem__(key)

    def __iter__(self):
        '''
        The iterator for this class wraps the iterators for
        all stored DBs and throws the usual StopIteration()
        exception when all iterators have been exhausted.
        '''
        class MultiIter(object):
            def __init__(self, iterables):
                self.iterables = [iter.__iter__() for iter in iterables]
                self.cur_iter = None

            def __iter__(self):
                return self

            def next(self):
                if self.cur_iter == None:
                    # If we're out of iterables, then StopIteration
                    try:
                        self.cur_iter = self.iterables.pop()
                    except IndexError:
                        raise StopIteration()
                try:
                    return self.cur_iter.next()
                except StopIteration:
                    # Clear out the iterator and call next
                    self.cur_iter = None
                    return self.next()

        return MultiIter(self._keyed_db.values())

    def __len__(self):
        totlen = 0
        for db in self._keyed_db.values():
            totlen += db.__len__()
        return totlen

    def __contains__(self, key):
        if key != None and self.stringify_keys:
            key = str(key)
        db = self._keyed_db[self.split_func(key)]
        return db.__contains__(key)

    def __setitem__(self, key, val):
        if key != None and self.stringify_keys:
            key = str(key)
        db = self._keyed_db[self.split_func(key)]
        db.__setitem__(key, val)

    def __delitem__(self, key):
        if key != None and self.stringify_keys:
            key = str(key)
        db = self._keyed_db[self.split_func(key)]
        db.__delitem__(key)

    def _sync_writes(self):
        for db in self._keyed_db.values():
            db._sync_writes()

    def sync_cache(self):
        for db in self._keyed_db.values():
            db.sync_cache()

    def drop_cache(self):
        for db in self._keyed_db.values():
            db.drop_cache()

    def __del__(self):
        # Close if we're being collected
        self.close()

class SplitDbSet(collections.MutableSet, SplitDbDict):
    '''
    Defines a way to split data among any number of arbitrary databases.
    All arguments in kwargs are applied to each database constructor.
    
    The default database class is base_db_class, while key specific classes
    can be defined in keyed_classes as a dictionary input. These overwrite
    the default db_class.
    
    If the split_func gives an invalid key name, a KeyError will be raised,
    so make sure updates to split_keys also updates split_func.
    
    If a cache_size if passed through kwargs, it is evenly divided among all
    databases.
    '''
    def __init__(self, db_name, base_db_class, split_keys, split_func, 
                 keyed_classes=None, stringify_keys=False, **kwargs):
        self.stringify_keys = stringify_keys
        self.split_keys = split_keys
        self.split_func = split_func

        self._db_name = db_name
        self._keyed_db = {}
        self._base_db_class = base_db_class
        self._keyed_classes = keyed_classes if keyed_classes else {}
        # Force caches to be split evenly among all databases
        if "cache_size" in kwargs:
            kwargs["cache_size"] /= len(self.split_keys)
        for skey in self.split_keys:
            if self._keyed_classes and skey in self._keyed_classes:
                db_class = self._keyed_classes[skey]
            else:
                db_class = self._base_db_class
            self._keyed_db[skey] = db_class(self._db_name+'_'+str(skey), **kwargs)

    def _dict_set(self, key, val):
        '''
        These allow for direct access to the dictionary holding
        the set under a different naming convention (to prevent
        dictionary like syntax from working on external interface).
        '''
        if key != None and self.stringify_keys:
            key = str(key)
        db = self._keyed_db[self.split_func(key)]
        db._dict_set(key, val)

    def _dict_get(self, key):
        if key != None and self.stringify_keys:
            key = str(key)
        db = self._keyed_db[self.split_func(key)]
        return db._dict_get(key)

    def add(self, elem):
        self._dict_set(elem, True)

    def discard(self, elem):
        self.__delitem__(elem)

    def __getitem__(self, elem):
        raise AttributeError( "'Set' object has no attribute '__getitem__'" )

    def __setitem__(self, key, val):
        raise AttributeError( "'Set' object has no attribute '__setitem__'" )

    def update(self, *args, **kwargs):
        '''
        Updates the set to include all arguments passed in.
        If the keyword argument preprocess is passed, then
        each element is preprocessed before being added.
        '''
        preprocess = kwargs.get('preprocess')
        for s in args:
            for e in s:
                self._dict_set(preprocess(e) if preprocess else e, True)
