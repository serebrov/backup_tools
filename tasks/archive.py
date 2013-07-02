"""Tasks and utility functions and classes for archives."""

#from __future__ import with_statement
#import re

import optparse
import os
import backup
from paver.easy import *

# Archive types/extensions
archive_map = {
  'gz'  : ".tar.gz",
  'bz2' : ".tar.bz2",
  'zip' : ".zip"
  }

@task
@cmdopts([
    optparse.make_option('--archive_type', default='gz', help='Archive type: gz or bz2'),
    optparse.make_option('--name', default='backup', help='Backup file name'),
    optparse.make_option('-s', '--src', help='Source file/dir destination'),
    optparse.make_option('-d', '--dest', help='Target archive destination directory')
])
def gz(options):
    """Archives the file or dir."""
    # ./paver gz --name=test -s ./README.md -d ./
    #print options
    src = os.path.abspath(options.src)
    ext = archive_map[options.archive_type]
    dest = os.path.join(os.path.abspath(options.dest), backup.gen_file_name(options.name+ext))

    import tarfile
    tar = tarfile.open(dest, 'w:' + options.archive_type)
    tar.add(src, os.path.basename(src))
    tar.close()
    print dest
    return dest


@task
@cmdopts([
    optparse.make_option('--name', default='backup', help='Backup file name'),
    optparse.make_option('-s', '--src', help='Source file/dir destination'),
    optparse.make_option('-d', '--dest', help='Target archive destination directory')
])
def zip(options):
    """Archives the file or dir."""
    src = os.path.abspath(options.src)
    ext = archive_map['zip']
    dest = os.path.join(os.path.abspath(options.dest), backup.gen_file_name(options.name+ext))

    import zipfile
    zp = zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED)
    if os.path.isfile(src):
        zp.write(src, os.path.basename(src))
    else:
        os.path.walk(src, add_to_zip, (zp, src))
    zp.close()
    print dest
    return dest

def add_to_zip(baton, dirname, names):
    zp = baton[0]
    root = os.path.join(baton[1], '')

    for file in names:
        path = os.path.join(dirname, file)
        if os.path.isfile(path):
            zp.write(path, path[len(root):])
        elif os.path.isdir(path) and os.path.islink(path):
            os.path.walk(path, add_to_zip, (zp, path))

@task
@cmdopts([
    optparse.make_option('--archive_type', default='gz', help='Archive type: gz or bz2'),
    optparse.make_option('--name', default='backup', help='Backup file name'),
    optparse.make_option('-s', '--src', help='Source file/dir destination'),
    optparse.make_option('-d', '--dest', help='Target archive destination directory')
])
def compress(options):
    if options.archive_type == 'zip':
        return zip()
    else:
        return gz()
