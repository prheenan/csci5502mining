# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys


from abc import ABCMeta

class Learner(object):
    __metaclass__ = ABCMeta
    def __init__(self,FeatureMask,Labels):
        """
        
        """
        self.FeatureMask = FeatureMask
    def Evaluate(Predictions,Labels):
        pass
        
