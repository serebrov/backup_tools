#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  s3-backup.py: perform a backup of a path
#
# Based on hot-backup.py   

######################################################################

import sys, os, getopt, stat, re, time, shutil, subprocess,datetime

######################################################################
# Global Settings

# Default number of backups to keep around (0 for "keep them all")
num_backups = int(os.environ.get("TRAC_BACKUPS_NUMBER", 64))

# Archive types/extensions
archive_map = {
  'gz'  : ".tar.gz",
  'bz2' : ".tar.bz2",
  'zip' : ".zip"
  }

# Chmod recursively on a whole subtree
def chmod_tree(path, mode, mask):
  def visit(arg, dirname, names):
    mode, mask = arg
    for name in names:
      fullname = os.path.join(dirname, name)
      if not os.path.islink(fullname):
        new_mode = (os.stat(fullname)[stat.ST_MODE] & ~mask) | mode
        os.chmod(fullname, new_mode)
  os.path.walk(path, visit, (mode, mask))

# For clearing away read-only directories
def safe_rmtree(dirname, retry=0):
  "Remove the tree at DIRNAME, making it writable first"
  def rmtree(dirname):
    chmod_tree(dirname, 0666, 0666)
    shutil.rmtree(dirname)

  if not os.path.exists(dirname):
    return

  if retry:
    for delay in (0.5, 1, 2, 4):
      try:
        rmtree(dirname)
        break
      except:
        time.sleep(delay)
    else:
      rmtree(dirname)
  else:
    rmtree(dirname)

######################################################################
# Command line arguments

def usage(out = sys.stdout):
  scriptname = os.path.basename(sys.argv[0])
  out.write(
"""USAGE: %s [OPTIONS] PATH BACKUP_PATH

Create a backup of PATH in a subdirectory of
the BACKUP_PATH location.

Optionally uploads the backup to S3.

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

""" % (scriptname,))


try:
  opts, args = getopt.gnu_getopt(sys.argv[1:], "h?", ["archive-type=",
                                                      "num-backups=",
                                                      "help",
                                                      "bucket=",
                                                      "aws-key=",
                                                      "aws-secret=",
                                                      "remove-local"])
except getopt.GetoptError, e:
  sys.stderr.write("ERROR: %s\n\n" % e)
  sys.stderr.flush()
  usage(sys.stderr)
  sys.exit(2)

archive_type = 'gz'
s3bucket = s3aws_key = s3aws_secret = bucket = remove_local = None

for o, a in opts:
  if o == "--archive-type":
    archive_type = a
  elif o == "--num-backups":
    num_backups = int(a)
  elif o in ("-h", "--help", "-?"):
    usage()
    sys.exit()
  elif o == "--bucket":
    s3bucket = a
    
    # set the default archive_type
    if archive_type is None:
      archive_type = 'gz'
    
    try:
      import boto
    except ImportError, e:
      sys.stderr.write("ERROR: %s\n\n" %e)
      sys.stderr.flush()
      usage(sys.stderr)
      sys.exit(2)      
  elif o == "--aws-key":
    s3aws_key = a
  elif o == "--aws-secret":
    s3aws_secret = a
  elif o == "--remove-local":
    remove_local = True

if len(args) != 2:
  sys.stderr.write("ERROR: only two arguments allowed.\n\n")
  sys.stderr.flush()
  usage(sys.stderr)
  sys.exit(2)

# connect and open bucket, no need to continue if we can't
if s3bucket is not None:
  from boto.s3.connection import S3Connection
  if s3aws_key is None:
    s3connection = S3Connection()
  else:
    s3connection = S3Connection(s3aws_key,s3aws_secret)
  
  try:
    bucket = s3connection.create_bucket(s3bucket)
  except Exception, e:    
    sys.stderr.write("ERROR: %s\n" % e)

    rs = s3connection.get_all_buckets()

    sys.stderr.write("\nUse an available bucket or create a new one.\nAvailable buckets:\n\n")
    for b in rs:
      sys.stderr.write("     %s" % b.name)
      
    sys.stderr.flush()
    sys.exit(1)

# Path to project
project_dir = args[0]
project = os.path.basename(os.path.abspath(project_dir))

# Where to store the project backup.  The backup will be placed in
# a *subdirectory* of this location.
backup_dir = args[1]

