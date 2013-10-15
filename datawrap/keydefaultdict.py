import collections

class KeyDefaultDict(collections.defaultdict):
    '''
    Provides a default dictionary which lets the default value be
    based on the key input.
    
    keydict = KeyDefaultDict(lambda key: key)
    
    Idea taken from stack overflow and cleaned up/reorganized:
        http://stackoverflow.com/questions/2912231/is-there-a-clever-way-to-pass-the-key-to-defaultdicts-default-factory/2912455#2912455
    '''
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        default = self[key] = self.default_factory(key)
        return default
