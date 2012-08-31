# Path hack to allow for test scripts to be run as __main__
def checkSubdirPath(name):
    if name == "__main__" and __package__ is None:
        from sys import path
        from os.path import dirname, join, abspath
        path.append(abspath(join(dirname(__file__), '..')))
