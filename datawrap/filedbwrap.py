import os, shelve
from basewrap import (
    MemDict,
    UnorderedCachedDict,
    UnorderedCachedSet,
    SplitDbDict,
    SplitDbSet)

def get_default_file_ext():
    '''
    Helper function for all file wrappers to identify
    standard extension.
    '''
    return 'fd'

class MemFromFileDict(MemDict):
    '''
    This wraps a standard dictionary with a file persistence that
    allows the dictionary to be reloaded and/or saved upon closing.
    '''   
    # Careful with changing __init__ params and forgetting them in _reinit
    def __init__(self, db_name, db_ext=None, read_only=False, database_default_func=None, 
                 clear=False, stringify_keys=False, **kwargs):
        MemDict.__init__(self, db_name, read_only=read_only, 
                         stringify_keys=stringify_keys, 
                         database_default_func=database_default_func, 
                         **kwargs)
        self._db_ext = db_ext if db_ext != None else get_default_file_ext()
        abs_dir_path = os.path.dirname(os.path.abspath(db_name))
        dir_present = os.path.exists(abs_dir_path)
        if not dir_present:
            try: os.makedirs(abs_dir_path)
            except OSError: pass
        self._db_full_path = '.'.join((os.path.abspath(db_name), self._db_ext))
        file_present = os.path.exists(self._db_full_path)
        self.flag = 'n' if clear else 'r' if read_only and file_present else 'c'
        self.closed = False
        self._db_file = shelve.open(self._db_full_path, flag=self.flag)
        if not clear:
            # Copy all elements into memory dict
            for key in self._db_file:
                self._database[key] = self._db_file[key]
        # We're done with the file for now
        self._db_file.close()

    def _add_init_kwargs(self, kwargs):
        MemDict._add_init_kwargs(self, kwargs)

        kwargs['db_name'] = self._db_name
        kwargs['db_ext'] = self._db_ext

    def _reinit(self, **kwargs):
        self._add_init_kwargs(kwargs)
        self.close()
        self.__init__(**kwargs)

    def reopen(self, read_only=None, **kwargs):
        kwargs['read_only'] = read_only if read_only != None else self.read_only
        kwargs['clear'] = False
        self._reinit(**kwargs)

    def clear(self, read_only=None, **kwargs):
        kwargs['read_only'] = read_only if read_only != None else self.read_only
        kwargs['clear'] = True
        self._reinit(**kwargs)

    def close(self, delete_file=False, **kwargs):
        if delete_file:
            # Security vulnerability if file is accessible by 3rd party
            # as there is a time gap between closing and deleting
            try: os.remove(self._db_full_path)
            except: pass
        elif not self.closed:
            self.sync_cache()
        self._reset_database()
        self.closed = True

    def _sync_writes(self):
        if not self.read_only:
            self._db_file = shelve.open(self._db_full_path, flag='n')
            for key in self._database:
                self._db_file[key] = self._database[key]
            self._db_file.sync()
            # We're done with the file for now
            self._db_file.close()

    def sync_cache(self):
        self._sync_writes()
        self.drop_cache()

class FileDict(UnorderedCachedDict):
    '''
    Defines a dictionary based on a file, with an unordered memory cache. 
    The database is saved to file when the cache gets too large or it is 
    synced. This allows for very large databases to be stored in the 
    filesystem without consuming all available memory.
    '''
    # Careful with changing __init__ params and forgetting them in _reinit
    def __init__(self, db_name, db_ext=None, read_only=False, clear=False, cache_size=10*1024, 
                 immutable_vals=False, stringify_keys=False, cache_misses=True,
                 database_default_func=None, read_pool_size=0, **kwargs):
        self._db_name = db_name
        self._db_ext = db_ext if db_ext != None else get_default_file_ext()
        abs_dir_path = os.path.dirname(os.path.abspath(db_name))
        dir_present = os.path.exists(abs_dir_path)
        if not dir_present:
            try: os.makedirs(abs_dir_path)
            except OSError: pass
        self._db_full_path = '.'.join((os.path.abspath(db_name), self._db_ext))
        file_present = os.path.exists(self._db_full_path)
        self.flag = 'n' if clear else 'r' if read_only and file_present else 'c'
        self._database = shelve.open(self._db_full_path, flag=self.flag)
        self.closed = False
        UnorderedCachedDict.__init__(self, self._database, cache_size=cache_size, 
                                     database_default_func=database_default_func, read_only=read_only, 
                                     immutable_vals=immutable_vals, stringify_keys=stringify_keys,
                                     cache_misses=cache_misses, read_pool_size=read_pool_size, **kwargs)

    def _add_init_kwargs(self, kwargs):
        kwargs['db_name'] = self._db_name
        kwargs['db_ext'] = self._db_ext
        UnorderedCachedDict._add_init_kwargs(self, kwargs)

    def _reinit(self, **kwargs):
        self._add_init_kwargs(kwargs)
        self.close()
        self.__init__(**kwargs)

    def reopen(self, read_only=None, cache_size=None, **kwargs):
        if read_only != None:
            kwargs['read_only'] = read_only
        if cache_size != None:
            kwargs['cache_size'] = cache_size
        kwargs['clear'] = False
        self._reinit(**kwargs)

    def clear(self, read_only=None, cache_size=None, **kwargs):
        if read_only != None:
            kwargs['read_only'] = read_only
        if cache_size != None:
            kwargs['cache_size'] = cache_size
        kwargs['clear'] = True
        self._reinit(**kwargs)

    def close(self, delete_file=False, **kwargs):
        if delete_file:
            # Security vulnerability if file is accessible by 3rd party
            # as there is a time gap between closing and deleting
            if not self.closed:
                self._database.close()
            try: os.remove(self._db_full_path)
            except: pass
        elif not self.closed:
            self.sync_cache()
            self._database.close()
        self.closed = True

