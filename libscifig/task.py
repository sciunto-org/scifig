#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A :class:`Task` is composed of the following steps:

    1. Transform the source files to a tex file
    2. convert tex to pdf with :func:`_tex_to_pdf()`
    3. convert pdf to svg with :func:`_pdf_to_svg()`
    4. convert pdf to eps with :func:`_pdf_to_eps()`
    5. convert pdf to png with :func:`_pdf_to_png()`

Step 1 can be complex and could require several sub-steps.
Thus, the role of :func:`_pre_make()` is to do all these sub-steps.

Steps 2 to 5 usually do not depend on the initial type of the task.
The function :func:`make()` do all of them.

Each format has its own export function. The function :func:`export()`
exports all of them.

"""

import os
import os.path
import shutil
import subprocess
import logging
import re

from libscifig import database as dblib


class Task():
    """
    Parent Task manager.

    :param filepath: filepath of the main file
    :param build: relative filepath of the build dir
    :param db: relative filepath of the db file
    """
    def __init__(self, filepath, build='build', db='db.db'):
        self.db = db
        self.cwd = os.getcwd()
        self.dependencies = []
        self.dependencies.append(filepath)
        self.dirname, filename = os.path.split(filepath)
        self.name = os.path.splitext(filename)[0]
        self.buildpath = os.path.join(build, self.dirname)
        self.pdfmaker = '/usr/bin/pdflatex'
        self.svgmaker = '/usr/bin/pdf2svg'
        self.epsmaker = '/usr/bin/pdftops'
        self.pngmaker = '/usr/bin/gs'

    def get_name(self):
        """
        Return the name of the task.
        """
        return self.dirname

    def check(self):
        """
        Check if the task needs to be done.
        """
        return dblib.check_modification(self.dirname, self.dependencies, self.db)

    def _tex_to_pdf(self):
        """
        Convert tex to pdf.
        """
        logging.info('tex -> pdf')
        # Prepare and run the command
        command = [self.pdfmaker, self.name + '.tex']
        # in plt, all path are relative, need to move
        logging.debug('chdir: %s' % self.buildpath)
        os.chdir(self.buildpath)
        logging.debug('Command: %s' % command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        # go back to the cur dir
        os.chdir(self.cwd)

        stdout, stderr = process.communicate()
        logging.debug(stdout.decode())
        errors = stderr.decode()
        if errors:
            logging.error(errors)  # TODO color

        self.pdf = self.name + '.pdf'

    def _pdf_to_svg(self):
        """
        Convert pdf to svg.
        """
        logging.info('pdf -> svg')
        self.svg = self.name + '.svg'
        # Prepare and run the command
        command = [self.svgmaker, self.name + '.pdf', self.svg]
        # in plt, all path are relative, need to move
        logging.debug('chdir: %s' % self.buildpath)
        os.chdir(self.buildpath)
        logging.debug('Command: %s' % command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        # go back to the cur dir
        os.chdir(self.cwd)

        stdout, stderr = process.communicate()
        logging.debug(stdout.decode())
        errors = stderr.decode()
        if errors:
            logging.error(errors)  # TODO color

    def _pdf_to_eps(self):
        """
        Convert pdf to eps.
        """
        logging.info('pdf -> eps')
        self.eps = self.name + '.eps'
        # Prepare and run the command
        command = [self.epsmaker, '-eps', self.name + '.pdf', self.eps]
        # in plt, all path are relative, need to move
        logging.debug('chdir: %s' % self.buildpath)
        os.chdir(self.buildpath)
        logging.debug('Command: %s' % command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        # go back to the cur dir
        os.chdir(self.cwd)

        stdout, stderr = process.communicate()
        logging.debug(stdout.decode())
        errors = stderr.decode()
        if errors:
            logging.error(errors)  # TODO color

    # TODO sDEVICE: pngalpha and pnggray
    def _pdf_to_png(self, dpi=600):
        """
        Convert pdf to png.
        """
        logging.info('pdf -> png')
        self.png = self.name + '.png'
        # Prepare and run the command
        command = [self.pngmaker, '-sDEVICE=png16m', '-o',
                   self.png, '-r' + str(spi), self.name + '.pdf']
        # in plt, all path are relative, need to move
        logging.debug('chdir: %s' % self.buildpath)
        os.chdir(self.buildpath)
        logging.debug('Command: %s' % command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        # go back to the cur dir
        os.chdir(self.cwd)

        stdout, stderr = process.communicate()
        logging.debug(stdout.decode())
        errors = stderr.decode()
        if errors:
            logging.error(errors)  # TODO color

    def _pre_make(self):
        """
        make a tex file.
        """
        logging.debug('Default pre_make() in class Task, nothing to do!')
        pass

    def make(self):
        """
        Compile the figure in all formats.
        """
        self._pre_make()
        # Build a pdf
        self._tex_to_pdf()
        self._pdf_to_svg()
        self._pdf_to_eps()
        self._pdf_to_png()
        dblib.store_checksum(self.dirname, self.dependencies, self.db)

    def export_pdf(self, dst='/tmp'):
        """
        Export built PDF files.

        :param dst: filepath of the destination directory
        """
        dst = os.path.expanduser(dst)
        pdf_src = os.path.join(self.buildpath, self.pdf)
        logging.debug('Export %s to %s' % (pdf_src, dst))
        shutil.copy(pdf_src, dst)

    def export_svg(self, dst='/tmp'):
        """
        Export built SVG files.

        :param dst: filepath of the destination directory
        """
        dst = os.path.expanduser(dst)
        svg_src = os.path.join(self.buildpath, self.svg)
        logging.debug('Export %s to %s' % (svg_src, dst))
        shutil.copy(svg_src, dst)

    def export_eps(self, dst='/tmp'):
        """
        Export built EPS files.

        :param dst: filepath of the destination directory
        """
        dst = os.path.expanduser(dst)
        eps_src = os.path.join(self.buildpath, self.eps)
        logging.debug('Export %s to %s' % (eps_src, dst))
        shutil.copy(eps_src, dst)

    def export_png(self, dst='/tmp'):
        """
        Export built png files.

        :param dst: filepath of the destination directory
        """
        dst = os.path.expanduser(dst)
        png_src = os.path.join(self.buildpath, self.png)
        logging.debug('Export %s to %s' % (png_src, dst))
        shutil.copy(png_src, dst)

    def export(self, dst='/tmp'):
        """
        Export built files.

        :param dst: filepath of the destination directory
        """
        pdfdir = os.path.join(dst, 'pdf')
        os.makedirs(pdfdir, exist_ok=True)
        self.export_pdf(pdfdir)
        svgdir = os.path.join(dst, 'svg')
        os.makedirs(svgdir, exist_ok=True)
        self.export_svg(svgdir)
        epsdir = os.path.join(dst, 'eps')
        os.makedirs(epsdir, exist_ok=True)
        self.export_eps(epsdir)
        pngdir = os.path.join(dst, 'png')
        os.makedirs(pngdir, exist_ok=True)
        self.export_png(pngdir)

class TikzTask(Task):
    """
    Tikz Task manager.
    """
    def __init__(self, filepath, datafiles=[],
                 build='build', db='db.db'):
        Task.__init__(self, filepath, build=build)
        self.data = datafiles
        self.dependencies.extend(datafiles)
        self.tex = os.path.join(build, self.dirname, self.name + '.tex')
        self.tikz = filepath

    def _tikz_to_tex(self):
        """
        Convert tikz to tex.
        """
        # Copy data files
        for data in self.data:
            dest = os.path.join(self.buildpath, os.path.split(data)[1])
            logging.debug('copy %s file to %s' % (data, dest))
            shutil.copy(data, dest)
        logging.info('tikz -> tex')
        tex_content = '\\documentclass{standalone}\n\n'
        tex_content += '\\usepackage{gnuplot-lua-tikz}\n'
        tex_content += """\\usepackage{tikz}
