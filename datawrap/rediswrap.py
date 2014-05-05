import collections

from redis import StrictRedis

DEFAULT_BATCH_SIZE = 1024

# TODO Eventually extend the RedisCacheDict from UnorderedCacheDict
# TODO add cache dropping
class RedisCacheDict(StrictRedis, collections.MutableMapping):
    '''
    This class provides an in-memory ache wrapper on top of an `StrictRedis`
    redis connection.  The wrapper can be intefaced with similar to a Python
    dictionary as `__getitem__`, `__setitem__`, `__delitem__` and `__contains__`
    are implemented.  Some notable functionality not available in this wrapper
    is support for iteration and implementation of the `__len__` magic method.

    The cache functions as follows:
        - If a key is requested that isn't present in the local in-memory cache
          then the key is immediately fetched from Redis.
        - If a key is requested that already exists in cache, the cached version
          is returned.
        - A value set at a key sets *only* to cache, replacing whatever
          previously existed at that key in cache.
        - When `sync_cache` is called, any writes to the wrapper that exist in
          cache and have yet to be pushed to Redis are pushed in batch.

    In addition to raw key/value storage, this wrapper facilitates accessing
    Redis hashes.  To reference a Redis hash entry, index the wrapper with a
    2-tuple key.  As an example, the following sets the value `lorem` at key
    `bar` in the Redis hash existing at `foo` in Redis database `12`:

    
    ```
    redis_wrapper = RedisCacheDict(db=12)
    redis_wrapper[('foo', 'bar')] = 'lorem'
    ```

    The class can be instantiated with `redis-py`'s `StrictRedis` named
    connection parameters; the most common of these parameters being:
        - `db`: an *integer* index of the database to bind to
        - `host`: host of the Redis server (defaults to `localhost`)
        - `port`: port of the Redis server (defaults to `6379`)
    '''
    def __init__(self, value_converter=None, *args, **kwargs):
        self._cache = {}
        self._dirty_keys = set()
        self.converter = value_converter

        StrictRedis.__init__(self, *args, **kwargs)

    def __getitem__(self, key):
        x_key, y_key = self.explode_key(key)
        try:
            val = self._cache[x_key]
            val = val.get(y_key) if y_key else val
        except KeyError:
            if y_key:
                val = self.hgetall(x_key)
                self._cache[x_key] = val
                val = val.get(y_key)
            else:
                val = self.get(x_key)
                self._cache[x_key] = val
        return self.converter(val) if self.converter else val

    def __setitem__(self, key, value):
        x_key, y_key = self.explode_key(key)
        if y_key:
            try:
                d = self._cache[x_key]
                d[y_key] = value
            except KeyError:
                self._cache[x_key] = { y_key: value }
        else:
            self._cache[x_key] = value
        self._dirty_keys.add(key)

    def __delitem__(self, key):
        '''Note that deleting first syncs all queued writes'''
        self.sync()

        x_key, y_key = self.explode_key(key)
        if y_key:
            try:
                del self._cache[x_key][y_key]
            except KeyError:
                pass
            self.hdel(x_key, y_key)
        else:
            try:
                del self._cache[x_key]
            except KeyError:
                pass
            self.delete(x_key)

    def __contains__(self, key):
        return self[key] is not None

    def __len__(self):
        raise NotImplementedError('Not straight forward means of acquiring Redis DB length given the hash abstraction')

    def __iter__(self):
        raise NotImplementedError('Redis does not supply a cursor for iteration')

    def __bool__(self):
        return True # Always return truey because we can't determine length
    __nonzero__ = __bool__

    @property
    def num_queued_writes(self):
        return len(self._dirty_keys)

    def sync_cache(self, batch_size=DEFAULT_BATCH_SIZE):
        with self.pipeline() as pipeline:
            for i, key in enumerate(self._dirty_keys):
                x_key, y_key = self.explode_key(key)

                if y_key:
                    pipeline.hset(x_key, y_key, self._cache[x_key][y_key])
                else:
                    pipeline.set(x_key, self._cache[x_key])

                if i and i % batch_size == 0:
                    pipeline.execute()
            pipeline.execute()
        self._dirty_keys = set()

    @staticmethod
    def explode_key(key):
        if isinstance(key, basestring):
            return key, None

        try:
            if len(key) != 2:
                raise KeyError('Tuple keys must be length 2')
            return key[0], key[1]
        except TypeError:
            raise KeyError('Key is neither a string nor a tuple-like object')

    def close(self, flushdb=False, **kwargs):
        if flushdb:
            self.flushdb()
        # Connections are pooled internally by redis-py
