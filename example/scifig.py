#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import glob
import os
import os.path
import shutil
import argparse

from libscifig import detector, database


def list_figdirs(src='src'):
    """
    Return the list of directories containing figures.
    """
    return glob.glob(os.path.join(src, '*'))


def make_build_dir(build='build'):
    """
    Make a build directory.
    """
    logging.debug('Make build dir: %s' % build)
    os.makedirs(build, exist_ok=True)


def clean_up(path):
    """
    Clean up all compiled files.
    """
    db = os.path.join(path, 'db.json')
    logging.debug('Clean up %s' % db)
    try:
        os.remove(db)
    except FileNotFoundError:
        pass
    build = os.path.join(path, 'build')
    logging.debug('Clean up %s' % build)
    if os.path.exists(build):
        shutil.rmtree(build)


def main(workingdir, dest='/tmp', pdf_only=False):
    make_build_dir(os.path.join(workingdir, 'build'))
    tasks = []
    for directory in list_figdirs(os.path.join(workingdir, 'src')):
        tasks.extend(detector.detect_task(directory, workingdir))

    db_path = os.path.join(workingdir, 'db.json')
    with database.DataBase(db_path) as db:
        for task in tasks:
            if pdf_only:
                task.make_pdf(db)
            else:
                task.make(db)
            task.export(db, dst=dest)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='', epilog='')
    parser.add_argument('-c', '--clean', action='store_true',
                        default=False, help='Clean')
    parser.add_argument('--pdf', action='store_true',
                        default=False, help='PDF only')
    parser.add_argument('-d', '--dest', metavar='DEST',
                        default='/tmp', help='destination')
    parser.add_argument('-w', '--workingdir', metavar='WORKINGDIR',
                        default='.', help='Working directory (where src/ '
                        'is and build/ will be written)')
    parser.add_argument('--debug', action='store_true',
                        default=False, help='Run in debug mode')

    args = parser.parse_args()

    from libscifig.collogging import formatter_message, ColoredFormatter
    if args.debug:
        llevel = logging.DEBUG
    else:
        llevel = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(llevel)

    if llevel == logging.DEBUG:
        FORMAT = "[$BOLD%(name)-10s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
    else:
        FORMAT = "%(message)s"

    COLOR_FORMAT = formatter_message(FORMAT, True)
    color_formatter = ColoredFormatter(COLOR_FORMAT)

    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(llevel)
    steam_handler.setFormatter(color_formatter)
    logger.addHandler(steam_handler)

    if args.clean:
        logger.info('Cleaning...')
        clean_up(args.workingdir)
    elif args.pdf:
        main(args.workingdir, args.dest, pdf_only=True)
    else:
        main(args.workingdir, args.dest, pdf_only=False)
