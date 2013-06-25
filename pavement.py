#!/usr/bin/env python
from paver.easy import *
from paver.release import setup_meta

import time

from tasks import backup

#import paver.doctools
#import paver.virtual
#import paver.misctasks
#from paver.setuputils import setup

#options = environment.options

@task
@cmdopts([
    ('base=', 'b', 'Basename for backup file')
])
def backup_file_name(options):
    """ Run as paver backup_file_name --base=test.sql ."""
    filename = backup.gen_file_name(options.base)
    print filename
    return filename
