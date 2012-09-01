# PyDataWrap

Python Wrappers on Databases and Datatypes/Data Structures

## Description
This module is a home for Python wrappers of data, databases and
datastructures. It defines common use wrapping that can treat one
style of data as another or reorder/subselect a collection.

The filedbwrap file defines many file based database objects such as
dictionaries and sets which are treated as memory objects in Python
but have a very large capacity with limited memory footprint.

The savable file defines object persistence objects which save state
when they deconstruct and reload that state upon initialization.

The listwrap file defines a no-copy list subset selector that can
retrieve subsets of data to be treated as complete, contiguous lists.

There are also some file loading/saving modules for various formats.

## Dependencies
* xlrd (for old excel files in tableloader.py)
* openpyxl (for new excel files in tableloader.py)
* bsddb (speeds up filedbwrap; don't use this addition for production code -- requires very expensive oracle license)

### Dependency Installation
Download xlrd from http://pypi.python.org/pypi/xlrd

    cd <xlrd directory>
    [sudo] python setup.py install

Download hjunes-openpyxl (python version fixes) from https://bitbucket.org/hjunes/openpyxl/downloads

    cd <openpyxl directory>
    [sudo] python setup.py install

## Setup
### Installation instructions
Once the dependencies are resolved the package requires no other installation
processes.

## Features
* File based dictionaries and sets
* Persistent file based objects
* 2D table loading/saving
* Table wrappers to transpose and transform data
* List wrapping for sublist selection (without copying)

## Navigating the Repo
### testing
All unit tests for the repo.  

## Language Preferences
* Camel Case
* Object Oriented (with a few exceptions)

## TODO
Add tests for fileloader and savable

## Author
Author(s): Matthew Seal

Collaborator(s): Joe Maguire

#### (C) Copyright 2012, [Delphi Solutions](http://Delphi.us)