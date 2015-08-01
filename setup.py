#!/usr/bin/env python

from distutils.core import setup
import libscifig

setup(
    name         = 'scifig',
    version      = libscifig.__version__,
    #url          = info.URL,
    author       = "Francois Boulogne",
    #license      = info.LICENSE,
    #author_email = info.EMAIL,
    #description  = info.SHORT_DESCRIPTION,
    scripts      = ['example/scifig.py'],
    packages     = ['libscifig'],
)
