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

import unittest
import tempfile

from scifigselect import get_graphics_paths

class test_get_graphics_paths(unittest.TestCase):

    def test_simple_include(self):
        #Prepare the tex file
        temp = tempfile.mkstemp()[1]
        with open(temp, 'w') as tmp:
            tex = """
            \includegraphics{foo.pdf}
            \includegraphics{fig/toto.pdf}
            \includegraphics[scale=2]{fig/tutu.eps}
            \includegraphics{fig/toto-12_AEe.pdf}

            """
            tmp.write(tex)

        expected = ['foo.pdf',
                    'fig/toto.pdf',
                    'fig/tutu.eps',
                    'fig/toto-12_AEe.pdf']

        with open(temp, 'r') as tmp:
            result = get_graphics_paths(temp)

        self.assertEqual(expected, result)

    def test_2_includes_per_line(self):
        #Prepare the tex file
        temp = tempfile.mkstemp()[1]
        with open(temp, 'w') as tmp:
            tex = """
            \includegraphics[scale=2]{fig/foo.eps}\includegraphics[scale=2]{fig/bar.eps}

            """
            tmp.write(tex)

        expected = ['fig/foo.eps', 'fig/bar.eps']

        with open(temp, 'r') as tmp:
            result = get_graphics_paths(temp)

        self.assertEqual(expected, result)
