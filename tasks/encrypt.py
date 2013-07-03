"""Tasks and utility functions and classes for encryption."""

#from __future__ import with_statement

import optparse
import os
import backup
from paver.easy import *

@task
@cmdopts([
    optparse.make_option('--trust_model', default='always', help='gpg --trust-model parameter.'),
    optparse.make_option('--recipient', help='gpg --recipient parameter'),
    optparse.make_option('--user', help='gpg --local-user parameter'),
    optparse.make_option('-s', '--src', help='Source file/dir destination'),
    optparse.make_option('-d', '--dest', help='Target file destination directory')
])
def gnupg(options):
    """Encrypts file using gnupg.

       Install gnupg (on Ubuntu):

           $ sudo apt-get install gnupg

       This task will invoke gpg command like this:

          $ gpg --batch --trust-model always --recipient "Name <name@example.com>" --local-user "Name2 <name2@example.com>" --output file_name.gpg --encrypt file_name
    """
    # ./paver gnupg --recipient "User <user@example.com>" --user "User <user@example.com>" -s paver -d .
    src = os.path.abspath(options.src)
    src_name = os.path.basename(options.src)
    dest = os.path.join(os.path.abspath(options.dest), src_name+'.gpg')
    # do we need to make a file name with timestamp here? Usually we encrypt archive, so timestamp is already present. Maybe add an option?
    #dest = os.path.join(os.path.abspath(options.dest), backup.gen_file_name(src_name+'.gpg'))
    gpg_command = 'gpg --batch --trust-model %s --recipient "%s" --local-user "%s" --output %s --encrypt %s' % (options.trust_model, options.recipient, options.user, dest, src)
    sh(gpg_command)
    print dest
    return dest

