#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

import subprocess
import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ChangeHandler(FileSystemEventHandler):
    """React to modified source files."""
    def on_modified(self, event):
        extensions = ('.plt', '.tikz', '.tikzsnippet')
        if os.path.splitext(event.src_path)[-1].lower() in extensions:
            subprocess.call("make pdf", shell=True)


def main():
    handler = ChangeHandler()
    observer = Observer()
    observer.schedule(handler, 'src', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
