import os
import shutil
from setuptools import setup

def read(fname):
    with open(fname) as fhandle:
        return fhandle.read()

def readMD(fname):
    # Utility function to read the README file.
    full_fname = os.path.join(os.path.dirname(__file__), fname)
    if 'PANDOC_PATH' in os.environ:
        import pandoc
        pandoc.core.PANDOC_PATH = os.environ['PANDOC_PATH']
        doc = pandoc.Document()
        with open(full_fname) as fhandle:
            doc.markdown = fhandle.read()
        return doc.rst
    else:
        return read(fname)

required = [req.strip() for req in read('requirements.txt').splitlines() if req.strip()]

setup(
    name='PyDataWrap',
    version='1.2.2',
    author='Matthew Seal',
    author_email='mseal@opengov.com',
    description='Tools for wrapping data and manipulating it in efficient ways',
    long_description=readMD('README.md'),
    install_requires=required,
    license='LGPL 2.1',
    packages=['datawrap'],
    test_suite='tests',
    zip_safe=False,
    url='https://github.com/OpenGov/python_data_wrap',
    download_url='https://github.com/OpenGov/python_data_wrap/tarball/v1.2.1',
    keywords=['tables', 'data', 'databases', 'dictionary', 'filedb'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'Topic :: Database :: Front-Ends',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2 :: Only'
    ]
)