# Added to the filename regexp, set when using --archive-type.
ext_re = ""

# Do we want to create an archive of the backup
if archive_type:
  if archive_type in archive_map:
    # Additionally find files with the archive extension.
    ext_re = "(" + re.escape(archive_map[archive_type]) + ")?"
  else:
    sys.stderr.write("Unknown archive type '%s'.\n\n\n" % archive_type)
    sys.stderr.flush()
    usage(sys.stderr)
    sys.exit(2)


######################################################################
# Helper functions

def comparator(a, b):
  # We pass in filenames so there is never a case where they are equal.
  regexp = re.compile("-(?P<datetime>\d{4}-\d{2}-\d{2}-\d{2}:\d{2}:\d{2})?" +
                      ext_re + "$")
  matcha = regexp.search(a)
  matchb = regexp.search(b)
  reva = matcha.groupdict()['datetime']
  revb = matchb.groupdict()['datetime']
  if (reva < revb):
    return -1
  else:
    return 1

######################################################################
# Main

print("Beginning backup of '"+ project_dir + "'.")


### Step 2: Find next available backup path

timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H:%M:%S')

backup_subdir = os.path.join(backup_dir, project + "-" + timestamp)


### Step 4: Make an archive of the backup if required.
if archive_type:
  archive_path = backup_subdir + archive_map[archive_type]
  err_msg = ""
  err_code = 0

  print("Archiving backup to '" + archive_path + "'...")
  if archive_type == 'gz' or archive_type == 'bz2':
    try:
      import tarfile
      tar = tarfile.open(archive_path, 'w:' + archive_type)
      tar.add(project_dir, os.path.basename(project_dir))
      tar.close()
    except ImportError, e:
      err_msg = "Import failed: " + str(e)
      err_code = -2
    except tarfile.TarError, e:
      err_msg = "Tar failed: " + str(e)
      err_code = -3

  elif archive_type == 'zip':
    try:
      import zipfile
      
      def add_to_zip(baton, dirname, names):
        zp = baton[0]
        root = os.path.join(baton[1], '')
        
        for file in names:
          path = os.path.join(dirname, file)
          if os.path.isfile(path):
            zp.write(path, path[len(root):])
          elif os.path.isdir(path) and os.path.islink(path):
            os.path.walk(path, add_to_zip, (zp, path))
            
      zp = zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED)
      os.path.walk(project_dir, add_to_zip, (zp, project_dir))
      zp.close()
    except ImportError, e:
      err_msg = "Import failed: " + str(e)
      err_code = -4
    except zipfile.error, e:
      err_msg = "Zip failed: " + str(e)
      err_code = -5


  if err_code != 0:
    sys.stderr.write("Unable to create an archive for the backup.\n%s\n" % err_msg)
    sys.stderr.flush()
    sys.exit(err_code)
  else:
    print("Archive created...")
  
  if bucket:
    print("Uploading %s to S3..." % archive_path)
    from boto.s3.key import Key
    k = Key(bucket,name=os.path.basename(archive_path))
    k.set_contents_from_filename(archive_path)
    
    if remove_local:
      print("Removing local copy of %s..." % archive_path)
      os.remove(archive_path)

### Step 5: finally, remove all project backups other than the last
###         NUM_BACKUPS.

if num_backups > 0:
  regexp = re.compile("^" + project + "-\d{4}-\d{2}-\d{2}-\d{2}:\d{2}:\d{2}" + ext_re + "$")
  
  directory_list = os.listdir(backup_dir)
  old_list = [x for x in directory_list if regexp.search(x)]
  old_list.sort(comparator)
  del old_list[max(0,len(old_list)-num_backups):]
  for item in old_list:
    old_backup_item = os.path.join(backup_dir, item)
    print("Removing old backup: " + old_backup_item)
    if os.path.isdir(old_backup_item):
      safe_rmtree(old_backup_item, 1)
    else:
      os.remove(old_backup_item)
      
  if bucket:
    # remove extra copies from s3 also
    old_list = [x for x in bucket.list() if regexp.search(x.name)]
    old_list.sort(lambda x, y: comparator(x.name,y.name))
    del old_list[max(0,len(old_list)-num_backups):]
  for item in old_list:
    print("Removing old S3 backup: " + item.key)
    item.delete()
    
