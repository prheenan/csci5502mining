# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys


from abc import ABCMeta,abstractmethod
import sklearn.metrics as scores


class EvaluationObject:
    def __init__(self,truth,predictions):
        """
        Creates an object with the various scores we want. 

        Args: 
            truth: binary array of size N, ground truth
            predictions: binary array of size N, from some model
        """
        scorers = [ ['accuracy',scores.accuracy_score],
                    ['precision',scores.precision_score],
                    ['recall',scores.recall_score],
                    ['f_score',scores.f1_score],
                    ['confusion_matrix',scores.confusion_matrix],
                    ['roc_auc_score',scores.roc_auc_score]
                ]
        for lab,s in scorers:
            mScore = s(truth,predictions)
            # set the score as one of our fields
            setattr(self,lab,mScore)
            
    
class Learner(object):
    __metaclass__ = ABCMeta
    def __init__(self,FeatureMask):
        """
        Args:
            FeatureMask: The FeatureMask object, from FeatureGenerator

            Labels: array of labels; element [i] is the labels for object i,
            relative to the start index of the window for i
        """
        # save the feature mask
        self.FeatureMask = FeatureMask
    def Evaluate(self,Predictions):
        """
        Given predictions for the labels, returns an evaluation object

        Args:
           Predictions: size of self.n, 1/0 predictions for there is / isnt
           and event
        Returns:
           Evaluation object with the relevant statistics. 
        """
        # get the actual labels
        truth = self.FeatureMask.LabelsForAllPoints
        return Evaluate_Predictions(self,Truth,Predictions)
    def ObjToMask(self,Obj,Labels):
        return FeatureMask(Obj,Labels)
    def Evaluate_Predictions(self,Truth,predIdx):
        """
        Overwrite inherited Evaluate, since we dont know our labels.
        Choose whichever has the lowest number of points as '1'

        Args:
            Truth,predIdx: see Evaluate
        """
        """
        mSet = set(predIdx)
        # if for some reason we missed all the events, say so
        if (len(mSet) == 1):
            use = np.zeros(Truth.size)
            return EvaluationObject(Truth,use)
        ele1 = mSet.pop()
        ele2 = mSet.pop()
        mList = list(predIdx)
        # zeros should always have more elements...
        if (mList.count(ele1) > mList.count(ele2)):
            whereZero = [np.where(predIdx==ele1)]
            whereOne = [np.where(predIdx==ele2)]
        else:
            whereZero = [np.where(predIdx==ele2)]
            whereOne = [np.where(predIdx==ele1)]
        use = predIdx.copy()
        use[whereZero] = 0
        use[whereOne] = 1
        """
        return EvaluationObject(Truth,predIdx)        
    @property
    def LabelsForAllPoints(self):
        """
        returns a matrix of 0/1 points for all arrays
        """
        return self.FeatureMask.LabelsForAllPoints
    @property
    def N(self):
        """
        returns the total number of datas points ('columns') along all windows
        """
        return self.FeatureMask.N
    @property
    def IdxWhereEvent(self):
        """
        returns the *indices* where a 1 is happening
        """
        return self.FeatureMask.IdxWhereEvent
    @abstractmethod
    def Fit(self,Mask):
        """
        Abstract Method with fits the data it was given, using the mask
        """
        pass
    @abstractmethod
    def Predict(self,Mask):
        """
        Abstract Method with predicts the data it was given, using the mask.
        Relies on previous fit
        """
        pass
