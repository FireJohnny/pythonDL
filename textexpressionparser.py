# Module implementing a text-based parser for DL Expressions
# Tyler Adams
# tyler.r.adams@gmail.com
# April 2013

import dlobjects as dl
import pyparsing as pp

# from http://stackoverflow.com/questions/4571441/recursive-expressions-with-pyparsing
def _toNested(numterms):
	if numterms is None:
		# None operator can only by binary op
		initlen = 2
		incr = 1
	else:
		initlen = {0:1,1:2,2:3,3:5}[numterms]
		incr = {0:1,1:1,2:2,3:4}[numterms]

	# define parse action for this number of terms,
	# to convert flat list of tokens into nested list
	def pa(s,l,t):
		t = t[0]
		if len(t) > initlen:
			ret = pp.ParseResults(t[:initlen])
			i = initlen
			while i < len(t):
				ret = pp.ParseResults([ret] + t[i:i+incr])
				i += incr
			return pp.ParseResults([ret])
	return pa
	
def _test():		
	parser = TextExpressionParser()
	tests = [
				'top',
				'bottom',
				'~top',
				'Person and Parent and Adult',
				'top and bottom',
				'Person and exists hasChild.hasChild.~Female and (Cow or Chicken)',
				'Person and exists hasChild.hasChild.~Female and ~(Cow or Chicken or bottom)',
				'Person and exists hasChild.hasChild.~Female and ~(Cow or Chicken or top)'
				'~~Person',
			]
	for test in tests:
		print 'input: ' + test
		results = parser._getParser().parseString(test)
		print 'tokenized:', results[0]
		ot = parser._createObjectTree(results[0])
		print 'object tree:', ot
		print 'normalized:', ot.normalize()
		print

class TextExpressionParser:
	'''Use an instance of this class to parse text into tokens according to the DL Expression grammar'''
	
	def __init__(self, symbols={'forall':'forall','exists':'exists', 'and':'and','or':'or','not':'~','bottom':'bottom','top':'top'}):
		self.symbols = symbols
		self.parser = None
		
	def  parseLine(self, str):
		results = self._getParser().parseString(str)
		return self._createObjectTree(results[0]).normalize()
	
	'''
	Implementation unfinished;  need to handle duplicate terms
	def parseKB(self, linesDict, replace=True):
		changed = True
		while changed:
			changed = False
			for key0, value0 in linesDict.iteritems():
				for key1, value1 in linesDict.iteritems():
					if key0 != key1:
						val = value1.replace(key0, value0)
						if val != value1:
							linesDict[key1] = val
							changed = True
		ret = {}
		for key, value in linesDict.iteritems():
			ret[key] = self.parseLine(value)
		return ret
	'''
							
	def _createObjectTree(self, token):
		if isinstance(token, basestring):
			if token == self.symbols['bottom']:
				return dl.BOTTOM
			elif token == self.symbols['top']:
				return dl.TOP
			else:
				return dl.LiteralExpression(token)
		elif token[0] == self.symbols['not']:
			return dl.NegatedExpression(subExpression=self._createObjectTree(token[1]))
		elif token[1] == self.symbols['and']:
			return dl.ConjunctiveExpression(left=self._createObjectTree(token[0]), right=self._createObjectTree(token[2]))
		elif token[1] == self.symbols['or']:
			return dl.DisjunctiveExpression(left=self._createObjectTree(token[0]), right=self._createObjectTree(token[2]))
		elif token[0][0] == self.symbols['forall']:
			return dl.ValueRestrictedExpression(roleName=token[0][1], subExpression=self._createObjectTree(token[1]), universal=True)
		elif token[0][0] == self.symbols['exists']:
			return dl.ValueRestrictedExpression(roleName=token[0][1], subExpression=self._createObjectTree(token[1]), universal=False)
		else:
			return None
		
	def _getParser(self):
		if not self.parser:
			period = pp.Literal('.').suppress()
			lparen = pp.Literal('(').suppress()
			rparen = pp.Literal(')').suppress()
			forall = pp.Literal(self.symbols['forall'])
			exists = pp.Literal(self.symbols['exists'])
			bottom = pp.Literal(self.symbols['bottom'])
			top = pp.Literal(self.symbols['top'])
			
			uppers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
			lowers = uppers.lower()
			
			conceptName = bottom | top | pp.Combine(pp.Word(uppers, exact=1) + pp.Word(pp.alphas))
			relationName = pp.Combine(pp.Word(lowers, exact=1) +  pp.Word(pp.alphas))
			valueOp = pp.Group(pp.Optional(forall | exists, default=forall) + relationName + period)
			dlExpression = pp.Forward()
			dlOperand = lparen + dlExpression + rparen | conceptName
			dlExpression << pp.operatorPrecedence(dlOperand,
				[
				(self.symbols['not'], 1, pp.opAssoc.RIGHT, ),
				(valueOp, 1, pp.opAssoc.RIGHT, ),
				(self.symbols['and'], 2, pp.opAssoc.LEFT, _toNested(2)),
				(self.symbols['or'], 2, pp.opAssoc.LEFT, _toNested(2)),
				])
			self.parser = dlExpression
		return self.parser

if __name__ == "__main__":
	_test()
		