#!/usr/bin/env python
from paver.easy import *
from paver.release import setup_meta

import optparse
import os
import time

from tasks import backup
from tasks import mysql
from tasks import archive

#import paver.doctools
#import paver.virtual
#import paver.misctasks
#from paver.setuputils import setup

#options = environment.options

# Paver resourses
# http://paver.github.io/paver/
# https://github.com/paver/paver
# http://doughellmann.com/2009/01/converting-from-make-to-paver.html

@task
@cmdopts([
    ('base=', 'b', 'Basename for backup file')
])
def backup_file_name(options):
    """ Run as paver backup_file_name --base=test.sql ."""
    filename = backup.gen_file_name(options.base)
    print filename
    return filename

@task
@cmdopts([
    optparse.make_option('-u', '--mysql_user', help='Mysql user name'),
    optparse.make_option('-p', '--mysql_password', default='', help='Mysql user password'),
    optparse.make_option('--host', default='localhost', help='Mysql host'),
    optparse.make_option('-d', '--dest', default='', help='Dump file destination'),
    optparse.make_option('--archive_type', default='gz', help='Archive type: gz, bz2 or zip'),
    optparse.make_option('--name', default='backup', help='Backup file name'),
])
def backup_mysql(options):
    # ./paver backup_mysql -u root -d ./test
    dumps = mysql.mysqldump_all(options)
    #options['db']=['test']
    #dumps = mysql.mysqldump(options)
    for db, dump in dumps:
         options['src'] = dump
         options['name'] = db
         arc = archive.compress()
         backup.rm_file(dump)
         ext = archive.archive_map[options.archive_type]
         backup.rm_old_files(options.dest, db, ext, 28)


@task
@cmdopts([
    optparse.make_option('-s', '--src', help='Source project dir'),
    optparse.make_option('-d', '--dest', default='', help='Dump file destination'),
    optparse.make_option('--archive_type', default='gz', help='Archive type: gz, bz2 or zip'),
    optparse.make_option('--name', default='', help='Project name'),
])
def backup_dir(options):
    # ./paver backup_dir -s /home/user/projects/myproject -d ./test --name myproject
    if not options.name:
        options.name = os.path.basename(options.src)
    arc = archive.compress()
    ext = archive.archive_map[options.archive_type]
    backup.rm_old_files(options.dest, options.name, ext, 28)
