import os
from setuptools import setup

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "PyDataWrap",
    version = "1.1.0",
    author = "Matthew Seal",
    author_email = "mseal@delphi.us",
    description = ("Tools for wrapping data and manipulating it in efficient ways"),
    install_requires=['xlrd','openpyxl'],
    packages=['datawrap'],
    long_description=read('README.md'),
)
