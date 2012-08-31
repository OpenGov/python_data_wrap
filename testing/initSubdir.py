'''
Path hack to allow for child directory to know about parent
directory package requirements when the child is not part
of any package. This is useful when you call main from a 
child directory and want to have access to parent files --
like when testing in a test module on parent module files.

At the top of such a file do the following:

# Import this to be able to load parent directory modules
from initSubdir import checkSubdirPath; checkSubdirPath(__name__)

@param name Importer '__name__'
@author Matt Seal
'''
def checkSubdirPath(name):
    if name == "__main__" and __package__ is None:
        from sys import path
        from os.path import dirname, join, abspath
        path.append(abspath(join(dirname(__file__), '..')))
