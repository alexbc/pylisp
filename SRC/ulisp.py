#!/usr/bin/env python2.5
from ulispcore import eval, logging, LOG_FILE
import sys
import getopt

def REPL():
	print "Welcome to Ulisp v0"
	print "Please enter a Sexpression into the console below"
	print "Type a blank line to exit"
	print

	while 1:
		inp = raw_input(">> ")
		if inp == "":
			break
		print eval(inp)

	print "Thank you for flying lisp"
	print


def runfile(fname):
	print eval(open(fname).read())

def setupdebug(debugmode):
	global logging
	global LOG_FILE
	
	LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


	logging.basicConfig(filename=LOG_FILE,level=LEVELS[debugmode], filemode="w")
	
	console = logging.StreamHandler()
	console.setLevel(logging.WARNING)
	# set a format which is simpler for console use
	formatter = logging.Formatter('%(levelname)-8s %(message)s')
	# tell the handler to use this format
	console.setFormatter(formatter)
	# add the handler to the root logger
	logging.getLogger('').addHandler(console)

def usage():
	print """Usage
	-h (help) For help (this message)
	-i (interactive) for  REPL (default)
	-e (evaluate) to run an expression and exit
	-r (run) to run from a file and exit
	-d (debug) to change the debug settings from default
	-p (prelude) run file before starting the REPL
	-l (logfile) change output log file

	For more information please consult the documentation
	"""
	sys.exit()

def main(argv):
	global LOG_FILE
	try:
        	opts, args = getopt.getopt(argv, "hifdrple:t", ["help", "interactive", "file=", "debug=", "run=", "prelude=", "logfile=", "eval="])
	except getopt.GetoptError, err:
		usage() #if they give us bad arguments, give them a usage message
	
	#process arguments
	debugmode = "debug"

	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
		elif o in ("-r", "--run"):
			runfile(a)
			sys.exit()
		elif o == "--debug":
			if a in ['debug', 'info', 'warning', 'error', 'critical']:
				debugmode = a
			else:
				usage()
		elif o == "--prelude":
			runfile(a)
		elif o == "--logfile":
			LOG_FILE = a
		elif o == "--eval":
			expr = a
			print eval(expr)
			sys.exit()
		elif o == "-t":
			import tests #TODO Maybe change verbosity of tests depending on debug level?
			tests.dotest(2)
			sys.exit()
	
	#once everything is processed, set up the log files and run the REPL
	setupdebug(debugmode)
	REPL()
			

if __name__ == "__main__":
	main(sys.argv[1:])	
