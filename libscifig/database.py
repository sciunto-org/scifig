#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os.path
import hashlib
try:
    import cPickle as pickle
except:
    import pickle

def _calculate_checksum(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()


def check_modification(name, dependencies, db_path):
    """
    Check if at least one dependency changed.

    :param name: name of the figure
    :param dependencies: list of dependencies
    :param db_path: path of the database
    :returns: boolean
    """
    logging.debug('Check modification for %s' % name)
    if not os.path.isfile(db_path):
        logging.debug('No db, modif is True')
        return True
    cur_signature = {}
    for dep in dependencies:
        cur_signature[dep] = _calculate_checksum(dep)
    with open(db_path, 'rb') as fh:
        db = pickle.load(fh)
        db = db.get(name)
        if db is None:
            logging.debug('name unknown in db, modif is True')
            return True
        for dep, md5 in cur_signature.items():
            value = db.get(dep)
            if value is None or value != md5:
                logging.debug('value of %s is None or does not match, modif is True' % dep)
                return True
    return False


def store_checksum(name, dependencies, db_path):
    """
    Store the checksum in the db.

    :param name: name of the figure
    :param dependencies: list of dependencies
    :param db_path: path of the database
    """
    logging.debug('Store checksums in db')
    # Calculate md5 sums
    cur_signature = {}
    for dep in dependencies:
        cur_signature[dep] = _calculate_checksum(dep)
    try:
        with open(db_path, 'rb') as fh:
            db = pickle.load(fh)
    except FileNotFoundError:
        db = {}
    # Merge dict
    db[name] = cur_signature
    with open(db_path, 'wb') as fh:
        pickle.dump(db, fh)


def erase_db(db_path):
    """
    Erase a database.

    :param db_path: path of the database
    """
    logging.debug('Erase db')
    with open(db_path, 'wb') as fh:
        pickle.dump({}, fh)
