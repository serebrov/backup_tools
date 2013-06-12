#!/usr/bin/env python
import ConfigParser
import os
import time

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

# On Debian, /etc/mysql/debian.cnf contains 'root' a like login and password.
config = ConfigParser.ConfigParser()
config.read("/etc/mysql/debian.cnf")
username = config.get('client', 'user')
password = config.get('client', 'password')
hostname = config.get('client', 'host')

filestamp = time.strftime('%Y-%m-%d-%H:%M:%S')

# Get a list of databases with :
database_list_command="mysql -u %s -p%s -h %s --silent -N -e 'show databases'" % (username, password, hostname)
for database in os.popen(database_list_command).readlines():
    database = database.strip()
    if database == 'information_schema':
        continue
    if database == 'performance_schema':
        continue
    filename = "~/backups/mysql/%s-%s.sql" % (filestamp, database)
    os.popen("mysqldump -u %s -p%s -h %s -e --opt -c %s | gzip -c > %s.gz" % (username, password, hostname, database, filename))
# todo check options below
# cmd="mysqldump -u "+user+" -h "+host+" -p"+passwd+" --opt --routines --flush-privileges --single-transaction --database "+result[0]+" | gzip -9 --rsyncable > yourlocation/"+backupfile