class FileSet(UnorderedCachedSet):
    '''
    Much like a FileDict, except treated as a Set instead.
    '''
    # Careful with changing __init__ params and forgetting them in reopen/clear
    def __init__(self, db_name, db_ext=None, read_only=False, clear=False, cache_size=10*1024, 
                 immutable_vals=False, stringify_keys=False, cache_misses=True, 
                 read_pool_size=0, **kwargs):
        self._db_name = db_name
        self._db_ext = db_ext if db_ext != None else get_default_file_ext()
        abs_dir_path = os.path.dirname(os.path.abspath(db_name))
        dir_present = os.path.exists(abs_dir_path)
        if not dir_present:
            try: os.makedirs(abs_dir_path)
            except OSError: pass
        self._db_full_path = '.'.join((os.path.abspath(db_name), self._db_ext))
        file_present = os.path.exists(self._db_full_path)
        self.flag = 'n' if clear else 'r' if read_only and file_present else 'c'
        self._database = shelve.open(self._db_full_path, flag=self.flag)
        self.closed = False
        UnorderedCachedSet.__init__(self, self._database, cache_size=cache_size, 
                                    read_only=read_only, immutable_vals=immutable_vals,
                                    stringify_keys=stringify_keys, 
                                    cache_misses=cache_misses, 
                                    read_pool_size=read_pool_size, **kwargs)

    def _add_init_kwargs(self, kwargs):
        kwargs['db_name'] = self._db_name
        kwargs['db_ext'] = self._db_ext
        UnorderedCachedSet._add_init_kwargs(self, kwargs)

    def _reinit(self, **kwargs):
        self._add_init_kwargs(kwargs)
        self.close()
        self.__init__(**kwargs)

    def reopen(self, read_only=None, cache_size=None, **kwargs):
        if read_only != None:
            kwargs['read_only'] = read_only
        if cache_size != None:
            kwargs['cache_size'] = cache_size
        kwargs['clear'] = False
        self._reinit(**kwargs)

    def clear(self, read_only=None, cache_size=None, **kwargs):
        if read_only != None:
            kwargs['read_only'] = read_only
        if cache_size != None:
            kwargs['cache_size'] = cache_size
        kwargs['clear'] = True
        self._reinit(**kwargs)

    def close(self, delete_file=False, **kwargs):
        if delete_file:
            # Security vulnerability if file is accessible by 3rd party
            # as there is a time gap between closing and deleting
            if not self.closed:
                self._database.close()
            try: os.remove(self._db_full_path)
            except: pass
        elif not self.closed:
            self.sync_cache()
            self._database.close()
        self.closed = True

class SplitFileDict(SplitDbDict):
    '''
    Defines a split DB (see SplitDbDict) based on separate files.
    This is useful if you have a large dictionary of words and want
    to store all words with the same first character together.
    '''
    def __init__(self, db_name, split_keys, split_func, db_ext=None, read_only=False, 
                 clear=False, cache_misses=True, cache_size=10*1024, immutable_vals=False, 
                 stringify_keys=False, database_default_func=None, **kwargs):
        SplitDbDict.__init__(self, db_name, FileDict, split_keys, split_func, db_ext=db_ext,
                             read_only=read_only, clear=clear, cache_size=cache_size,
                             immutable_vals=immutable_vals, stringify_keys=stringify_keys, 
                             database_default_func=database_default_func, 
                             cache_misses=cache_misses, **kwargs)

class SplitFileSet(SplitDbSet):
    '''
    Much like a SplitFileDict, except treated as a Set instead.
    '''
    def __init__(self, db_name, split_keys, split_func, db_ext=None, read_only=False, 
                 clear=False, cache_misses=True, cache_size=10*1024, immutable_vals=False, 
                 stringify_keys=False, **kwargs):
        SplitDbSet.__init__(self, db_name, FileSet, split_keys, split_func, db_ext=db_ext,
                            read_only=read_only, clear=clear, cache_size=cache_size,
                            immutable_vals=immutable_vals, stringify_keys=stringify_keys, 
                            cache_misses=cache_misses, **kwargs)

