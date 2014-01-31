#!/usr/bin/env python2
# this doesnt work yet
# Jan 31, 2014

# Description:          This is a yaml linter which validates the path to a yaml file,
#                       a directory full of yaml files, or a recursive search of yaml files.
# Usage     :
#           - Check a single file:
#             python /home/jon/blah.py '/tmp/path/to/file.yaml'
#           - Check a whole directories YAML files
#             python /home/jon/blah.py '/tmp/path/to/*.yaml'
#           - Recursively heck a whole directories YAML files
#             python /home/jon/blah.py -r '/tmp/*.yaml'

from yaml import load
from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import sys, os, fnmatch
import argparse
print "this doesnt work yet"
sys.exit(0)
parser = argparse.ArgumentParser(description='This program will search for file or files in a' + 
                                             ' directory that are specified as yaml, and then' +
                                             ' validates them using the yaml library.')

parser.add_argument('-r','-R','--recursive', action='store_true', help='Search with recursivity.', default=False, required=False)
parser.add_argument('directory', nargs='?')

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def readFromFile(inputfile):
    pureyaml = []
    with open(inputfile, "r") as f:         
        for line in f.readlines():
            li=line.lstrip()
            if not li.startswith('{'):
            	pureyaml.append(li)
    return ''.join(pureyaml)

def yamlSanityCheck(filei,inputstr):
	""" This will take a single file path and open it with
	    yaml parser, and exceptions will be thrown if the yaml
	    file is insane.

	    >> yamlSyntaxCheck('/tmp/file.yml')
	    << Return: True (if no errors)
	    else an exceptions
	    """
	try:
		#load( open(inputfile, 'r'), Loader=Loader)
		load(inputstr, Loader=Loader)
	except Exception, trace:
		sys.stderr.write(bcolors.FAIL + "[ FAIL ]   " + 
						 bcolors.ENDC + filei + 
						 "\nException: " + str(trace) + "\n")
		return False

	print bcolors.OKGREEN + "[  OK  ]   " + bcolors.ENDC + filei
	return True

def findFiles(directory, pattern, recurse):
	""" I cant figure out list comprehension for if recurse == true, so performance will suffer. """
	matches = []
	if recurse:
		for root, dirs, files in os.walk(directory):
			for basename in files:
				if fnmatch.fnmatch(basename, pattern):
					filename = os.path.join(root, basename)
					matches.append(filename)
	else:
		#matches = directory + [fn for fn in os.listdir(directory) if fnmatch.fnmatch(fn, pattern)]
		for fn in os.listdir(directory):
			if fnmatch.fnmatch(fn, pattern) and not os.path.isdir(fn):
				matches.append(directory + "/" + fn)
	return matches

def main():
	args = vars(parser.parse_args())

	# Arg parsing...
	path = args['directory']
	try:
		(directory, pattern) = os.path.split(args['directory'])
	except AttributeError:
		raise AttributeError("Missing last arguement?")
	if pattern == '':
		pattern = '*'
	recurse = args['recursive']

	# WHERES THE LINT
	exitvalue = 0
	for dafile in findFiles(recurse=recurse,directory=directory,pattern=pattern):
		if not yamlSanityCheck(dafile,readFromFile(dafile)):
			exitvalue = 255

	sys.exit(exitvalue)

if __name__ == "__main__":
	main()
