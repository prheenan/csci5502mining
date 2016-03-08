# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
import PyUtil.IgorUtil as IgorUtil

class TouchOffObj:
    def __init__(self,apprTime,apprIdx,retrTime,retrIdx):
        self.apprTime = apprTime
        self.apprIdx = apprIdx
        self.retrTime = retrTime
        self.retrIdx = retrIdx

class Filter:
    def __init__(self,timeConst,degree=2):
        """
        Initialize a filtering object. 
        Args:
            timeConst: the filtering time constant, in seconds
            degree: degree of the filtering constant
        """
        self.timeFilter = timeConst
    def FilterDataY(self,timeY,DataY):
        """
        Given a set of times (assumed uniformly increasing)
        for dataY, filters the data
        Args:
            timeY: the time bases to use
        Returns:
            filtered Y values
        """
        deltaTForY = timeY[1] - timeY[0]
        n = int(np.ceil(self.timeFilter/deltaTForY))
        return IgorUtil.savitskyFilter(DataY,nSmooth=n,degree=2)
    def GetApproachAndRetractTouchoffTimes(TimeSepForceObj):
        """
        Given a TimeSepForceObj object (ie: low or high res), 
        gets the (approximate) approach and retract touchoff times, 

        Args:
            DataObj:TimeSepForceObj instance, with time separation and force
        Returns: 
            TouchOffObj instance
        """
        # filter the zsnsr data to what we are about

        # using the meta data, get the approximate 'halfway' mark

        # split the data, filter, find where the derivative is median, then
        # first crosses the median - this is either the start or the end of the
        # touchoff 

        pass
