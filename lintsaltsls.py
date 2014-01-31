#!/usr/bin/env python2
# --------------------
# Jan 31, 2014
#
# Description:          This is a sls/yaml linter which validates the path to a sls/yaml file,
#                       a directory full of sls/yaml files, or a recursive search of yaml files.
# Target Audiance:      To those who use salt and manage salt.sls files, to ensure a strict yaml
#                       syntax.
# Usage     :
#           - Check a single file:
#             python /home/jon/blah.py '/tmp/path/to/file.yaml'
#           - Check a whole directories YAML files
#             python /home/jon/blah.py '/tmp/path/to/*.yaml'
#           - Recursively heck a whole directories YAML files
#             python /home/jon/blah.py -r '/tmp/*.yaml'

# Output example:
# jon@epoch2 /tmp/python-tools $ python /tmp/python-tools/lintsaltsls.py -R /tmp/chunky-salt/*.sls
# [  OK  ]   /tmp/chunky-salt/pillar/env.sls
# [  OK  ]   /tmp/chunky-salt/pillar/top.sls
# [  OK  ]   /tmp/chunky-salt/pillar/region.sls
# [ FAIL ]   /tmp/chunky-salt/pillar/nodes.sls
# Exception: while parsing a block mapping
#   in "<string>", line 1, column 1:
#     nodes:
#     ^
# expected <block end>, but found '-'
#   in "<string>", line 5, column 1:
#     - name: cache-n01.staging.inova. ... 
#     ^
# [  OK  ]   /tmp/chunky-salt/pillar/users.sls
# [  OK  ]   /tmp/chunky-salt/modules/top.sls
# [  OK  ]   /tmp/chunky-salt/modules/roles/lb_server/init.sls
# [  OK  ]   /tmp/chunky-salt/modules/roles/lb_server/nginx.sls
# [  OK  ]   /tmp/chunky-salt/modules/roles/cache_server/init.sls
# [  OK  ]   /tmp/chunky-salt/modules/roles/cache_server/memcached.sls
# [  OK  ]   /tmp/chunky-salt/modules/roles/salt_server/salt_server.sls
# [  OK  ]   /tmp/chunky-salt/modules/roles/salt_server/init.sls
# [  OK  ]   /tmp/chunky-salt/modules/roles/chunky_server/mongo.sls

# ===============================================
# Common Error Causes:
# Exception: while scanning a simple key
#  in "<string>", line 64, column 1:
#    pkg.installed
# --
# Problem:
#  apache:
#    pkg.installed
# (NOT VALID YAML)
# Solution:
#  apache:
#    pkg:
#      - installed
#    service:
#      - running
#      - watch:
#        - pkg: apache
#        - file: /etc/httpd/conf/httpd.conf
#        - user: apache
# --

from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper  # pyaml rocks
except ImportError:
    from yaml import Loader, Dumper  # stdlib yaml meh.

import sys
import os
import fnmatch
import argparse

parser = argparse.ArgumentParser(description='This program will search for file or files in a' +
                                             ' directory that are specified as yaml, and then' +
                                             ' validates them using the yaml library.')

parser.add_argument('-r', '-R', '--recursive', action='store_true',
                    help='Search with recursivity.', default=False, required=False)
parser.add_argument('-q', '--quiet', action='store_true', help='Quiet -- only output failures.', default=False, required=False)
parser.add_argument('-s', '--silent',  action='store_true', help='Silent -- output nothing.', default=False, required=False)
parser.add_argument('directory', nargs='?')


class bcolors:
    """ Ansi color hax """
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def readFromFile(inputfile):
    """ Returns a string from a file, less specific lines,
        used to filter out salt JINJA macros. i.e.:
        {  starting on a line defines something
        {{ }} keys with this are usually variables
    """
    pureyaml = []
    with open(inputfile, "r") as f:         
        for line in f.readlines():
            li=line.lstrip()
            if li.startswith('{'):
                pass
            elif "{{" in li and '}}' in li:
               pass
            else:
                pureyaml.append(li)

    return ''.join(pureyaml)

def yamlSanityCheck(filei,inputstr,quiet,silent):
    """ This will take a single file path and open it with
        yaml parser, and exceptions will be thrown if the yaml
        file is insane.

        >> yamlSyntaxCheck('/tmp/file.yml')
        << Return: True (if no errors)
        else an exceptions
        """
    if os.path.basename(filei) == "nodes.sls":
        if quiet or silent:
            pass
        else:
            print bcolors.OKBLUE + "[ SKIP ]   " + bcolors.ENDC + filei
    else:
        try:
            # load( open(inputfile, 'r'), Loader=Loader)
            load(inputstr, Loader=Loader)
            if quiet or silent:
                pass
            else:
                print bcolors.OKGREEN + "[  OK  ]   " + bcolors.ENDC + filei
        except Exception, trace:
            if not silent:
                sys.stderr.write(bcolors.FAIL + "[ FAIL ]   " + 
                             bcolors.ENDC + filei + 
                             "\nException: " + str(trace) + "\n")
            return False

    return True

def findFiles(directory, pattern, recurse):
    """ This will take a directory and a pattern to search for, and will find all files
        matching a pattern in that directory. It will recurse into sub directories if recurse=True
        """
    """ I cant figure out list comprehension for if recurse == true, so performance will suffer. """
    matches = []
    if recurse:
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    matches.append(filename)
    else:
        # matches = directory + [fn for fn in os.listdir(directory) if fnmatch.fnmatch(fn, pattern)]
        for fn in os.listdir(directory):
            if fnmatch.fnmatch(fn, pattern) and not os.path.isdir(fn):
                matches.append(directory + "/" + fn)
    return matches

def main():
    """ Guess what this does """
    args = vars(parser.parse_args())

    # Arg parsing...
    path = args['directory']
    (directory, pattern) = os.path.split(args['directory'])
    if pattern == '':
        pattern = '*'
    recurse = args['recursive']
    quiet_bit = args['quiet']
    silent_bit = args['silent']

    # WHERES THE LINT
    exitvalue = 0
    for dafile in findFiles(recurse=recurse,directory=directory,pattern=pattern):
        if not yamlSanityCheck(filei=dafile,inputstr=readFromFile(dafile),quiet=quiet_bit,silent=silent_bit):
            exitvalue = 255

    sys.exit(exitvalue)

if __name__ == "__main__":
    main()
