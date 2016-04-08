#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError as ex:
    print('[python-bibtexparser] setuptools not found. Falling back to distutils.core')
    from distutils.core import setup
import libscifig

setup(
    name         = 'scifig',
    version      = libscifig.__version__,
    url          = "https://scifig.readthedocs.org",
    author       = "Francois Boulogne",
    license      = "GPLv3",
    author_email = "devel@sciunto.org",
    description  = "A build tool for (non?)-scientific figures",
    scripts      = ['example/scifig.py', 'tools/scifigextract.py'],
    packages     = ['libscifig'],
)