\\usepackage{amssymb}
\\usepackage{amsfonts}
\\usepackage{mathrsfs}
\\usepackage{amsmath}
\\usepackage[amssymb]{SIunits}\n
"""

        # tikz contains 2 parts
        # above \begin{tikzpicture} -> extra libs...
        # and bellow (code...)
        # For a correct rendering, the top part
        # must be before \begin{document}
        with open(self.tikz, 'r') as fh:
            tikz_content = fh.read()
        tikz_content = tikz_content.split("\\begin{tikzpicture}")
        tex_content += tikz_content[0]
        tex_content += "\\begin{document}\n"
        tex_content += "\\begin{tikzpicture}\n"
        tex_content += tikz_content[1]
        tex_content += '\\end{document}'

        with open(self.tex, 'w') as fh:
            fh.write(tex_content)

    def _pre_make(self):
        """
        make a tex file.
        """
        logging.debug('pre_make(): Tikz file %s' % self.tikz)
        # Make build path
        logging.debug('pre_make build path %s' % self.buildpath)
        os.makedirs(self.buildpath)
        # First convert tikz to tex
        self._tikz_to_tex()


class GnuplotTask(Task):
    """
    Gnuplot Task manager.
    """
    def __init__(self, filepath, datafiles=[], tikzsnippet1=False,
                 tikzsnippet2=False, build='build', db='db.db'):
        Task.__init__(self, filepath, build=build)
        self.plt = filepath

        self.data = datafiles
        self.dependencies.extend(datafiles)
        self.pltcopy = os.path.join(build, self.dirname, self.name + '.plt')
        self.tex = os.path.join(build, self.dirname, self.name + '.tex')
        self.plttikz = os.path.join(build, self.dirname, self.name + '.plttikz')
        self.tikzsnippet1 = tikzsnippet1
        self.tikzsnippet2 = tikzsnippet2
        if tikzsnippet1:
            self.snippet1file = os.path.join(self.dirname, self.name + '.tikzsnippet1')
            self.dependencies.append(self.snippet1file)
        if tikzsnippet2:
            self.snippet2file = os.path.join(self.dirname, self.name + '.tikzsnippet2')
            self.dependencies.append(self.snippet2file)

        self.gnuplot = '/usr/bin/gnuplot'

    def _plt_to_plttikz(self):
        """
        Convert plt to plttikz.
        """
        logging.info('plt -> plttikz')
        logging.debug('copy plt file to %s' % self.buildpath)
        shutil.copyfile(self.plt, self.pltcopy)
        # Copy data files
        for data in self.data:
            dest = os.path.join(self.buildpath, os.path.split(data)[1])
            logging.debug('copy %s file to %s' % (data, dest))
            shutil.copy(data, dest)
        # Prepare and run the command
        command = [self.gnuplot, self.name + '.plt']
        logging.debug('Command: %s' % command)
        # in plt, all path are relative, need to move
        os.chdir(self.buildpath)
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        # go back to the cur dir
        os.chdir(self.cwd)

        stdout, stderr = process.communicate()
        with open(self.plttikz, 'w') as fh:
            fh.write(stdout.decode())
        errors = stderr.decode()
        if errors:
            logging.error(errors)  # TODO color

    def _plttikz_to_tex(self):
        """
        Convert plttikz to tex.
        """
        logging.info('plttikz -> tex')
        tex_content = '\\documentclass{standalone}\n\n'
        tex_content += '\\usepackage{gnuplot-lua-tikz}\n'
        tex_content += """\\usepackage{tikz}
