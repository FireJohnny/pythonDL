# Module containing the implementation of the simple structural subsumption algorithm
# Tyler Adams
# tyler.r.adams@gmail.com
# April 2013

import dlobjects as dl
import textexpressionparser as dlparser


def _test():
	parser = dlparser.TextExpressionParser()
	tests = [
				('Person and Cow', 'Person'),
				('Person and Cow', '~Person'),
				('~Person and Cow', '~Person'),
				('~(Person or Cow)', '~Cow'),
				('Person and hasChild.hasChild.Person', 'Person and hasChild.hasChild.top'),
				('Person and hasChild.hasChild.~Person', 'Person and hasChild.hasChild.top'),
				('Person and hasChild.hasChild.Person', 'Person and hasChild.hasChild.bottom'),
				]
	for test in tests:
		print 'test: is', "'"+test[0]+"'(A)", 'subsumed by', "'"+test[1]+"'(B)?"
		(tokens0, tokens1) = (parser._getParser().parseString(test[0]), parser._getParser().parseString(test[1]))
		(n0, n1) = (parser._createObjectTree(tokens0[0]).normalize(), parser._createObjectTree(tokens1[0]).normalize())
		print 'tokenized (subsumed):', tokens0
		print 'tokenized (subsumer):', tokens1
		print 'normalized (subsumed):', n0
		print 'normalized (subsumer):', n1
		print 'A', 'IS' if subsumedby(n0, n1) else 'IS NOT', 'subsumed by B'
		print 
		

def __renderClauses(expression):
	if isinstance(expression, dl.LiteralExpression) or isinstance(expression, dl.ValueRestrictedExpression) or expression == dl.BOTTOM or expression == dl.TOP:
		return [expression]
	else:
		if isinstance(expression, dl.ConjunctiveExpression):
			return __renderClauses(expression.left) + __renderClauses(expression.right)
		else:
			raise TypeError('Error on expression ' + expression.__repr__() + ', Clauses other than concept names and value restrictions are not supported by this algorithm')
		
def __splitClauses(clauses):
	conceptNames = []
	valueRestrictions = []
	
	for clause in clauses:
		if isinstance(clause, dl.ValueRestrictedExpression):
			valueRestrictions.append(clause)
		elif isinstance(clause, dl.LiteralExpression):
			conceptNames.append(clause)
		else:
			raise TypeError('Clauses other than concept names and value restrictions are not supported by this algorithm')

	return (conceptNames, valueRestrictions)
	
def subsumedby(e0, e1):
	''' return whether e0 is subsumed by e1 '''
	if e0 == e1 or e1 == dl.TOP or e0 == dl.BOTTOM:
		return True
		
	if e1 == dl.BOTTOM or e0 == dl.TOP:
		return False
		
	try:
		if e0.universal and e1.universal:
			return (e0.roleName == e1.roleName) and subsumedby(e0.subExpression, e1.subExpression)
		else:
			raise TypeError('Existential quantification is not supported by this algorithm.')
	except Exception:
		pass
	
	(subsumerConcepts, subsumerVRs) = __splitClauses(__renderClauses(e1))
	(subsumedConcepts, subsumedVRs) = __splitClauses(__renderClauses(e0))
	
	for subsumerConcept in subsumerConcepts:
		match = False
		for subsumedConcept in subsumedConcepts:
			if subsumerConcept == subsumedConcept:
				match = True
				break
		
		if not match:
			return False
	
	for subsumerVR in subsumerVRs:
		match = False
		for subsumedVR in subsumedVRs:
			if (subsumerVR.roleName == subsumedVR.roleName) and subsumedby(subsumedVR.subExpression, subsumerVR.subExpression):
				match = True
				break
		
		if not match:
			return False
			
	return True


if __name__ == "__main__":
	_test()					
		