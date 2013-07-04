Command line backup tools
============================================

Backup tools are implemented as [paver](https://github.com/paver/paver) tasks.

Supported operations:
* (mysql) List mysql databases
* (mysql) Dump mysql database (or several or all)
* (archive) Compress a file or a dir into gz/bz2/zip archive
* (backup) Generate backup file name with current date/time based on specified backup base name
* (backup) Remove old backups for specified backup base name
* (encrypt) Encrypt file with gnupg

Each task can be launched separately via paver, for example:

    $ ./paver mysqldump --mysql_user=root --db redmine --db sugarcrm --dest=/home/seb/backups

Paver also can show the list of available tasks:

    $ ./paver --help

And a help for a specific command:

    $ ./paver mysqldump --help

Examples of top-level tasks which combine base operations to perform a backup are in the main [pavement.py](https://github.com/serebrov/backup_tools/blob/master/pavement.py) file.

Also see [backup.sh.example](https://github.com/serebrov/backup_tools/blob/master/backup.sh.example) for master shell script to launch backup process (it can be used as a cron job):

    $ sudo crontab -e
    @midnight /home/seb/backups/backup.sh >/home/seb/backups/backup.log 2>/home/seb/backups/backup.err.log

Tasks implementation is based on following code (see ex/ folder):
* [s3-backup](https://github.com/echamberlain/s3-backup).
* [subversion hot backup script](http://svn.apache.org/repos/asf/subversion/trunk/tools/backup/hot-backup.py.in)
* [Python script to backup mysql databases on Debian](http://codepoets.co.uk/2010/python-script-to-backup-mysql-databases-on-debian/)

Paver resourses:
* [Paver documentation](http://paver.github.io/paver/)
* [Paver github repository](https://github.com/paver/paver)
* [Converting from Make to Paver](http://doughellmann.com/2009/01/converting-from-make-to-paver.html)
