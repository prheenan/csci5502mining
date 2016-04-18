# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

from sklearn.mixture import GMM

import Learner

class GaussianOpt:
    def __init__(self,n_components=2,n_iter=500,
                 **kwargs):
        self.n_components=n_components
        # any other arguments, set dynamically
        for k,v in kwargs.items():
            setattr(self,k,v)
            

class GaussianMixtureLearner(Learner.Learner):
    def __init__(self,FeatureMask,opts=GaussianOpt()):
        super(GaussianMixtureLearner, self).__init__(FeatureMask)
        self.opts = opts
        # construct the features kmeans will use
        self.arr = self.MaskToMatrix(FeatureMask)
        self.toFit = None
    def MaskToMatrix(self,mask):
        N = mask.N
        minMaxWave = mask.Forward_Wavelet
        maskedForce = mask.CannyFilter * mask.ForceStd
        return np.reshape((maskedForce,
                           minMaxWave),
                          (N,2))
    def FitAndPredict(self):
        return toFit.fit_predict(self.arr)
    def Predict(self,Mask):
        return self.toFit.predict(self.MaskToMatrix(Mask))
    def Fit(self,Mask):
        optionDict = self.opts.__dict__
        self.toFit = GMM(**optionDict)
        return self.toFit.fit(self.MaskToMatrix(Mask))
        
