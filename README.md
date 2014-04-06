# PyDataWrap
Python Wrappers on Data Structures and abstractions over persistent
data stores.

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
* allset
* xlrd (for excel files in tableloader.py)
* redis (for RedisDB wrappers)

## Setup
### Installation
From source:

    python settup.py install

From pip:

    pip install pydatawrap

## Features
* File based dictionaries and sets
* Persistent file based objects
* 2D table loading/saving
* Table wrappers to transpose and transform data
* List wrapping for sublist selection (without copying)

## Navigating the Repo
### datawrap
The implementation files for the repository.

### tests
All unit tests for the repo.

## Language Preferences
* Google Style Guide
* Object Oriented (with a few exceptions)

## TODO
* Add tests for fileloader and savable

## Author
Author(s): Matthew Seal

Collaborator(s): Joe Maguire, Loren Abrams

&copy; Copyright 2013, [OpenGov](http://opengov.com)