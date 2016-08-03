#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os.path
import logging
from libscifig.task import GnuplotTask, TikzTask


#TODO : recursive glob: https://docs.python.org/3.5/library/glob.html
import os
import fnmatch
def _recursive_glob(base, ext):
    """
    Helper function to find files with extention ext
    in the path base.
    """
    return [os.path.join(dirpath, f)
        for dirpath, dirnames, files in os.walk(base)
        for f in fnmatch.filter(files, '*' + ext)]


def detect_datafile(plt, root):
    """
    Detect datafiles associated with a plt file.

    :param plt: plt filepath
    :param root: root filepath
    :returns: list of filepath starting at root
    """
    base = os.path.split(plt)[0]
    datafiles = []
    for ext in ('csv', '.res', '.dat', '.txt', '.png', '.jpg'):
        files = _recursive_glob(base, ext)
        files = [os.path.relpath(f, root) for f in files]
        datafiles.extend(files)
    logging.debug('In %s', base)
    logging.debug('Detected datafiles: %s', datafiles)
    return datafiles


def detect_tikzsnippets(plt):
    """
    Detect tikzsnippets associated with a plt file.

    :param plt: plt filepath
    :returns: tuple of 2 booleans
    """
    base = os.path.splitext(plt)[0] + '.tikzsnippet'
    snippets = [os.path.isfile(base),
                os.path.isfile(base + '1'),
                os.path.isfile(base + '2'),]
    logging.debug('In %s', base)
    logging.debug('Detected tikzsnippets: %s', snippets)
    return snippets


def detect_task(directory, root_path):
    """
    Detect the task to do depending on file extensions.

    :param directory: directory to look at
    :returns: list of tasks
    """
    plt_files = glob.glob(os.path.join(directory, '*.plt'))
    tikz_files = glob.glob(os.path.join(directory, '*.tikz'))
    tasks = []
    for plt_file in plt_files:
        data = detect_datafile(plt_file, root_path)
        snippet, snippet1, snippet2 = detect_tikzsnippets(plt_file)
        tasks.append(GnuplotTask(plt_file,
                                 datafiles=data,
                                 tikzsnippet=snippet,
                                 tikzsnippet1=snippet1,
                                 tikzsnippet2=snippet2,
                                 ))
    for tikz_file in tikz_files:
        data = detect_datafile(tikz_file, root_path)
        tasks.append(TikzTask(tikz_file,
                              datafiles=data,
                              ))
    return tasks
