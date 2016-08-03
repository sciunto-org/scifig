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

from libscifig.checksum import calculate_checksum, is_different


class Task():
    """
    Parent Task manager.

    :param filepath: filepath of the main file
    :param build: relative filepath of the build dir
    """
    def __init__(self, filepath, build='build'):
        self.cwd = os.getcwd()
        self.id = 'ID:' + os.path.relpath(filepath)
        self.dependencies = []
        self.dependencies.append(filepath)
        self.dirname, filename = os.path.split(filepath)
        self.name = os.path.splitext(filename)[0]
        self.buildpath = os.path.join(build, os.path.relpath(self.dirname))
        self.pdfmaker = '/usr/bin/pdflatex'
        self.svgmaker = '/usr/bin/pdf2svg'
        self.epsmaker = '/usr/bin/pdftops'
        self.pngmaker = '/usr/bin/gs'

        self.eps = self.name + '.eps'
        self.pdf = self.name + '.pdf'
        self.png = self.name + '.png'
        self.svg = self.name + '.svg'

    def get_name(self):
        """
        Return the name of the task.
        """
        return self.id

    def _tex_to_pdf(self):
        """
        Convert tex to pdf.
        """
        logging.info('tex -> pdf')
        # Prepare and run the command
        command = [self.pdfmaker, self.name + '.tex']
        # in plt, all path are relative, need to move
        logging.debug('chdir: %s', self.buildpath)
        os.chdir(self.buildpath)
        logging.debug('Command: %s', command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        # go back to the cur dir
        os.chdir(self.cwd)

        stdout, stderr = process.communicate()
        logging.debug(stdout.decode())
        errors = stderr.decode()
        if errors:
            logging.error(errors)  # TODO color

    def _pdf_to_svg(self):
        """
        Convert pdf to svg.
        """
        logging.info('pdf -> svg')

        # Prepare and run the command
        command = [self.svgmaker, self.name + '.pdf', self.svg]
        # in plt, all path are relative, need to move
        logging.debug('chdir: %s', self.buildpath)
        os.chdir(self.buildpath)
        logging.debug('Command: %s', command)
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

        # Prepare and run the command
        command = [self.epsmaker, '-eps', self.name + '.pdf', self.eps]
        # in plt, all path are relative, need to move
        logging.debug('chdir: %s', self.buildpath)
        os.chdir(self.buildpath)
        logging.debug('Command: %s', command)
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

        # Prepare and run the command
        command = [self.pngmaker, '-sDEVICE=png16m', '-o',
                   self.png, '-r' + str(dpi), self.name + '.pdf']
        # in plt, all path are relative, need to move
        logging.debug('chdir: %s', self.buildpath)
        os.chdir(self.buildpath)
        logging.debug('Command: %s', command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        # go back to the cur dir
        os.chdir(self.cwd)

        stdout, stderr = process.communicate()
        logging.debug(stdout.decode())
        errors = stderr.decode()
        if errors:
            logging.error(errors)  # TODO color

    def check_dependencies(self, db):
        """
        Check if dependencies have been modified.

        :param db: `DataBase` instance
        """
        self.current_hashes = {}
        for dep in self.dependencies:
            self.current_hashes[dep] = calculate_checksum(dep)

        db_hashes = db.get(self.id, 'deps')

        return is_different(self.current_hashes, db_hashes)

    def check_targets(self, db, pdf_only=False):
        """
        Check if targets have been modified.

        :param db: `DataBase` instance
        :param pdf_only: Check only the status for pdf
        """
        status = db.get(self.id, 'targets')
        if pdf_only:
            return not status['pdf']
        else:
            if False in status.values():
                return True
            else:
                return False

    def _pre_make(self):
        """
        Make a tex file.
        """
        logging.debug('Default pre_make() in class Task, nothing to do!')
        pass

    def make_pdf(self, db):
        """
        Compile the figure in pdf.
        """
        if self.check_dependencies(db) or self.check_targets(db, pdf_only=True):
            logging.info('Build in pdf %s' % self.name)
            self._pre_make()
            # Build a pdf
            self._tex_to_pdf()
            db.set(self.id, 'deps', self.current_hashes)
            target_status = {'tex': True,
                             'pdf': True,
                             'svg': False,
                             'eps': False,
                             'png': False}
            db.set(self.id, 'targets', target_status)
            db.set(self.id, 'export', target_status)
        else:
            logging.info('Nothing to do for %s' % self.name)

    def make(self, db):
        """
        Compile the figure in all formats.
        """
        if self.check_dependencies(db) or self.check_targets(db, pdf_only=False):
            logging.info('Build in all formats %s' % self.name)
            self._pre_make()
            # Build a pdf
            self._tex_to_pdf()
            # Build other formats
            self._pdf_to_svg()
            self._pdf_to_eps()
            self._pdf_to_png()
            db.set(self.id, 'deps', self.current_hashes)
            target_status = {'tex': True,
                             'pdf': True,
                             'svg': True,
                             'eps': True,
                             'png': True}
            db.set(self.id, 'targets', target_status)
            db.set(self.id, 'export', target_status)
        else:
            logging.info('Nothing to do for %s' % self.name)

    def export_tex(self, dst='/tmp'):
        """
        Export TEX files.

        :param dst: filepath of the destination directory
        """
        dst = os.path.expanduser(dst)
        tex_src = self.tex
        logging.debug('Export %s to %s', tex_src, dst)
        shutil.copy(tex_src, dst)

    def export_pdf(self, dst='/tmp'):
        """
        Export built PDF files.

        :param dst: filepath of the destination directory
        """
        dst = os.path.expanduser(dst)
        pdf_src = os.path.join(self.buildpath, self.pdf)
        logging.debug('Export %s to %s', pdf_src, dst)
        shutil.copy(pdf_src, dst)

    def export_svg(self, dst='/tmp'):
        """
        Export built SVG files.

        :param dst: filepath of the destination directory
        """
        dst = os.path.expanduser(dst)
        svg_src = os.path.join(self.buildpath, self.svg)
        logging.debug('Export %s to %s', svg_src, dst)
        shutil.copy(svg_src, dst)

    def export_eps(self, dst='/tmp'):
        """
        Export built EPS files.

        :param dst: filepath of the destination directory
        """
        dst = os.path.expanduser(dst)
        eps_src = os.path.join(self.buildpath, self.eps)
        logging.debug('Export %s to %s', eps_src, dst)
        shutil.copy(eps_src, dst)

    def export_png(self, dst='/tmp'):
        """
        Export built png files.

        :param dst: filepath of the destination directory
        """
        dst = os.path.expanduser(dst)
        png_src = os.path.join(self.buildpath, self.png)
        logging.debug('Export %s to %s', png_src, dst)
        shutil.copy(png_src, dst)

    def export(self, db, dst='/tmp'):
        """
        Export built files.

        :param db: `DataBase` instance
        :param dst: filepath of the destination directory
        """
        logging.info('Export %s' % self.name)
        status = db.get(self.id, 'export')
        for ext, func in (('tex', self.export_tex),
                          ('pdf', self.export_pdf),
                          ('svg', self.export_svg),
                          ('eps', self.export_eps),
                          ('png', self.export_png),):

            if status[ext]:
                path = os.path.join(dst, ext)
                os.makedirs(path, exist_ok=True)
                func(path)
        export_status = {'tex': False,
                         'pdf': False,
                         'svg': False,
                         'eps': False,
                         'png': False}
        db.set(self.id, 'export', export_status)


class TikzTask(Task):
    """
    Tikz Task manager.
    """
    def __init__(self, filepath, datafiles=[],
                 build='build'):
        Task.__init__(self, filepath, build=build)
        self.data = datafiles
        self.dependencies.extend(datafiles)
        self.tex = os.path.join(build, self.dirname, self.name + '.tex')
        self.tikz = filepath

    def _tikz_to_tex(self):
        """
        Convert tikz to tex.

        :raises: SyntaxError
        """
        # Copy data files
        for data in self.data:
            # Data starts from the root.
            # We need the relative path from the individual directory
            # (ex: src/figure/)
            dest = os.path.join(self.buildpath, os.path.relpath(data,
                                start=os.path.split(self.tikz)[0]))
            # Data may be in subdirectories
            # We reproduce the tree
            os.makedirs(os.path.split(dest)[0], exist_ok=True)
            logging.debug('copy %s file to %s', data, dest)
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
        tex_content += "\\begin{tikzpicture}"
        try:
            tex_content += tikz_content[1]
        except IndexError:
            # The file does not contain tikzpicture
            raise SyntaxError('The file %s does not contain \\begin{tikzpicture}' % self.tikz)
        tex_content += '\\end{document}'

        with open(self.tex, 'w') as fh:
            fh.write(tex_content)

    def _pre_make(self):
        """
        make a tex file.
        """
        logging.debug('pre_make(): Tikz file %s', self.tikz)
        # Make build path
        logging.debug('pre_make build path %s', self.buildpath)
        os.makedirs(self.buildpath, exist_ok=True)
        # First convert tikz to tex
        self._tikz_to_tex()


class GnuplotTask(Task):
    """
    Gnuplot Task manager.
    """
    def __init__(self, filepath, datafiles=[], tikzsnippet=False,
                 tikzsnippet1=False, tikzsnippet2=False,
                 build='build'):
        Task.__init__(self, filepath, build=build)
        self.plt = filepath

        self.data = datafiles
        self.dependencies.extend(datafiles)
        self.pltcopy = os.path.join(build, self.dirname, self.name + '.plt')
        self.tex = os.path.join(build, self.dirname, self.name + '.tex')
        self.plttikz = os.path.join(build, self.dirname, self.name + '.plttikz')
        self.tikzsnippet = tikzsnippet
        self.tikzsnippet1 = tikzsnippet1
        self.tikzsnippet2 = tikzsnippet2
        if tikzsnippet:
            self.snippetfile = os.path.join(self.dirname, self.name + '.tikzsnippet')
            logging.debug('Append dependency: %s' % self.snippetfile)
            self.dependencies.append(self.snippetfile)
        if tikzsnippet1:
            self.snippet1file = os.path.join(self.dirname, self.name + '.tikzsnippet1')
            logging.debug('Append dependency: %s' % self.snippet1file)
            self.dependencies.append(self.snippet1file)
        if tikzsnippet2:
            self.snippet2file = os.path.join(self.dirname, self.name + '.tikzsnippet2')
            logging.debug('Append dependency: %s' % self.snippet2file)
            self.dependencies.append(self.snippet2file)

        self.gnuplot = '/usr/bin/gnuplot'

    def _plt_to_plttikz(self):
        """
        Convert plt to plttikz.
        """
        logging.info('plt -> plttikz')
        logging.debug('copy plt file to %s', self.buildpath)
        shutil.copyfile(self.plt, self.pltcopy)

        # Copy data files
        for data in self.data:
            # Data starts from the root.
            # We need the relative path from the individual directory (ex: src/figure/)
            dest = os.path.join(self.buildpath, os.path.relpath(data,
                                start=os.path.split(self.plt)[0]))
            # Data may be in subdirectories
            # We reproduce the tree
            os.makedirs(os.path.split(dest)[0], exist_ok=True)
            shutil.copy(data, dest)
        # Prepare and run the command
        command = [self.gnuplot, self.name + '.plt']
        logging.debug('Command: %s', command)
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

        :raises: SyntaxError
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
        if self.tikzsnippet:
            logging.debug('Read tikzsnippet')
            with open(self.snippetfile, 'r') as fh:
                snippet = fh.read()
            snippet = re.sub('\\\\end{tikzpicture}', '', snippet)
            snippet = snippet.split('\\begin{tikzpicture}')
            logging.debug('Inject header tikzsnippet')
            tex_content += snippet[0]
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
            snippet2 = snippet2.split('\\begin{tikzpicture}')
            logging.debug('Inject header tikzsnippet2')
            tex_content += snippet2[0]

        tex_content += '\\begin{document}\n'
        # Write the beginning (it is a gnuplot tikz code)
        tex_content += '\\begin{tikzpicture}[gnuplot]\n'

        if self.tikzsnippet:
            logging.debug('Inject body tikzsnippet')
            try:
                tex_content += snippet[1]
            except IndexError:
                # The file does not contain tikzpicture
                raise SyntaxError('The file %s does not contain \\begin{tikzpicture}' % self.tikzsnippet)
        if self.tikzsnippet1:
            logging.debug('Inject body tikzsnippet1')
            try:
                tex_content += snippet1[1]
            except IndexError:
                # The file does not contain tikzpicture
                raise SyntaxError('The file %s does not contain \\begin{tikzpicture}' % self.tikzsnippet1)

        # Inject plttikz
        with open(self.plttikz, 'r') as fh:
            plttikz_content = fh.read()
        plttikz_content = plttikz_content.replace('\\end{tikzpicture}', '')
        tex_content += plttikz_content.replace('\\begin{tikzpicture}[gnuplot]', '')

        if self.tikzsnippet2:
            logging.debug('Inject body tikzsnippet2')
            try:
                tex_content += snippet2[1]
            except IndexError:
                # The file does not contain tikzpicture
                raise SyntaxError('The file %s does not contain \\begin{tikzpicture}' % self.tikzsnippet2)

        tex_content += '\\end{tikzpicture}\n'
        tex_content += '\\end{document}'

        with open(self.tex, 'w') as fh:
            fh.write(tex_content)

    def _pre_make(self):
        """
        make a tex file.
        """
        logging.debug('pre_make(): Gnuplot file %s', self.plt)
        # Make build path
        logging.debug('pre_make build path %s', self.buildpath)
        os.makedirs(self.buildpath, exist_ok=True)
        # First convert plt to plttikz
        self._plt_to_plttikz()
        # Then, make a tex
        self._plttikz_to_tex()
