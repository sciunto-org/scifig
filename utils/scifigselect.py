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

import argparse
import re
import os.path
import shutil


def get_graphics(texfilehandler, directory):
    """
    Parse tex files and returns graphic names

    texfilehandler: filehandler .tex
    """
    graphic_names = []
    for line in texfilehandler.readlines():
        graphics = re.findall('includegraphics(\[.*?\]|){' +
                              directory +
                              '/([a-zA-Z0-9\.\-_]*)}', line)
        for graphic in graphics:
            graphic_names.append(graphic[1])
    return graphic_names


if __name__ == '__main__':
    description = 'Make a proper fig directory'
    epilog = 'All figures like \includegraphics{fig/figure.pdf} will be copied in the output `fig`.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog)
    parser.add_argument('figures', help='Directory containing figures', metavar='DIR')
    parser.add_argument('texfile', help='TeX file', metavar='FILE')
    parser.add_argument('output', help='Output directory', metavar='OUTPUT')

    args = parser.parse_args()

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    with open(args.texfile, 'r') as tex:
        graphics = get_graphics(tex, args.output)
        for graphic in graphics:
            source = os.path.join(args.figures, graphic)
            if os.path.isfile(source):
                shutil.copy2(source, args.output)
            else:
                print('%s does not exist.' % source)
