"""Tasks and utility functions and classes for mysql."""

#from __future__ import with_statement
#import re

import backup
from paver.easy import *

@task
@cmdopts([
    ('mysql_user=', 'u', 'Mysql user name'),
    ('mysql_password=', 'p', 'Mysql user password'),
    ('mysql_host=', 'h', 'Mysql host'),
    ('dest=', 'd', 'Dump destination'),
])
def mysqldump(options):
    """Perfoms mysql dump."""
    db_list_command = "mysql -u %s -p%s -h %s --silent -N -e 'show databases'" % (options.mysql_user, options.mysql_password, options.mysql_host)
    for database in sh(database_list_command).readlines():
        database = database.strip()
        if database == 'information_schema':
            continue
        if database == 'performance_schema':
            continue
        filename = options.backup_dir + backup.gen_file_name(database+".sql")
        sh("mysqldump -u %s -p%s -h %s -e --opt -c %s | gzip -c > %s.gz" % (config.mysql_user, config.mysql_password, config.mysql_host, database, filename))

