# Sample (interactive) use of pythonDL.  Not intended to be run as a standalone script
# Tyler Adams
# tyler.r.adams@gmail.com
# April 2013

# import all the necessary things
import subsumption as s
import simplestructuralsubsumption as sss
import textexpressionparser as tep

# create the query processor and text parser
qp = s.SubsumptionQueryProcessor(sss)
parser = tep.TextExpressionParser()
# alias the parseline call for brevity
c = parser.parseLine

# let's define some basic concepts
cow = c('Cow')
madcow = c('Cow and forall hasFood.Meat')
notcow = c('~Cow')
person = c('Person')

# the query processor was instantiated with the simple structural subsumption algorithm, and 
# performs all queries (like satisfiability, disjointness, etc.) using it
qp.equivalent(cow, cow)
qp.equivalent(cow, madcow)
qp.subsumedby(cow, madcow)
qp.subsumedby(madcow, cow)
qp.disjoint(cow, person)
qp.disjoint(cow, notcow)

# note that this implementation only works for FL, extended to allow literal negation.
# However, it only depends on the normal form being in FL; so if an expression ends up
# being in FL, it can still be queried upon.
qp.subsumedby(c('Person and ~(exists hasChild.exists hasChild.(Rich or Poor))'), c('Person and hasChild.hasChild.~Rich'))


# If the definitions get a little more complex, such as a larger knowledge base, we can 
# perform some queries over the whole set.  For example, we can define a set of concepts as
# a python list or dict, and find all subsumption relations present.
conceptsdict = {
'Cow' : cow,
'MadCow' : madcow,
'Person' : person,
'Man' : c('Male and Adult and Person'),
'Single' : c('Person and Adult and forall hasSpouse.bottom'),
'Bachelor' : c('Person and Adult and Male and forall hasSpouse.bottom')
}

qp.allSubsumption(conceptsdict)