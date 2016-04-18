# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

from sklearn.svm import LinearSVC

import Learner

class SvcOpt:
    def __init__(self,**kwargs):
        # any other arguments, set dynamically
        for k,v in kwargs.items():
            setattr(self,k,v)
            

class SVM_Learner(Learner.Learner):
    def __init__(self,FeatureMask,opts=SvcOpt()):
        super(SVM_Learner, self).__init__(FeatureMask)
        self.opts = opts
        # construct the features kmeans will use
        self.arr = self.MaskToMatrix(FeatureMask)
        self.toFit = None
    def MaskToMatrix(self,mask):
        return self.DefaultFeatureMatrix(mask)
    def Predict(self,Mask):
        return self.toFit.predict(self.MaskToMatrix(Mask))
    def Fit(self,Mask):
        optionDict = self.opts.__dict__
        self.toFit = LinearSVC(**optionDict)
        return self.toFit.fit(self.MaskToMatrix(Mask),
                              Mask.LabelsForAllPoints)
        
