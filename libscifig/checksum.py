#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

import hashlib
import logging


def calculate_checksum(filepath):
    """
    Calculate the checksum of a file.

    :param filepath: file path
    :returns: string
    """
    hasher = hashlib.md5()
    with open(filepath, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()


def is_different(cur_hashes, db_hashes):
    """
    Check if at least one item changed.

    :param cur_hashes: current hashes
    :param db_hashes: previous hashes

    :returns: boolean
    """
    for dep, md5 in cur_hashes.items():
        try:
            value = db_hashes[dep]
        except KeyError:
            return True
        if value is None or value != md5:
            logging.debug('value of %s is None or does not match, modif is True', dep)
            return True
    return False
