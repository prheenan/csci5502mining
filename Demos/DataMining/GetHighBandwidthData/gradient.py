#!usr/bin/env python

import numpy
import theano
import theano.tensor as T
from theano import pp

class Gradient:
	'''
	Compute the derivative of some expression y with respect to its parameter x
	'''
	def __init__(self, y):
		# establish the gradient function upon construction
		x                 = T.dscalar('x')
		symbolic_gradient = T.grad(x**2, x) # "x**2" should be replaced with "y"
		self.function     = theano.function([x], symbolic_gradient)

