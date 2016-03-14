# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys


def GetFeatureMatrix(PreProcessedObjects,ListOfFunctions):
    """
    Returns the NxF Matrix, where N is the size of all data in windows od
    PreProcessedObjects, F is number of feature functions in ListOfFunctions

    Args:
        PreProcessedObjects: list of PreProcessedObjects
        ListOfFunctions: each element is a function taking in a single data
        object (with D total window elements) and returning a list of D floats
        (XXX probably a bad idea to go between windows, we will see)
    
    Returns:
        NxF feature matrix
    """
    pass


