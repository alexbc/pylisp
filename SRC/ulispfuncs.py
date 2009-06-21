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
