# Module containing the basic and composite objects which make up DL formulae.
# One wishing to write a parser will need to map their domain to these constructs.
# Tyler Adams
# April 2013
import copy


class Expression(object):
	'''Expression base class'''
	
	def normalize(self):
		raise NotImplementedError('normalize() must be implemented by subclasses')
	
	def applyNegation(self):
		raise NotImplementedError('applyNegation() must be implemented by subclasses')
	
	def __eq__(self, other):
		return type(other) is type(self) and self.__dict__ == other.__dict__
	
	def __ne__(self, other):
		return not self.__eq__(other)
		
class BottomExpression(Expression, object):
	'''The BOTTOM special expression'''
	
	def normalize(self):
		return self
	def applyNegation(self):
		return TopExpression()
	def __repr__(self):
		return 'bottom'
		
class TopExpression(Expression, object):
	''' The TOP special expression '''
	def normalize(self):	
		return self
	def applyNegation(self):
		return BottomExpression()
	def __repr__(self):
		return 'top'
		
BOTTOM = BottomExpression()
TOP = TopExpression()		
		
		
class ConjunctiveExpression(Expression):
	'''An expression representing the conjunction (intersection) of two other expressions, e.g. A AND B'''
	
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def normalize(self):
		self.left = self.left.normalize()
		self.right = self.right.normalize()
		if self.left == self.right:
			return self.left
		if self.left == NegatedExpression(copy.deepcopy(self.right)).normalize():
			return BOTTOM
		if self.left == BOTTOM or self.right == BOTTOM:
			return BOTTOM
		if self.left == TOP:
			return self.right
		if self.right == TOP:
			return self.left
		return self
	
	def applyNegation(self):
		return DisjunctiveExpression(NegatedExpression(self.left), NegatedExpression(self.right))
		
	def __repr__(self):
		return '(' + self.left.__repr__() + ' and ' + self.right.__repr__() + ')'
		

class DisjunctiveExpression(Expression):
	'''An expression representing the disjunction (union) of two other expressions, e.g. A OR B'''
	
	def __init__(self, left, right):
		self.left = left
		self.right = right
		
	def normalize(self):
		if isinstance(self.right, ConjunctiveExpression):
			return ConjunctiveExpression(DisjunctiveExpression(self.left, self.right.left), DisjunctiveExpression(self.left, self.right.right)).normalize()
		if isinstance(self.left, ConjunctiveExpression):
			return ConjunctiveExpression(DisjunctiveExpression(self.right, self.left.left), DisjunctiveExpression(self.right, self.left.right)).normalize()
	
		self.left = self.left.normalize()
		self.right = self.right.normalize()
		if self.left == self.right:
			return self.left
		if self.left == NegatedExpression(copy.deepcopy(self.right)).normalize():
			return TOP
		if self.left == TOP or self.right == TOP:
			return TOP
		if self.left == BOTTOM:
			return self.right
		if self.right == BOTTOM:
			return self.left
		return self
		
	def applyNegation(self):
		return ConjunctiveExpression(NegatedExpression(self.left), NegatedExpression(self.right))
		
	
	def __repr__(self):
		return '(' + self.left.__repr__() + ' or ' + self.right.__repr__() + ')'
		
		
class ValueRestrictedExpression(Expression):
	'''A value restriction, e.g. FORALL R.C'''
	
	def __init__(self, roleName, subExpression, universal=True):
		self.roleName = roleName
		self.subExpression = subExpression
		self.universal = universal
		
	def applyNegation(self):
		self.universal = not self.universal
		self.subExpression = NegatedExpression(self.subExpression)
		return self
	
	def normalize(self):
		self.subExpression = self.subExpression.normalize()
		return self
		
	def __repr__(self):
		return '(' + ('forall' if self.universal else 'exists') + ' ' + self.roleName + '.' + self.subExpression.__repr__() + ')'
		
class NegatedExpression(Expression):
	'''A negated expression, e.g. NOT A'''
	
	def __init__(self, subExpression):
		self.subExpression = subExpression
		
	def normalize(self):
		return self.subExpression.applyNegation().normalize()
		
	def applyNegation(self):
		return self.subExpression
		
	def __repr__(self):
		return '~(' + self.subExpression.__repr__() + ')'
	
class LiteralExpression(Expression):
	'''An expression consisting solely of a literal (or 'primitive') concept name.  May or may not be negated.'''
	
	def __init__(self, value, negated=False):
		self.value = value
		self.negated = negated
	
	def normalize(self):
		return self
	
	def applyNegation(self):
		self.negated = not self.negated
		return self
		
	def __repr__(self):
		return ('~' if self.negated else '') + self.value
	