\\usepackage{amssymb}
\\usepackage{amsfonts}
\\usepackage{mathrsfs}
\\usepackage{amsmath}
\\usepackage[amssymb]{SIunits}\n
"""

        # Inject headers
        if self.tikzsnippet1:
            logging.debug('Read tikzsnippet1')
            with open(self.snippet1file, 'r') as fh:
                snippet1 = fh.read()
            snippet1 = re.sub('\\\\end{tikzpicture}', '', snippet1)
            snippet1 = snippet1.split('\\begin{tikzpicture}')
            logging.debug('Inject header tikzsnippet1')
            tex_content += snippet1[0]
        if self.tikzsnippet2:
            logging.debug('Read tikzsnippet2')
            with open(self.snippet2file, 'r') as fh:
                snippet2 = fh.read()
            snippet2 = re.sub('\\\\end{tikzpicture}', '', snippet2)
            snippet2 = snippet1.split('\\begin{tikzpicture}')
            logging.debug('Inject header tikzsnippet2')
            tex_content += snippet2[0]

        tex_content += '\\begin{document}\n'
        # Write the beginning (it is a gnuplot tikz code)
        tex_content += '\\begin{tikzpicture}[gnuplot]\n'

        if self.tikzsnippet1:
            logging.debug('Inject body tikzsnippet1')
            tex_content += snippet1[1]

        # Inject plttikz
        with open(self.plttikz, 'r') as fh:
            plttikz_content = fh.read()
        plttikz_content = plttikz_content.replace('\\end{tikzpicture}', '')
        tex_content += plttikz_content.replace('\\begin{tikzpicture}[gnuplot]', '')

        if self.tikzsnippet2:
            logging.debug('Inject body tikzsnippet2')
            tex_content += snippet2[1]

        tex_content += '\\end{tikzpicture}\n'
        tex_content += '\\end{document}'

        with open(self.tex, 'w') as fh:
            fh.write(tex_content)

    def _pre_make(self):
        """
        make a tex file.
        """
        logging.debug('pre_make(): Gnuplot file %s' % self.plt)
        # Make build path
        logging.debug('pre_make build path %s' % self.buildpath)
        os.makedirs(self.buildpath)
        # First convert plt to plttikz
        self._plt_to_plttikz()
        # Then, make a tex
        self._plttikz_to_tex()