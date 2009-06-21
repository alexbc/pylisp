#!/usr/bin/env python2.5
import random
from types import FunctionType
import logging
import sys
import getopt

variables = {}
macros = {}
closures = {0: variables}
currentclosure = 0
closurestack = [0]

LOG_FILE = "Log.txt"
logger = logging.getLogger("ulisp_core")

class lambdafunction():
	def __init__(self, body, closureid, varset):
		self.body = body
		self.closureid = closureid
		self.varset = varset
	def __str__(self):
		return """
		******
		I am a lambda function
		Body %s
		closureid %s
		Varset %s
		******""" % (self.body, self.closureid, self.varset)

	def run(self, args):
		closurestate()
		global variables
		closurestate()
		changeclosure(self.closureid)
		makeclosure()
		closurestate()
		
		for i in range(len(args)):
                        variables[self.varset[i]] = args[i]

		ret = eval(self.body)
		retclosure()
		
		return ret


def closurestate():
	global logging
	logger = logging.getLogger("closure")
	logger.info("Variables = %r", variables)
	logger.info("closures = %r", closures)
	logger.info("Currentclosure = %s", currentclosure)
	logger.info("Closurestack = %s", closurestack)

def changeclosure(changeto): #change closures
	global closures
	global currentclosure
	global variables

	closures[currentclosure] = dict(variables)
	variables = closures[changeto]
	currentclosure = changeto

def makeclosureid():
	global closures
	while 1:
		cid = random.randrange(0, 2**16)
		if cid not in closures:
			return cid

def makeclosure(): #make a new closure and switch to it
	global variables
	global closures
	global closurestack
	global currentclosure

	cid = makeclosureid()
	closures[cid] = dict(variables)
	changeclosure(cid)
	closurestack.append(cid)

def retclosure():
	global closurestack
	global currentclosure

	if closurestack != []:
		cid = currentclosure
		while cid == currentclosure:
			cid = closurestack.pop()
			if closurestack == []:
				cid = 0
				break

		changeclosure(cid)
		

	
def simpletreeparse(inp):
	"""Very simple Tree parser to seperate out sublists from lists"""
	numbrackets = 0
	slab = ""
	slabs = []
	quotes = False
	WHITESPACE = [' ', '\t', '\n']
	ESCAPECHAR = '\\'
	escaped = False

	for i in inp:
		if i == ESCAPECHAR:
			escaped = True
			continue #its escaped so don't worry about this character and treat the next one as text

		if i == "(" and not quotes and not escaped:
			numbrackets += 1
			slab += i
		elif i == ")" and not quotes and not escaped:
			numbrackets -= 1
			slab += i
			if numbrackets == 0: #if, we've just closed brackets and are now on the last scope
				slabs.append(slab) #then treat it like a deliminator
				slab = ""

		else:
			if i in WHITESPACE and numbrackets == 0 and not quotes:
				if slab != "":
					slabs.append(slab)
					slab = ""
			else:
				slab += i
			if i == '"' and not escaped:
				quotes = not quotes
		escaped = False

	if slab != "":
		slabs.append(slab)

	slabs = [x.strip() for x in slabs] #get rid of any dangling whitespace
	slabs = [x for x in slabs if x != ""] #and get rid of any null entries
	return slabs

def eq(args):
	"""Equals, for any number of arguments"""

	for i in range(len(args) - 1):
		if eval(args[i]) != eval(args[i + 1]):
			return False
	return True

def gth(args):
	"""Greater than, for any number of arguments"""
	for i in range(len(args) - 1):
		if eval(args[i]) < eval(args[i + 1]):
			return False
	return True

def lth(args):
	"""Less than, for any number of arguments"""
	return ((not gth(args)) and not (eq(args)))

def doand(args):
	for i in range(len(args) - 1):
                if (not eval(args[i]) and eval(args[i + 1])):
                        return False
        return True

def door(args):
	for i in range(len(args) - 1):
		if eval(args[i]):
			return True
	return False

def plus(args):
	return reduce(lambda x,y: x+y, args)

def times(args):
	return reduce(lambda x,y: x*y, args)

def cons(args):
	return reduce(lambda x,y: x+y, args)
	
def first(args):
	return args[0]

def rest(args):
	return args[1:]

def setq(args):
	assert len(args) == 2, "Need two args to setQ!"
	global variables
	name = args[0]
	value = eval(args[1])
	variables[name] = value
	return value

def let(args):
	assert len(args) == 3, "Need three args to let!"
	global variables
	makeclosure()
	closurestate()
	name = args[0]
	value = eval(args[1])
	variables[name] = value
	ret = eval(args[2])
	closurestate()
	retclosure()
	return ret
	

def convertint(inp):
	try:
		return int(inp)
	except:
		return

def do(args):
	return args[-1]

def evalwrapper(args):
	return map(eval, args)

def doif(args):
	assert len(args) == 3, "Must have three arguments to if"
	expr = eval(args[0])
	if expr:
		return eval(args[1])
	else:
		return eval(args[2])

