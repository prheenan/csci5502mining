# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

import Learner

class KmeansOpts:
    def __init__(self,nIters,nClusters):
        pass

class KmeansLearner(Learner.Learner):
    def __init__(self,FeatureMask,Labels):
        super(KmeansLearner, self).__init__(FeatureMask,Labels)
         

    
