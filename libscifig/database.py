#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

import json
import logging

class DataBase():
    """
    Custom class to manipulate a json database.

    :param db_path: filepath of the database.
    """
    def __init__(self, db_path):
        self.path = db_path

    def __enter__(self):
        try:
            with open(self.path, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}
        return self

    def __exit__(self, type, value, traceback):
        with open(self.path, 'w') as f:
            json.dump(self.data, f)

    def set(self, name, obj, content):
        """
        Set a content to a tree (name--object).

        :param name: ID of the element, like filepath
        :param obj: Content type (like deps, targets...)
        :param content: Content to store, a dict.
        """
        if not name in self.data.keys():
            self.data[name] = {obj: content}
        else:
            self.data[name][obj] = content

    def get(self, name, obj):
        """
        Get a content from a tree (name--object).

        :param name: ID of the element, like filepath
        :param obj: Content type (like deps, targets...)
        """
        try:
            d = self.data[name][obj]
        except KeyError:
            d = {}
        return d