def macro(args):
	assert len(args) == 3, "Must have three arguments for macro"
	macroname =  args[0]
	arglist = makelist(args[1])
	body =  args[2]
	macros[macroname] = {'body': body, 'args': arglist}

def println(args):
	global logger
	output = " ".join([str(x) for x in args])
	print output
	logger.info("Printed %r", args)
	

def readln(args):
	prmpt = ""
	if len(args) > 0:
		prmpt = args[0]
	return raw_input(prmpt)

def fn(args):
	global variables, currentclosure
	assert len(args) == 2, "ERROR fn requires 2 arguments!"
	varsets = args[0]
	body = args[1]
	varsets = makelist(varsets)

	lam = lambdafunction(body, currentclosure, varsets)
	return lam.run

def makelist(inp): #useful for fn and macros/etc. stuffs up lists of lists badly
	inp = inp.replace("(", "") #remove brackets to allow varsets to be parsed properly
        inp = inp.replace(")", "")
        inp = inp.split(" ")
	return inp
	
def evallist(args):
	global logger
	logger.info("EVALLIST evaling %r", args)
	return map(eval, args)[-1]


noeval = ['macro', 'setq', 'let', 'lambda', 'eval', 'if', 'and' 'or', '>', '<', '=']
fns = {'+' : plus, 'setq' : setq, 'cons' : cons, 'first': first, 'rest':rest, 'do': do, 'eval' : evalwrapper, 'lambda':fn, 'let': let, '=' : eq, '>' : gth, '<': lth, 'if' : doif, 'and': doand, 'or' : door, 'macro': macro, 'println': println, 'readln': readln, '*': times}

def eval(inp):
	global variables
	global logging
	logger = logging.getLogger("eval")

	logger.info("Evaling %s" ,inp)
	logger.info("Have variables %r" , variables)
        if inp.count("(") != inp.count(")"): #there is at least one mismatched bracket
		logger.error("Mismatched brackets!")
		return

	inp = inp.strip() #get rid of leading/trailing spaces
	if not inp: #if we have nothing to do
		return #return nothing

	islist = (inp[0] == "(" and inp[-1] == ")")
	if islist: #this is a list, so strip it
		if len(simpletreeparse(inp)) > 1:
			#this isn't one list, its many!
			return evallist(simpletreeparse(inp))
                inp = inp[1:-1].strip()

	if inp in variables: #its a variable
                logger.info("Found variable %s = %r", inp, variables[inp]) #%r = repr
                return variables[inp]

	if convertint(inp): #its an int
		logger.info("Found int %s", inp)
		return convertint(inp)

	if inp[0] == "'": #this is quoted
		inp = inp[1:]
		logger.info("Found quote '%s", inp)
		return simpletreeparse(inp)
	
	#why was the inp.count('"') == 2 here?
	if inp[0] == '"' and inp[-1] == '"': #its a double quoted string
		inp = inp[1:-1]
		logger.info("Found quoted string '%s'", inp)
		return inp
	
	if not islist: #this isn't a list, there really is nothing to do here
		logger.error("Unknown symbol '%s'", inp)
		return
		

	tree = simpletreeparse(inp)

	function = tree[0] #function is always the first argument
	args = tree[1:] #arguments are the rest

	logger.info("function = %s", str(function))

	if function in fns:
		fn = fns[function]
		logger.info("Found in function table")
	elif callable(eval(function)): #we've been given an actual function to run
		fn = eval(function)
		logger.info("Is a lambda function")
	elif function in macros:
		#do macro expansion, so expand it and eval it
		logger.info("Is a macro")
		return eval(macroexpand(macros[function]['body'],  macros[function]['args'], args))
	else:
		logger.info("Not a function %s!", function)
		tree = map(eval, tree)
		return tree

	if function not in noeval:
		args = map(eval, args)
	logger.info("args = %r", args)
	ret  = fn(args)
	logger.info("eval returns %r ", ret)
	return ret


def macroexpand(body, arglist, args):
	"""Expand macros, todo: very hackish method, change."""
	global logging
        logger = logging.getLogger("eval")
        logger.info("Macro body %r arglist %r args %r", body, arglist, args)

	WHITESPACE = [' ', '\n', '\t']
	for white in WHITESPACE:
		body = body.replace(white, ' ')

	for i in range(len(arglist)):
		body = body.replace(" " + arglist[i] + " ", " " + args[i] + " ")
		body = body.replace(" " + arglist[i] + ")", " " + args[i] + ")")
		body = body.replace("(" + arglist[i] + " ", "(" + args[i] + " ")
		body = body.replace("(" + arglist[i] + ")", "(" + args[i] + ")")


	logger.info("Expanded to %s", body)
	return body


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



def main(argv):
	global LOG_FILE
	try:
        	opts, args = getopt.getopt(argv, "hifdrple", ["help", "interactive", "file=", "debug=", "run=", "prelude=", "logfile=", "eval="])
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
	
	#once everything is processed, set up the log files and run the REPL
	setupdebug(debugmode)
	REPL()
			

if __name__ == "__main__":
	main(sys.argv[1:])	
