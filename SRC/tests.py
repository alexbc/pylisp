import ulispcore
import unittest

#testing module, used to give everything unit tests 
class coretests(unittest.TestCase):
	def setUp(self):
		self.samplecases = (("(+ 1 4)", 5, "Testing adding"),
		("(* 2 3)", 7, "Testing multiplication")
		)

		print "Starting tests...."

	def testsamplecases(self):
		for evalstring, result, reason in self.samplecases:
			self.assertEqual(ulispcore.eval(evalstring), result, reason)

def dotest(verb):
	suite = unittest.TestLoader().loadTestsFromTestCase(coretests)
	unittest.TextTestRunner(verbosity=verb).run(suite)

if __name__ == '__main__':
	dotest(0) #do a test



