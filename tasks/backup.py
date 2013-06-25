"""Tool functions for backups.

This module does not include any tasks, only functions.

"""

#from paver.easy import sh
import time

def get_stamp():
    return time.strftime('%Y-%m-%d-%H:%M:%S')

def gen_file_name(basename):
    return "%s-%s" % (get_stamp(), basename)
