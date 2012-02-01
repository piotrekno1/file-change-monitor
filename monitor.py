"""
Executes input system command upon file change.
Example: monitor.py -c "pdflatex main.tex" -i 1 -p ".*?\.tex"
Created on: 01.02.2012
"""

__author__ = 'Piotr Duda <piotrekno1@gmail.com>'
__version__ = 0.1


import os
import sys
import time
import re
import subprocess
import logging
from optparse import OptionParser
from datetime import datetime, timedelta


def monitor(cmd, file_type, interval):
    """Monitors files for changes and stars the specified command when changes
    are found
    `cmd` The command to be applied after file change
    `file_type` Regexp describing monitored file names
    'interval' How often should the check run
    """
    while True:
        if watched_file_changed(file_type, interval):
            apply_user_cmd(cmd)

        logging.debug("Waiting for next iteration")
        time.sleep(interval)


def watched_file_changed(file_type, interval):
    """Checks whether the files in the current directory, or its subdirectories
    did not change.

    `file_type` Regexp describing file names taken into account while checking.
    Returns True/False depending on file changes
    """
    for root, dirs, files in os.walk(os.path.curdir):
        for fname in files:
            try:
                if re.match(file_type, fname):
                    if file_changed(os.path.join(root, fname), interval):
                        logging.info("File modified!")
                        return True
            except re.error:
                logging.error("Invalid file name regex")
                sys.exit(1)
    return False


def file_changed(file_path, interval):
    """Checks the modification date for the file.
    Returns True/False if the file was modified earlier or equal than interval
    """
    finfo = os.stat(file_path)
    date_modified = datetime.fromtimestamp(finfo.st_mtime)
    if datetime.now() < date_modified + timedelta(seconds=1):
        return True
    return False


def apply_user_cmd(cmd):
    """Calls the specified system command."""
    subprocess.call(cmd.split())


USAGE = '''%prog -i number -p re_pattern -c command'''


def main():
    parser = OptionParser(usage=USAGE)
    parser.add_option('-i', '--interval', dest='interval', help="How often to\
            check for updates (seconds)", type='int', default=1)
    parser.add_option('-p', '--pattern', dest='pattern', help="Pattern for\
        files to minitor", default='.*', type='string')
    parser.add_option('-c', '--cmd', dest='command', help="Command to execute\
            upon file change", type='string')
    parser.add_option('-v', '--verbose', dest='verbose', help="Verbose mode",
        default=False, action='store_true')

    (opts, args) = parser.parse_args()

    if not opts.command:
        parser.print_usage()
        sys.exit(1)

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)

    try:
        monitor(opts.command, opts.pattern, opts.interval)
    except KeyboardInterrupt:
        logging.info("Shutting down...")

if __name__ == '__main__':
    main()
