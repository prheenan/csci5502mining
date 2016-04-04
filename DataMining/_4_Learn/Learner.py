# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys


from abc import ABCMeta,abstractmethod

class EvaluationObject:
    def __init__(self):
        pass
    
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
    def Evaluate(Predictions):
        """
        Given predictions for the labels, returns an evaluation object

        Args:
           Predictions: size of self.n, 1/0 predictions for there is / isnt
           and event
        Returns:
           Evaluation object with the relevant statistics. 
        """
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
