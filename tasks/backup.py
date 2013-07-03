"""Tool functions for backups.

This module does not include any tasks, only functions.

"""

import os
import re
import time

def get_stamp():
    """Returns timestamp for backup file names."""
    return time.strftime('%Y-%m-%d-%H:%M:%S')

def get_stamp_regexp(basename, strict=False):
    """Returns regexp to find backup files with the same basename."""
    rexp = "^(?P<datetime>\d{4}-\d{2}-\d{2}-\d{2}:\d{2}:\d{2})-" + basename
    if strict:
      rexp += "$"
    return re.compile(rexp)

def gen_file_name(basename):
    """Generage backup file name for given basename."""
    return "%s-%s" % (get_stamp(), basename)

def rm_file(filename):
    """Removes file. Raises an exception if passed name is not file."""
    if not os.path.isfile(filename):
        raise Exception('Can not remove non-existing file or non-file: ' + filename)
    return os.remove(filename)

def rm_old_files(dirname, basename, num_keep=64, strict=False):
    """Removes old backup files.

        dirname     -- directory name to scan
        basename    -- backup base name
        num_keep    -- number of backups to keep
        strict      -- whether to do strict comparison when searching for backups;
                       if it is set then basename should include complete backup file name
                       after date timestamp (including extension);
                       if it is not set then basename can be used without extension - this
                       way, for example, backups of the same project archived with
                       tar.gz and zip will be treated as the same backups set.
    """
    regexp = get_stamp_regexp(basename, strict)

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
    del old_list[max(0,len(old_list)-num_keep):]
    for item in old_list:
        old_backup_item = os.path.join(dirname, item)
        print("Removing old backup: " + old_backup_item)
        rm_file(old_backup_item)
