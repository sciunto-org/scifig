#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os.path
import logging
from libscifig.task import GnuplotTask, TikzTask


#TODO : recursive glob: https://docs.python.org/3.5/library/glob.html

def detect_datafile(plt, root):
    """
    Detect datafiles associated with a plt file.

    :param plt: plt filepath
    :param root: root filepath
    :returns: list
    """
    base = os.path.split(plt)[0]
    datafiles = []
    for ext in ('.dat', '.txt', '.png', '.jpg'):
        files = glob.glob(os.path.join(base, '**' + ext))
        files = [os.path.relpath(f, root) for f in files]
        datafiles.extend(files)
    logging.debug('In %s' % base)
    logging.debug('Detected datafiles: %s' % datafiles)
    return datafiles


def detect_tikzsnippets(plt):
    """
    Detect tikzsnippets associated with a plt file.

    :param plt: plt filepath
    :returns: tuple of 2 booleans
    """
    base = os.path.splitext(plt)[0] + '.tikzsnippet'
    return (os.path.isfile(base + '1'), os.path.isfile(base + '2'))


def detect_task(directory, root_path):
    """
    Detect the task to do depending on file extensions.

    :param directory: directory to look at
    :returns: list of tasks
    """
    plt_files = glob.glob(os.path.join(directory, '*.plt'))
    tikz_files = glob.glob(os.path.join(directory, '*.tikz'))
    db_path = os.path.join(root_path, 'db.db')
    tasks = []
    for plt_file in plt_files:
        data = detect_datafile(plt_file, root_path)
        snippet1, snippet2 = detect_tikzsnippets(plt_file)
        tasks.append(GnuplotTask(plt_file,
                                 datafiles=data,
                                 tikzsnippet1=snippet1,
                                 tikzsnippet2=snippet2,
                                 db=db_path,
                                 ))
    for tikz_file in tikz_files:
        data = detect_datafile(tikz_file, root_path)
        tasks.append(TikzTask(tikz_file,
                                 datafiles=data,
                                 db=db_path,
                                 ))
    return tasks
