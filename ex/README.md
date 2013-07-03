Command line backup tools
============================================

backup_mysql.py
--------------------------------------------
Backup mysql databases.

Resources:

* http://codepoets.co.uk/2010/python-script-to-backup-mysql-databases-on-debian/
* http://www.abstractclassmate.com/2011/10/small-python-script-to-backup-your.html
* https://github.com/rcruz/AutoMySQLBackup

Usage:
* mkdir ~/backups
* mkdir ~/backups/mysql
* sudo python backup_mysql.py

Add as cron job:
* sudo crontab -e
* @midnight /home/seb/mysql.backup.sh >/home/seb/backups/mysql/backup.log 2>/home/seb/backups/mysql/backup.err.log

hot-backup.py
--------------------------------------------
Backup svn repository.
Initial version is from [subversion tools](http://svn.apache.org/repos/asf/subversion/trunk/tools/backup/hot-backup.py.in)

USAGE:

hot-backup.py [OPTIONS] REPOS_PATH BACKUP_PATH

Create a backup of the repository at REPOS_PATH in a subdirectory of
the BACKUP_PATH location, named after the youngest revision.

Options:
  --archive-type=FMT Create an archive of the backup. FMT can be one of:
                       bz2  : Creates a bzip2 compressed tar file.
                       gz   : Creates a gzip compressed tar file.
                       zip  : Creates a compressed zip file.
                       zip64: Creates a zip64 file (can be > 2GB).
  --num-backups=N    Number of prior backups to keep around (0 to keep all).
  --verify           Verify the backup.
  --help      -h     Print this help message and exit.


s3-backup.py
--------------------------------------------
Backup directory and optionally copy to amazon.

Initial version if from [s3-backup git repository](https://github.com/echamberlain/s3-backup).

USAGE: s3-backup.py [OPTIONS] PATH BACKUP_PATH

Create a backup of PATH in a subdirectory of
the BACKUP_PATH location.

Optionally uploads the backup to S3.  Requires boto.

Options:
  --archive-type=FMT   Create an archive of the backup. FMT can be one of:
                         bz2 : Creates a bzip2 compressed tar file.
                         gz  : Creates a gzip compressed tar file (default).
                         zip : Creates a compressed zip file.
  --num-backups=N      Number of prior backups to keep around (0 to keep all).
  --help      -h       Print this help message and exit.

S3 Options (requires boto):
  --bucket=string      S3 bucket to use for backups (required when using s3 backup)
  --aws-key=key        Your AWS Access Key ID (default is to read the key from the environment)
  --aws-secret=secret  Your AWS Secret Access Key (default is to read the secret from the environment)
  --remove-local       Deletes the local archive after uploading it to S3

Additional resources:
* [Script to backup directoty and scp it to remote machine](http://www.jonstjohn.com/post/25/Simple-Python-Server-Backup-Script). Also supports files exclusion based on masks.
