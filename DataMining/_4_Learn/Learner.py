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
                    ['confusion_matrix',scores.confusion_matrix]
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
        return EvaluationObject(truth,Predictions)
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
    def FitAndPredict(self):
        """
        Abstract Method with fits the data it was given, and returns its 
        prediction

        Returns:
            0/1 binary 'is an event happening' prediction
        """
        pass
