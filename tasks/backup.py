"""Tool functions for backups.

This module does not include any tasks, only functions.

"""

import os
import re
import time

def get_stamp():
    return time.strftime('%Y-%m-%d-%H:%M:%S')

def get_stamp_regexp(basename, ext):
    rexp = "^(?P<datetime>\d{4}-\d{2}-\d{2}-\d{2}:\d{2}:\d{2})-" + basename + '(' + ext + ")$"
    return re.compile(rexp)

def gen_file_name(basename):
    return "%s-%s" % (get_stamp(), basename)

def rm_file(filename):
    if not os.path.isfile(filename):
        raise Exception('Can not remove non-existing file: ' + filename)
    return os.remove(filename)

def rm_old_files(dirname, basename, ext, num_delete=64):
  regexp = get_stamp_regexp(basename, ext)

  def compare_files(a, b):
    matcha = regexp.search(a)
    matchb = regexp.search(b)
    reva = matcha.groupdict()['datetime']
    revb = matchb.groupdict()['datetime']
    if (reva < revb):
        return -1
    else:
        return 1

  directory_list = os.listdir(dirname)
  old_list = [x for x in directory_list if regexp.search(x)]
  old_list.sort(compare_files)
  del old_list[max(0,len(old_list)-num_delete):]
  for item in old_list:
    old_backup_item = os.path.join(dirname, item)
    print("Removing old backup: " + old_backup_item)
    if os.path.isdir(old_backup_item):
      safe_rmtree(old_backup_item, 1)
    else:
      os.remove(old_backup_item)


# Chmod recursively on a whole subtree
#def chmod_tree(path, mode, mask):
  #def visit(arg, dirname, names):
    #mode, mask = arg
    #for name in names:
      #fullname = os.path.join(dirname, name)
      #if not os.path.islink(fullname):
        #new_mode = (os.stat(fullname)[stat.ST_MODE] & ~mask) | mode
        #os.chmod(fullname, new_mode)
  #os.path.walk(path, visit, (mode, mask))

# For clearing away read-only directories
#def safe_rmtree(dirname, retry=0):
  #"Remove the tree at DIRNAME, making it writable first"
  #def rmtree(dirname):
    #chmod_tree(dirname, 0666, 0666)
    #shutil.rmtree(dirname)

  #if not os.path.exists(dirname):
    #return

  #if retry:
    #for delay in (0.5, 1, 2, 4):
      #try:
        #rmtree(dirname)
        #break
      #except:
        #time.sleep(delay)
    #else:
      #rmtree(dirname)
  #else:
    #rmtree(dirname)
