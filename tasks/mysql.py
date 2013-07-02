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
    optparse.make_option('-p', '--mysql_password', default='', help='Mysql user password'),
    optparse.make_option('--host', default='localhost', help='Mysql host'),
    optparse.make_option('--db', action="append", help='Mysql db to dump'),
    optparse.make_option('-d', '--dest', default='', help='Dump file destination')
])
def mysqldump(options):
    """Perfoms mysql dump."""
    #print options
    # ./paver mysqldump --mysql_user=root --db dtztask --db sugar --dest=.
    result = []
    for database in options.db:
        if not options.mysql_password:
            mysqldump_command = "mysqldump -u %s -h %s -e --opt -c %s" % (options.mysql_user, options.host, database)
        else:
            mysqldump_command = "mysqldump -u %s -p%s -h %s -e --opt -c %s" % (options.mysql_user, options.mysql_password, options.host, database)
        if options.dest:
            #filename = os.path.dirname(os.path.realpath(options.dest)) + '\' + backup.gen_file_name(database+".sql")
            filename = path(options.dest) / backup.gen_file_name(database+".sql")
            mysqldump_command = (mysqldump_command + " > %s") % (filename)
            sh(mysqldump_command)
            result.append((database,filename))
        else:
            dump = sh(mysqldump_command, capture=True)
            result.append((database,dump))
    print '\n'.join([d+'\n'+dump for d,dump in result])
    return result

@task
@cmdopts([
    optparse.make_option('-u', '--mysql_user', help='Mysql user name'),
    optparse.make_option('-p', '--mysql_password', default='', help='Mysql user password'),
    optparse.make_option('--host', default='localhost', help='Mysql host'),
])
def mysql_db_list(options):
    """Retuns mysql db list."""
    if not options.mysql_password:
        db_list_command = "mysql -u %s -h %s --silent -N -e 'show databases'" % (options.mysql_user, options.host)
    else:
        db_list_command = "mysql -u %s -p%s -h %s --silent -N -e 'show databases'" % (options.mysql_user, options.mysql_password, options.host)
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
    optparse.make_option('-p', '--mysql_password', default='', help='Mysql user password'),
    optparse.make_option('--host', default='localhost', help='Mysql host'),
    optparse.make_option('-d', '--dest', default='', help='Dump file destination')
])
def mysqldump_all(options):
    """Dump all mysql databases."""
    # ./paver mysqldump_all --mysql_user=root --dest=.
    dblist = mysql_db_list()
    options['db'] = []
    for db in dblist:
        options['db'].append(db)
    return mysqldump()
