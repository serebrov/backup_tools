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
    optparse.make_option('-n', '--num', default='7', type="int", help='Number of backups to keep'),
    optparse.make_option('--recipient', default='', help='gpg --recipient parameter'),
    optparse.make_option('--user', default='', help='gpg --local-user parameter'),
    optparse.make_option('--trust_model', default='always', help='gpg --trust-model parameter.'),
    optparse.make_option('--test', default='', help='test mode, backup single "test" database'),
])
def backup_mysql(options):
    """Do a mysql backup.

    Dumps all databases, compresses dumps and removes old backups.
    Optionally (if --recipent is specified) encrypts backup with gpg.
    """
    # ./paver backup_mysql -u root -d ./test
    if options.test:
        options['db']=['test']
    dumps = mysql.mysqldump_all(options)
    for db, dump in dumps:
         options['src'] = dump
         options['name'] = db
         arc = archive.compress()
         backup.rm_file(dump)
         if options.recipient:
             options.src = arc
             gpg = encrypt.gnupg()
             backup.rm_file(arc)
         backup.rm_old_files(options.dest, db, options.num)


@task
@cmdopts([
    optparse.make_option('-s', '--src', help='Source project dir'),
    optparse.make_option('-d', '--dest', default='', help='Dump file destination'),
    optparse.make_option('--archive_type', default='gz', help='Archive type: gz, bz2 or zip'),
    optparse.make_option('--name', default='', help='Project name'),
    optparse.make_option('-n', '--num', default='7', type="int", help='Number of backups to keep'),
    optparse.make_option('--recipient', default='', help='gpg --recipient parameter'),
    optparse.make_option('--user', default='', help='gpg --local-user parameter'),
    optparse.make_option('--trust_model', default='always', help='gpg --trust-model parameter.'),
])
def backup_dir(options):
    """Do a project directory backup.

    Compresses a project directory and removes old backups.
    Optionally (if --recipent is specified) encrypts backup with gpg.
    """
    # ./paver backup_dir -s /home/user/projects/myproject -d ./test --name myproject
    if not options.name:
        options.name = os.path.basename(options.src)
    arc = archive.compress()
    if options.recipient:
        options.src = arc
        gpg = encrypt.gnupg()
        backup.rm_file(arc)
    backup.rm_old_files(options.dest, options.name, options.num)
