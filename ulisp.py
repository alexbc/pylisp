import random


variables = {}
macros = {}
closures = {}
currentclosure = 0
closurestack = []

def closurestate():
	print "**********"
	print "Variables", variables
	print "closures", closures
	print "Currentclosure", currentclosure
	print "Closurestack", closurestack
	print "***********"

def changeclosure(changeto): #change closures
	global closures
	global currentclosure
	global variables

	closures[currentclosure] = variables
	variables = closures[changeto]
	currentclosure = changeto
	print "Changed closure to ", changeto
	print "Vars = ", variables

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

	print "Making a new closure"
	print variables
	cid = makeclosureid()
	closures[cid] = variables
	currentclosure = cid
	closurestack.append(cid)
	print cid

def retclosure():
	global closurestack
	
	print "Poping closure"
	if closurestack != []:
		cid = closurestack.pop()
		print cid
		changeclosure(cid)

	
def simpletreeparse(inp):
	"""Very simple Tree parser to seperate out sublists from lists"""
	numbrackets = 0
	slab = ""
	slabs = []
	quotes = False
	WHITESPACE = [' ', '\t', '\n']
	for i in inp:
		if i == "(" and not quotes:
			numbrackets += 1
			slab += i
		elif i == ")" and not quotes:
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
			if i == '"':
				quotes = not quotes

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
	print name, value
	return value

def let(args):
	assert len(args) == 3, "Need three args to let!"
	global variables
	makeclosure()
	name = args[0]
	value = eval(args[1])
	variables[name] = value
	ret = eval(args[2], variables)
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
	print macros[macroname]

def println(args):
	print " ".join([str(x) for x in args])

def readln(args):
	prmpt = ""
	print args, len(args)
	if len(args) > 0:
		prmpt = args[0]
	return raw_input(prmpt)

def fn(args):
	global variables, currentclosure
	assert len(args) == 2, "ERROR fn requires 2 arguments!"
	varsets = args[0]
	body = args[1]
	varsets = makelist(varsets)
	print "Making new lambda"
	print "Variables", variables
	

	def newfunc(args, varsets, cl):
		closurestate() #tell us wtf is happening
		changeclosure(cl) #change to the closure we should be in
		makeclosure() #make this a new closure
		print "*LAMBDA EVAL*", args
		print "*LAMBDA VARS*", vars, id(vars)
		print "*LAMBDA VARSETS*", varsets
		for i in range(len(args)):
			print i
			vars[varsets[i]] = args[i]

		ret = eval(body, vars)
		print "*LAMBDA RET*", ret
		retclosure()
		retclosure()
		
		return ret
		

	return lambda x: newfunc(x, varsets, currentclosure)

def makelist(inp): #useful for fn and macros/etc. stuffs up lists of lists badly
	inp = inp.replace("(", "") #remove brackets to allow varsets to be parsed properly
        inp = inp.replace(")", "")
        inp = inp.split(" ")
	return inp
	
def evallist(args):
	print "*EVALLIST*", args
	return map(eval, args)[-1]

noeval = ['macro', 'setq', 'let', 'lambda', 'eval', 'if', 'and' 'or', '>', '<', '=']
fns = {'+' : plus, 'setq' : setq, 'cons' : cons, 'first': first, 'rest':rest, 'do': do, 'eval' : evalwrapper, 'lambda':fn, 'let': let, '=' : eq, '>' : gth, '<': lth, 'if' : doif, 'and': doand, 'or' : door, 'macro': macro, 'println': println, 'readln': readln}

def eval(inp, vars=None):
	if not vars:
		vars = variables

	inp = inp.strip() #get rid of leading/trailing spaces
	if not inp: #if we have nothing to do
		return #return nothing

	print "*EVAL* Evaling", inp
	print "*EVAL* variables", vars
	islist = (inp[0] == "(" and inp[-1] == ")")
	if islist: #this is a list, so strip it
		if len(simpletreeparse(inp)) > 1:
			print "MUTLILIST"
			#this isn't one list, its many!
			return evallist(simpletreeparse(inp))
                inp = inp[1:-1].strip()

	print "Stripped inp", inp
	if inp in vars: #its a variable
                print "*EVAL* Found variable ", inp, "=", vars[inp]
                return vars[inp]

	if convertint(inp): #its an int
		print "*EVAL* Found int", inp
		return convertint(inp)

	if inp[0] == "'": #this is quoted
		inp = inp[1:]
		print "*EVAL* Found quote '", inp
		return simpletreeparse(inp)

	if inp[0] == '"' and inp[-1] == '"' and inp.count('"') == 2: #its a double quoted string
		inp = inp[1:-1]
		print "*EVAL* Found quoted string '" + inp + "'"
		return inp
	
	if not islist: #this isn't a list, there really is nothing to do here
		print "Unknown symbol", inp
		return
		

	tree = simpletreeparse(inp)

	function = tree[0] #function is always the first argument
	args = tree[1:] #arguments are the rest

	print "function = ", function

	if function in fns:
		fn = fns[function]
		print "Found in function table"
	elif type(eval(function)) == type(lambda x:x): #we've been given an actual function to run
		fn = eval(function)
		print "Is a lambda function"
	elif function in macros:
		#do macro expansion, so expand it and eval it
		print "Is a macro"
		return eval(macroexpand(macros[function]['body'],  macros[function]['args'], args))
	else:
		print "Not a function", function
		tree = map(eval, tree)
		return tree

	if function not in noeval:
		args = map(eval, args)
	print "*EVAL* args = ", repr(args)
	ret  = fn(args)
	print "*EVAL* RETURNS ", ret
	return ret


def macroexpand(body, arglist, args):
	"""Expand macros, todo: FIXME"""

	WHITESPACE = [' ', '\n', '\t']
	for white in WHITESPACE:
		body = body.replace(white, ' ')

	for i in range(len(arglist)):
		body = body.replace(" " + arglist[i] + " ", " " + args[i] + " ")

	print "*MACRO* Expanded to", body
	return body


while 1:
	inp = raw_input(">> ")
	if inp == "":
		break
	print eval(inp, variables)
	print variables
