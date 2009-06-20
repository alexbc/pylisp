inp = "(do (setq x (fn (x y) (+ x y))) (x 1 2))"

def simpletreeparse(inp):
	numbrackets = 0
	slab = ""
	slabs = []
	for i in inp:
		if i == "(":
			numbrackets += 1
			slab += i
		elif i == ")":
			numbrackets -= 1
			slab += i
		else:
			if i == " " and numbrackets == 0 :
				slabs.append(slab)
				slab = ""
			else:
				slab += i
	slabs.append(slab)
	return slabs

def plus(args):
	return reduce(lambda x,y: x+y, args)

def cons(args):
	return reduce(lambda x,y: x+y, args)
	
def first(args):
	return args[0]

def rest(args):
	return args[1:]

def setq(args):
	global variables
	name = args[0]
	value = eval(args[1])
	variables[name] = value
	print name, value
	return value

def convertint(inp):
	try:
		return int(inp)
	except:
		return

def do(args):
	return args[-1]

def evalwrapper(args):
	print "EVALARGS", args
	return map(eval, ["(" + x + ")" for x in args])

def fn(args):
	assert len(args) == 2, "ERROR fn requires 2 arguments!"
	varsets = args[0]
	body = args[1]
	varsets = varsets.replace("(", "") #remove brackets to allow varsets to be parsed properly
	varsets = varsets.replace(")", "") 
	varsets = varsets.split(" ")

	def newfunc(args):
		print "*LAMBDA EVAL*", args
		global variables
		oldvars = variables
		print args
		print variables
		print varsets
		for i in range(len(args)):
			print i
			variables[varsets[i]] = args[i]

		ret = eval(body)
		variables = oldvars
		print "*LAMBDA RET*", ret
		return ret
		

	return newfunc

noeval = ['setq', 'fn']

fns = {'+' : plus, 'setq' : setq, 'cons' : cons, 'first': first, 'rest':rest, 'do': do, 'eval' : evalwrapper, 'fn':fn}
variables = {'x': 100}

def eval(inp, vars=variables):
	inp = inp.strip() #get rid of leading/trailing spaces
	print "*EVAL* Evaling", inp

	if inp in vars: #its a variable
                print "*EVAL* Found variable ", inp, "=", vars[inp]
                return vars[inp]

	if convertint(inp): #its an int
		print "*EVAL* Found int", inp
		return convertint(inp)

	if inp[0] == "(" and inp[-1] == ")": #this is a list, so strip it
		inp = inp[1:-1].strip()
	
	if inp[0] == "'": #this is quoted
		inp = inp[1:]
		print "*EVAL* Found quote '", inp
		return simpletreeparse(inp)

	if inp[0] == '"' and inp[-1] == '"': #its a double quoted string
		inp = inp[1:-1]
		print "*EVAL* Found quoted string '" + inp + "'"
		return inp
		


	tree = simpletreeparse(inp)

	function = tree[0] #function is always the first argument
	args = tree[1:] #arguments are the rest

	print "function = ", function

	if function in fns:
		fn = fns[function]
	elif type(eval(function)) == type(lambda x:x): #we've been given an actual function to run
		fn = eval(function)
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

	

#print eval(inp)
#print variables

while 1:
	inp = raw_input(">> ")
	if inp == "":
		break
	print eval(inp)
