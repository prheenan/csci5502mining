# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

def dff_std(obj):
    """
    returns the derivative of the filtered force normalized to a standard normal curve 
    Args:
        obj : preprocessed object with the windows we want
    """
    def grad_std():
        filteredGradient = np.gradient(filteredForce)
        stdV= np.std(filteredGradient)
        zGrad = (filteredGradient - np.mean(filteredGradient))/stdV
        return zGrad

    features = list() 
    timeWindow,sepWindow,forceWindow = \
        obj.HiResData.GetTimeSepForce()
    nWindows = len(sepWindow)
    timeConst = 8e-5
    mFiltering = FilterObj.Filter(timeConst = timeConst)
    for i,(time,sep,force) in enumerate(zip(timeWindow,sepWindow,forceWindow)):
        # convert force to pN (just for plotting)
        force *= 1e12
        # also normalize it so the median before the event is zero (again,
        # just to make the plot pretty)
        deltaT = time[1]-time[0]
        startIdxInWindow = int((labels[i].StartTime-time[0])/(deltaT))
        force -= np.median(force[:startIdxInWindow])
        # get the filtered version too!
        filteredForce=mFiltering.FilterDataY(time,force)
        features.append(grad_std(filteredForce))

    return features
