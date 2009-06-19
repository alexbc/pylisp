inp = "((fn (x y) (+ x y)) 2 3) "

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
	value = args[1]
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

	print "varsets", varsets
	print "body", body
	def newfunc(args):
		global variables
		oldvars = variables
		print args
		print variables
		print varsets
		for i in range(len(args)):
			print i
			variables[varsets[i]] = args[i]

		print "Variables", variables
		print "Body", body
		ret = eval(body)
		variables = oldvars
		print "LAMBDA FUNCTION RAN", ret
		return ret
		

	return newfunc

noeval = ['setq', 'fn']

fns = {'+' : plus, 'setq' : setq, 'cons' : cons, 'first': first, 'rest':rest, 'do': do, 'eval' : evalwrapper, 'fn':fn}
variables = {'x': 100}

def eval(inp, vars=variables):
	inp = inp.strip() #get rid of leading/trailing spaces

	print "Evaling ", inp
	if convertint(inp): #its an int
		print "Found int", inp
		return convertint(inp)

	if inp in vars: #its a variable
                print "Found variable ", inp, "=", vars[inp]
                return vars[inp]

	inp = inp[1:-1].strip()
	if inp[0] == "'": #this is quoted
		inp = inp[1:]
		print "Found quoted string '", inp, "'"
		return inp


	tree = simpletreeparse(inp)

	function = tree[0]
	args = tree[1:]

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
	print "args = ", repr(args)
	ret  = fn(args)
	print "return value = ", ret
	return ret

	

print eval(inp)
print variables
