#!/usr/bin/env python
import ConfigParser
import os
import time
import sys
import optparse

# resources
# http://codepoets.co.uk/2010/python-script-to-backup-mysql-databases-on-debian/
# http://www.abstractclassmate.com/2011/10/small-python-script-to-backup-your.html
# https://github.com/rcruz/AutoMySQLBackup

#usage
# mkdir ~/backups
# mkdir ~/backups/mysql
# sudo python backup_mysql.py

# cron job
# sudo crontab -e
# @midnight /home/seb/mysql.backup.sh >/home/seb/backups/mysql/backup.log 2>/home/seb/backups/mysql/backup.err.log

# todo
# add config and use it instead of /etc/mysql/debian.cnf
# make backup dir configurable
# the script can be lauched then without sudo

class BackupConfig(object):
    """Reads configuration."""
    def __init__(self):
        """Constructor reads command line arguments and store given parameters."""
        ###Getting command line options
        usage = 'usage: %prog [options]'
        parser = optparse.OptionParser()
        parser.add_option('-c',  action="store", dest="config_path")
        parser.add_option('--mysql_user',  action="store", dest="mysql_user")
        parser.add_option('--mysql_password',  action="store", dest="mysql_password")
        parser.add_option('--mysql_host',  action="store", dest="mysql_host")
        cmd_opts, args = parser.parse_args()
        self.config_path = cmd_opts.config_path
        self.mysql_user = cmd_opts.mysql_user
        self.mysql_password = cmd_opts.mysql_password
        self.mysql_host = cmd_opts.mysql_host
        if self.config_path is None:
            self.config_path = os.path.dirname(os.path.realpath(__file__))+"/backup.cfg"
            print "Found default config "+self.config_path
        if not os.path.exists(self.config_path):
            sys.stderr.write('\nERROR: Missing config file: ' + self.config_path)
            sys.exit(1)
        self.configure(parser)

    def configure(self, parser):
        """Read configuration from the config file."""
        config = ConfigParser.ConfigParser()
        config.read(self.config_path)
        self.backup_dir = config.get('backup', 'dir')
        if self.mysql_user is None:
            self.mysql_user = config.get('mysql', 'user')
        if self.mysql_password is None:
            self.mysql_password = config.get('mysql', 'password')
        if self.mysql_host is None:
            self.mysql_host = config.get('mysql', 'host')

# On Debian, /etc/mysql/debian.cnf contains 'root' a like login and password.
config = BackupConfig()
filestamp = time.strftime('%Y-%m-%d-%H:%M:%S')

# Get a list of databases with :
database_list_command="mysql -u %s -p%s -h %s --silent -N -e 'show databases'" % (config.mysql_user, config.mysql_password, config.mysql_host)
#database_list_command="mysql -u %s --silent -N -e 'show databases'" % (config.mysql_user)
for database in os.popen(database_list_command).readlines():
    database = database.strip()
    if database == 'information_schema':
        continue
    if database == 'performance_schema':
        continue
    filename = config.backup_dir+"/%s-%s.sql" % (filestamp, database)
    os.popen("mysqldump -u %s -p%s -h %s -e --opt -c %s | gzip -c > %s.gz" % (config.mysql_user, config.mysql_password, config.mysql_host, database, filename))
# todo check options below
# cmd="mysqldump -u "+user+" -h "+host+" -p"+passwd+" --opt --routines --flush-privileges --single-transaction --database "+result[0]+" | gzip -9 --rsyncable > yourlocation/"+backupfile
