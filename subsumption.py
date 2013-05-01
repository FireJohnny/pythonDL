# Module which provides functions for answering a variety of queries, given
# a module that provides an implementation of the subsumedby function
# Tyler Adams
# tyler.r.adams@gmail.com
# April 2013

import dlobjects as dl
import copy

'''
def _test():
	import simplestructuralsubsumption as ss
	import textexpressionparser as parser
	qprocessor = SubsumptionQueryProcessor(ss)
	'''

def _transitiveClosure(concepts):
	'''Given a list of subsumedby tuples, compute the transitive closure.
	Credit to answer by soulcheck, found at 
	http://stackoverflow.com/questions/8673482/transitive-closure-python-tuples'''
	closure  = set(concepts)
	while True:
		new_tuples = set((x,w) for x,y in closure for q,w in closure if q == y)
		new_closure = closure | new_tuples
		if closure == new_closure:
			break
		closure = new_closure
	return closure


class SubsumptionQueryProcessor:
	def __init__(self, simpl):
		self.simpl = simpl
		
	def subsumedby(self, e0, e1):
		return self.simpl.subsumedby(e0, e1)
		
	def equivalent(self, e0, e1):
		return self.simpl.subsumedby(e0, e1) and self.simpl.subsumedby(e1, e0)
	
	def disjoint(self, e0, e1):
		return not self.satisfiable(dl.ConjunctiveExpression(copy.deepcopy(e0), copy.deepcopy(e1)).normalize())
		
	def satisfiable(self, e0):
		return not self.simpl.subsumedby(e0, dl.BOTTOM)
		
		
	def allSubsumption(self, concepts, returnValues=False):
		'''Return all non-reflexive subsumption relationships, including transitive relationships.'''
		return _transitiveClosure(list(self._allDirectSubsumption(concepts, returnValues)))
	
	def _allDirectSubsumption(self, concepts, returnValues=False):
		'''Generator for all direct (non-transitive) subsumedby relationships in a group of concepts, omitting
		reflexive pairs.  To obtain all transitive pairs, supply the output from this function to the transitiveClosure
		function.'''
		try:
			for key0, value0 in concepts.iteritems():
				for key1, value1 in concepts.iteritems():
					if key0 != key1 and self.simpl.subsumedby(value0, value1):
						yield (value0, value1) if returnValues else (key0, key1)
		except:
			for i in range(0, len(concepts)):
				for j in range(0, len(concepts)):
					if (i != j) and self.simpl.subsumedby(concepts[i], concepts[j]):
						yield (concepts[i], concepts[j]) if returnValues else (i, j)
		