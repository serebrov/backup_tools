"""Tasks and utility functions and classes for mysql."""

#from __future__ import with_statement
#import re

import optparse
import os
import backup
from paver.easy import *

@task
@cmdopts([
    optparse.make_option('-u', '--mysql_user', help='Mysql user name'),
    optparse.make_option('-p', '--mysql_password', default='', help='Mysql user password, default is empty - without password'),
    optparse.make_option('--host', default='localhost', help='Mysql host, default is "localhost"'),
    optparse.make_option('--db', action="append", help='Mysql db to dump, can be used several times to backup several databases'),
    optparse.make_option('-d', '--dest', help='Dump file destination')
])
def mysqldump(options):
    """Perfoms mysql dump using mysqldump command."""
    # ./paver mysqldump --mysql_user=root --db dtztask --db sugar --dest=.
    result = []
    password = ''
    if options.mysql_password:
        password = '-p %s' % (options.mysql_password)
    for database in options.db:
        mysqldump_command = "mysqldump -u %s %s -h %s -e --opt -c %s" % (options.mysql_user, password, options.host, database)
        filename = path(options.dest) / backup.gen_file_name(database+".sql")
        mysqldump_command = (mysqldump_command + " > %s") % (filename)
        sh(mysqldump_command)
        result.append((database,filename))
    print '\n'.join([d+'\n'+dump for d,dump in result])
    return result

@task
@cmdopts([
    optparse.make_option('-u', '--mysql_user', help='Mysql user name'),
    optparse.make_option('-p', '--mysql_password', default='', help='Mysql user password, default is empty - without password'),
    optparse.make_option('--host', default='localhost', help='Mysql host, default is "localhost"'),
])
def mysql_db_list(options):
    """Retuns a list of mysql databases."""
    password = ''
    if options.mysql_password:
        password = '-p %s' % (options.mysql_password)
    db_list_command = "mysql -u %s %s -h %s --silent -N -e 'show databases'" % (options.mysql_user, password, options.host)
    dblist = sh(db_list_command, capture=True).split('\n')
    result = []
    for db in dblist:
        db = db.strip()
        if not db:
            continue
        if db == 'information_schema':
            continue
        if db == 'performance_schema':
            continue
        result.append(db)
    print '\n'.join(result)
    return result

@task
@cmdopts([
    optparse.make_option('-u', '--mysql_user', help='Mysql user name'),
    optparse.make_option('-p', '--mysql_password', default='', help='Mysql user password, default is empty - without password'),
    optparse.make_option('--host', default='localhost', help='Mysql host, default is "localhost"'),
    optparse.make_option('-d', '--dest', help='Dump file destination')
])
def mysqldump_all(options):
    """Dumps all mysql databases."""
    # ./paver mysqldump_all --mysql_user=root --dest=.
    dblist = mysql_db_list()
    options['db'] = []
    for db in dblist:
        options['db'].append(db)
    return mysqldump()
