# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
from sklearn.cluster import KMeans

import Learner

class KmeansOpts:
    def __init__(self,precompute_distances=True,n_clusters=2,copy_x=True,
                 **kwargs):
        self.n_clusters=n_clusters
        self.copy_x =copy_x
        # any other arguments, set dynamically
        for k,v in kwargs.items():
            setattr(self,k,v)
            

class KmeansLearner(Learner.Learner):
    def __init__(self,FeatureMask,opts=KmeansOpts()):
        super(KmeansLearner, self).__init__(FeatureMask)
        self.opts = opts
        # construct the features kmeans will use
        self.arr = self.MaskToMatrix(FeatureMask)
        self.toFit = None
    def MaskToMatrix(self,mask):
        N = mask.N
        return np.reshape(mask.CannyFilter,
                          (N,1))
    def Predict(self,Mask):
        return self.toFit.predict(self.MaskToMatrix(Mask))
    def Fit(self,Mask):
        optionDict = self.opts.__dict__
        self.toFit = KMeans(**optionDict)
        return self.toFit.fit(self.MaskToMatrix(Mask))
    def Evaluate(self,predIdx):
        """
        overwrite inherited Evaluate, since we dont know our labels.
        Choose whichever has the lowest number of points as '1'
        """
        mSet = set(predIdx)
        ele1 = mSet.pop()
        ele2 = mSet.pop()
        mList = list(predIdx)
        if (mList.count(ele1) > mList.count(ele2)):
            whereZero = [np.where(predIdx==ele1)]
            whereOne = [np.where(predIdx==ele2)]
        else:
            whereZero = [np.where(predIdx==ele2)]
            whereOne = [np.where(predIdx==ele1)]
        use = predIdx.copy()
        use[whereZero] = 0
        use[whereOne] = 1
        return super(KmeansLearner,self).Evaluate(use)
        
        
