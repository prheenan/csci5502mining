# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

def TestFunction(obj):
    """
    returnsa flattened window (dumb!)
    Args:
        obj : preprocessed object with the windows we want
    returns a flattened list of hi res data from the windows
    """
    return [data for window in obj.HiResData.HiResData\
             for data in window]

def dff_std(obj):
    """
    returns the derivative of the filtered force normalized to a standard normal curve 
    Args:
        obj : preprocessed object with the windows we want
    """
    def grad_std(filtered_obj):
        filteredGradient = np.gradient(filtered_obj)
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
        # get the filtered version too!
        filteredForce=mFiltering.FilterDataY(time,force)
        features.append(grad_std(filteredForce))

    return features

def dff_min_max(obj):
    """
    returns the derivative of the filtered force normalized via min max
    Args:
        obj : preprocessed object with the windows we want
    """
    def grad_minmax(filtered_obj):
        filteredGradient = np.gradient(filtered_obj)
        norm = (filteredGradient - filteredGradient.min()) / (filteredGradient.max() - filteredGradient.min()) 
        return norm

    features = list() 
    timeWindow,sepWindow,forceWindow = \
        obj.HiResData.GetTimeSepForce()
    nWindows = len(sepWindow)
    timeConst = 8e-5
    mFiltering = FilterObj.Filter(timeConst = timeConst)
    for i,(time,sep,force) in enumerate(zip(timeWindow,sepWindow,forceWindow)):
        filteredForce=mFiltering.FilterDataY(time,force)
        features.append(grad_std(filteredForce))

    return features

def dfs_std(obj):
    """
    returns the derivative of the filtered separation normalized to a standard normal curve 
    Args:
        obj : preprocessed object with the windows we want
    """
    def grad_std(filtered_obj):
        filteredGradient = np.gradient(filtered_obj)
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
        filteredSep=mFiltering.FilterDataY(time,sep)
        features.append(grad_std(filteredSep))

    return features

def dfs_minmax(obj):
    """
    returns the derivative of the filtered separation normalized via minmax
    Args:
        obj : preprocessed object with the windows we want
    """
    def grad_minmax(filtered_obj):
        filteredGradient = np.gradient(filtered_obj)
        norm = (filteredGradient - filteredGradient.min()) / (filteredGradient.max() - filteredGradient.min()) 
        return norm

    features = list() 
    timeWindow,sepWindow,forceWindow = \
        obj.HiResData.GetTimeSepForce()
    nWindows = len(sepWindow)
    timeConst = 8e-5
    mFiltering = FilterObj.Filter(timeConst = timeConst)
    for i,(time,sep,force) in enumerate(zip(timeWindow,sepWindow,forceWindow)):
        filteredSep=mFiltering.FilterDataY(time,sep)
        features.append(grad_std(filteredSep))

    return features