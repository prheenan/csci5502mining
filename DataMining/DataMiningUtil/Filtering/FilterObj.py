# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
import CypherReader.Util.IgorUtil as IgorUtil
from scipy.signal import medfilt
class TouchOffObj:
    def __init__(self,apprTime,apprIdx,retrTime,retrIdx,halfwayTime,halfwayIdx,
                 startIdx = 0, endIdx = None):
        """
        Records the times and indices associated with a touchoff

        Args:
            startIdx: the index where we start from. Defaults to 0
            apprTime: time of approach hitting the surface
            apprIndex: index of apprTime
            halfwayTime: time halfway through dwell
            halfwayIdx: index forhalf wayTime
            retrTime: time of retratcting leaving the surface
            retrIdx: index of retrTime
            endIdx: end index
        """
        self.startIdx = startIdx
        self.apprTime = apprTime
        self.apprIdx = apprIdx
        self.retrTime = retrTime
        self.retrIdx = retrIdx
        self.dwellIdxStart = apprIdx+1
        self.dwellIdxEnd = retrIdx-1
        self.halfwayTime = halfwayTime
        self.halfwayIdx = halfwayIdx
        self.endIdx = endIdx

class Filter:
    def __init__(self,timeConst,degree=2,surfaceThickness=15e-9):
        """
        Initialize a filtering object. 
        Args:
            timeConst: the filtering time constant, in seconds. If none, 
            gets from surface thickness...

            degree: degree of the filtering constant
        """
        self.surfaceThickness = surfaceThickness
        self.timeFilter = timeConst
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
    def FilterDataY(self,timeY,DataY):
        """
        Class wrapper for module filterng funciton. Uses filtering constant
        to filter...
        Args:
            See FilterDataY
        """
        return FilterDataY(timeY,DataY,self.timeFilter)
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
        # determine where the filtered approach region change is first <=
        # median of unfilted
        # get the approach and retract indices
        halfwayIdx,halfwayTime = \
                    GetHalfwayThroughDwellTimeAndIndex(TimeSepForceObj)
        # get the start index (of the dwell) near the trigger time
        startIdx = np.argmin(np.abs(time-TimeSepForceObj.meta.TriggerTime))
        # end index should be at the start index, plug twice of the halfway
        # (Through thr dwell) index
        endIdx = startIdx+(halfwayIdx-startIdx)*2
        # get the median of the (raw) derivative in the dwell region
        forceDwell = rawY[startIdx:endIdx]
        rawMedian = np.median(forceDwell)
        regionApproach,regionRetract = \
                GetApproxTouchoffRegions(TimeSepForceObj,self.surfaceThickness)
        apprRegion = rawY[regionApproach]
        retrRegion = rawY[regionRetract]
        apprOffset = regionApproach[0]
        retrOffset = regionRetract[0]
        # the approach index is the *first* time (0) we are above (>=, True)
        # the median
        approachIdx = GetWhereCompares(time[regionApproach],
                                       apprRegion,timeConst,
                                       rawMedian,True)[0] + apprOffset
        # the retract index is the *last* time (-1) we are above (>=, True)
        # the median
        retrIdx= GetWhereCompares(time[regionRetract],
                                  retrRegion,timeConst,
                                  rawMedian,True)[-1] + retrOffset
        return TouchOffObj(time[approachIdx],approachIdx,time[retrIdx],retrIdx,
                           halfwayTime,halfwayIdx)


def FilterDataY(timeY,DataY,timeFilter):
    """
    Given a set of times (assumed uniformly increasing)
    for dataY, filters the data
    Args:
        timeY: the time bases to use
        DataY: the data to filter
        timeFilter: the time, same units of timeY, to filter
    Returns:
        filtered Y values
    """
    deltaTForY = timeY[1] - timeY[0]
    n = min(DataY.size-1,int(np.ceil(timeFilter/deltaTForY)))
    if (n % 2 ==0):
        n += 1
    return medfilt(DataY,n)

def GetWhereCompares(time,regionData,timeFilter,threshold,gt):
    """ 
    Get where the filtered vesion of 'regionData' is <= threshold or
    >= threshold
    
    Args:
        time: time bases of regionData
        regionData: the region of interest
        timeFilter: the timescale to filter the data to
        threshhold: the value to threshhold to 
        gt: if true, gets indices where gt. Else, gets index where less than
    """
    regionFiltered = FilterDataY(time,regionData,timeFilter=timeFilter)
    # get the gradient
    if (gt):
        return np.where(regionFiltered >= threshold)[0]
    else:
        return np.where(regionFiltered <= threshold)[0]

def GetHalfwayThroughDwellTimeAndIndex(mObj):
    """
    Given a TimeSepForceObj object, gets the approximate time and index to 
    halfway through the swell and index

    Args:
        TimeSepForceObj: TimeSepForceObj object, with the trigger and dwell 
        time in the meta
    Returns: 
        tuple of idx,time to halfway
    """
    # Get the diffferent distances we will need
    meta = mObj.meta
    time = mObj.time
    startTime= meta.TriggerTime
    # get the (approximate!) time to 'halfway'
    halfwayTime = startTime + meta.DwellTime/2
    halfwayIdx = np.argmin(np.abs(time-halfwayTime))
    return halfwayIdx,halfwayTime

def GetApproxTouchoffRegions(TimeSepForceObj,surfaceDepth):
    """
    Using the meta data in TimeSepForceObj, gets the approximate touchoff, 
    within window seconds (in time units of the object)
    
    Args:
        TimeSepForceObj: the object to use
    Returns:
        a tuple of indices into the original array:
        <Approach touchoff, Retract touchoff >
    """
    meta = TimeSepForceObj.meta
    time = TimeSepForceObj.time
    dwell = meta.DwellTime
    vel = min(meta.RetractVelocity,meta.ApproachVelocity)
    deltaT = surfaceDepth/vel
    window = max(deltaT,dwell/8)
    # science!
    # Get the diffferent distances we will need
    startTime= meta.TriggerTime
    halfwayTime,halfwayIdx = GetHalfwayThroughDwellTimeAndIndex(TimeSepForceObj)
    endTime = startTime + dwell
    # write down the indices where we are in the times we care about
    delta= window/2
    regionApproach = np.where( (time <= startTime + delta) &
                               (time >= startTime - delta) )[0]
    regionRetract =  np.where( (time <= endTime + delta) &
                               (time >= endTime- delta) )[0]
    return regionApproach,regionRetract
