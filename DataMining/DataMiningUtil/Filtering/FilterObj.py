# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
import CypherReader.Util.IgorUtil as IgorUtil

class TouchOffObj:
    def __init__(self,apprTime,apprIdx,retrTime,retrIdx,halfwayTime,halfwayIdx):
        self.apprTime = apprTime
        self.apprIdx = apprIdx
        self.retrTime = retrTime
        self.retrIdx = retrIdx
        self.halfwayTime = halfwayTime
        self.halfwayIdx = halfwayIdx

class Filter:
    def __init__(self,timeConst=None,degree=2,surfaceThickness=15e-9):
        """
        Initialize a filtering object. 
        Args:
            timeConst: the filtering time constant, in seconds. If none, 
            gets from surface thickness...

            degree: degree of the filtering constant
        """
        self.surfaceThickness = surfaceThickness
        self.timeFilter = timeConst
    def FilterDataY(self,timeY,DataY,timeFilter=None):
        """
        Given a set of times (assumed uniformly increasing)
        for dataY, filters the data
        Args:
            timeY: the time bases to use
        Returns:
            filtered Y values
        """
        deltaTForY = timeY[1] - timeY[0]
        if (timeFilter is None):
            timeFilter = self.timeFilter
        n = min(DataY.size-1,int(np.ceil(timeFilter/deltaTForY)))
        print(n)
        print(DataY.size)
        return IgorUtil.savitskyFilter(DataY,nSmooth=n,degree=2)
    def InvolsTimeConst(self,TimeSepForceObj):
        """
        Areturns the expected time for the invols curve to run its course
        args:
            TimeSepForceObj : we get the approach/retract velocity from the
            'meta' attribute of this
        """
        meta = TimeSepForceObj.meta
        return self.surfaceThickness/min(meta.ApproachVelocity,
                                         meta.RetractVelocity)
    def GetWhereGradientLessThan(self,time,regionData,timeFilter,threshold):
        print(regionData.size)
        print(regionData.shape)
        regionFiltered = self.FilterDataY(time,regionData,timeFilter=timeFilter)
        # get the gradient
        grad = np.gradient(regionFiltered)
        return np.where(grad <= threshold)[0]
    
    def GetApproachAndRetractTouchoffTimes(self,TimeSepForceObj):
        """
        Given a TimeSepForceObj object (ie: low or high res), 
        gets the (approximate) approach and retract touchoff times, 

        Args:
            DataObj:TimeSepForceObj instance, with time separation and force
        Returns: 
            TouchOffObj instance
        """
        # filter the sep data to what we are about
        rawY = TimeSepForceObj.force
        time = TimeSepForceObj.time
        timeConst = self.InvolsTimeConst(TimeSepForceObj)
        # using the meta data, get the approximate 'halfway' mark
        # split the data, filter, find where the derivative is median, then
        # first crosses the median - this is either the start or the end of the
        # touchoff 
        grad = np.abs(np.gradient(rawY))
        meta = TimeSepForceObj.meta
        # science!
        # Get the diffferent distances we will need
        startTime= meta.TriggerTime
        # get the (approximate!) time to 'halfway'
        halfwayTime = startTime + meta.DwellTime/2
        halfwayIdx = np.argmin(np.abs(time-halfwayTime))
        endTime = startTime + meta.DwellTime
        window = timeConst
        # write down the indices where we are in the times we care about 
        regionApproach = np.where( (time <= startTime + window) &
                                   (time >= startTime) )[0]
        regionRetract =  np.where( (time <= endTime) &
                                   (time >= endTime-window) )[0]
        # offsets into these regons
        apprOffset = regionApproach[0]
        retrOffset = regionRetract[0]
        # get the median of the (raw) derivative in this region
        rawMedian = np.median(grad)
        # determine where the filtered approach region change is first <=
        # median of unfilted
        apprRegion = rawY[regionApproach]
        retrRegion = rawY[regionRetract]
        # get the approach and retract indices
        approachIdx =self.GetWhereGradientLessThan(time[regionApproach],
                                                   apprRegion,timeConst,
                                                   rawMedian)[0] + apprOffset
        retrIdx= self.GetWhereGradientLessThan(time[regionApproach],
                                               retrRegion,timeConst,
                                               rawMedian)[0] + retrOffset
        return TouchOffObj(time[approachIdx],approachIdx,time[retrIdx],retrIdx,
                           halfwayTime,halfwayIdx)

