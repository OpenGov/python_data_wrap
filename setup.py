import os
import shutil
from setuptools import setup

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Cleanup builds so changes don't persist into setup
build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'build'))
dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dist'))
if (os.path.isdir(build_dir)):
    shutil.rmtree(build_dir)
if (os.path.isdir(dist_dir)):
    shutil.rmtree(dist_dir)

setup(
    name = "PyDataWrap",
    version = "1.2.0",
    author = "Matthew Seal",
    author_email = "mseal@opengov.com",
    description = ("Tools for wrapping data and manipulating it in efficient ways"),
    install_requires=['redis', 'xlrd'],
    packages=['datawrap'],
    test_suite = 'tests',
    zip_safe = False,
    long_description=read('README.md'),
)
