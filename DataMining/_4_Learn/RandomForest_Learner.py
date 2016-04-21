# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

from sklearn.ensemble import RandomForestClassifier
from _5_Evaluate.ParameterSweep import PlotMask

import Learner

class ForestOpt:
    def __init__(self,max_depth=5, n_estimators=3, max_features=1,**kwargs):
        # any other arguments, set dynamically
        self.max_depth=max_depth
        self.n_estimators=n_estimators
        self.max_features=max_features
        for k,v in kwargs.items():
            setattr(self,k,v)
            

class RandomForest_Learner(Learner.Learner):
    def __init__(self,FeatureMask,opts=ForestOpt()):
        super(RandomForest_Learner, self).__init__(FeatureMask)
        self.opts = opts
        # construct the features kmeans will use
        self.arr = self.MaskToMatrix(FeatureMask)
        self.toFit = None
    def MaskToMatrix(self,mask):
        return self.DefaultFeatureMatrix(mask)
    def Predict(self,Mask):
        idx =  self.toFit.predict(self.MaskToMatrix(Mask))
        return idx
    def Fit(self,Mask):
        optionDict = self.opts.__dict__
        self.toFit = RandomForestClassifier(**optionDict)
        return self.toFit.fit(self.MaskToMatrix(Mask),
                              Mask.LabelsForAllPoints)
        
