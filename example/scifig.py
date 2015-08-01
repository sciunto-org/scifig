#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import glob
import os
import os.path
import shutil
import argparse

from libscifig import detector


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
    build = os.path.join(path, 'build')
    db = os.path.join(path, 'db.db')
    logging.debug('Clean up %s' % build)
    if os.path.exists(build):
        shutil.rmtree(build)
    from libscifig.database import erase_db
    erase_db(db)


def main(workingdir, dest='/tmp'):
    make_build_dir(os.path.join(workingdir, 'build'))
    tasks = []
    for directory in list_figdirs(os.path.join(workingdir, 'src')):
        tasks.extend(detector.detect_task(directory, workingdir))

    for task in tasks:
        if task.check():
            logging.info('Build %s' % task.get_name())
            task.make()
            logging.info('Export %s' % task.get_name())
            task.export(dst=dest)
        else:
            logging.info('Nothing to do for %s' % task.get_name())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='', epilog='')
    #parser.add_argument('conf', help='Configuration file', metavar='CONF')
    parser.add_argument('-c', '--clean', action='store_true',
                        default=False, help='Clean')
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

    #logger.debug(args)
    if args.clean:
        logger.info('Cleaning...')
        clean_up(args.workingdir)
    else:
        main(args.workingdir, args.dest)
