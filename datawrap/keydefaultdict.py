import collections

class keydefaultdict(collections.defaultdict):
    '''
    Provides a default dictionary which lets the default value be
    based on the key input.
    
    keydict = keydefaultdict(lambda key: key)
    
    Idea taken from stack overflow and cleaned up.
    
    @author Matt Seal
    '''
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        default = self[key] = self.default_factory(key)
        return default
