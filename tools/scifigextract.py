#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# Author: Francois Boulogne <devel at sciunto dot org>, 2012-2016

import logging
import argparse
import re

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
steam_handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
steam_handler.setFormatter(formatter)
logger.addHandler(steam_handler)


def get_graphics_paths(texfilepath, uniquify=False):
    """
    Parse tex files and returns filepaths in \includegraphics{} latex
    functions.

    :param texfilepath: filepath for the texfile to parse
    :param uniquify: uniquify the list
    """
    graphic_names = []
    logger.debug('Read %s', texfilepath)
    with open(texfilepath, 'r') as tex:
        for line in tex.readlines():
            graphics = re.findall('\includegraphics(\[.*?\]|){([a-zA-Z0-9\.\-_/]*)}', line)
            if graphics != []:
                logger.debug('regexp result: %s', graphics)

            for graphic in graphics:
                graphic_names.append(graphic[1])
    if uniquify:
        return list(set(graphic_names))
    return graphic_names


if __name__ == '__main__':
    description = 'Extract path from includegraphics in tex files'
    epilog = ''

    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog)

    parser.add_argument('-d', '--debug', help='Activate debug logger', default=0, action='count')
    parser.add_argument('-v', '--verbose', help='Activate verbose logger', default=0, action='count')
    #parser.add_argument('-V', '--version', help='Print version and quit', default=0, action='count')

    subparsers = parser.add_subparsers(title='commands')

    # scifigselect list
    list_parser = subparsers.add_parser('list', help='Extract paths and list')
    list_parser.add_argument('tex', help='Name') # multiple files?
    list_parser.set_defaults(action='list')

    args = parser.parse_args()

    # Options
    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)

    logger.debug('Arguments: %s' %args)

    #TODO
    #if args.version:
    #    print(__version__)
    #    sys.exit(0)

    try:
        if args.action == 'list':
            graphics = get_graphics_paths(args.tex)
            for graphic in graphics:
                print(graphic)
    except AttributeError:
        logger.error('Missing action')
        parser.print_help()
