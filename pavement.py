#!/usr/bin/env python
from paver.easy import *
from paver.release import setup_meta

import optparse
import os
import time

from tasks import backup
from tasks import mysql
from tasks import archive
from tasks import encrypt

@task
@cmdopts([
    optparse.make_option('-u', '--mysql_user', help='Mysql user name'),
    optparse.make_option('-p', '--mysql_password', default='', help='Mysql user password'),
    optparse.make_option('--host', default='localhost', help='Mysql host'),
    optparse.make_option('-d', '--dest', help='Dump file destination'),
    optparse.make_option('--archive_type', default='gz', help='Archive type: gz, bz2 or zip'),
    optparse.make_option('--name', default='backup', help='Backup file name'),
])
def backup_mysql(options):
    """Do a mysql backup.

    Dumps all databases, compresses dumps and removes old backups.
    """
    # ./paver backup_mysql -u root -d ./test
    dumps = mysql.mysqldump_all(options)
    for db, dump in dumps:
         options['src'] = dump
         options['name'] = db
         arc = archive.compress()
         backup.rm_file(dump)
         backup.rm_old_files(options.dest, db, 28)

@task
@cmdopts([
    optparse.make_option('-u', '--mysql_user', help='Mysql user name'),
    optparse.make_option('-p', '--mysql_password', default='', help='Mysql user password'),
    optparse.make_option('--host', default='localhost', help='Mysql host'),
    optparse.make_option('-d', '--dest', help='Dump file destination'),
    optparse.make_option('--archive_type', default='gz', help='Archive type: gz, bz2 or zip'),
    optparse.make_option('--name', default='backup', help='Backup file name'),
])
def backup_mysql_test(options):
    """Do a test mysql backup.

    The same as backup_mysql, but backups single 'test' database.
    This task is to do a fast test of the backup_mysql task.
    """
    # ./paver backup_mysql -u root -d ./test
    options['db']=['test']
    dumps = mysql.mysqldump(options)
    for db, dump in dumps:
         options['src'] = dump
         options['name'] = db
         arc = archive.compress()
         backup.rm_file(dump)
         backup.rm_old_files(options.dest, db, 4)

@task
@cmdopts([
    optparse.make_option('-s', '--src', help='Source project dir'),
    optparse.make_option('-d', '--dest', default='', help='Dump file destination'),
    optparse.make_option('--archive_type', default='gz', help='Archive type: gz, bz2 or zip'),
    optparse.make_option('--name', default='', help='Project name'),
])
def backup_dir(options):
    """Do a project directory backup.

    Compresses a project directory and removes old backups.
    """
    # ./paver backup_dir -s /home/user/projects/myproject -d ./test --name myproject
    if not options.name:
        options.name = os.path.basename(options.src)
    arc = archive.compress()
    backup.rm_old_files(options.dest, options.name, 28)
