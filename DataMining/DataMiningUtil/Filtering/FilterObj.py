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
    def __init__(self,timeConst,degree=2,surfaceThickness=10e-9):
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
    def GetApproachAndRetractTouchoffTimes(self,TimeSepForceObj,
                                           rawMedianAppr=None,
                                           rawMedianRetr=None):
        """
        Given a TimeSepForceObj object (ie: low or high res), 
        gets the (approximate) approach and retract touchoff times, 

        Args:
            DataObj:TimeSepForceObj instance, with time separation and force
            rawMedianAppr: threshhold for the dwell to start. If none, defaults
            to medians of the dwell
            rawMedianRetr: threshhold for the dwell to end, If None, 
            defaults to the median of the dwell
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
        if (rawMedianAppr == None):
            rawMedianAppr = np.median(forceDwell)
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
                                       rawMedianAppr,True)[0] + apprOffset
        if (rawMedianRetr == None):
            rawMedianRetr = min(rawY[approachIdx],rawMedianAppr)
        # the retract index is the *last* time (-1) we are above (>=, True)
        # the median
        retrIdx= GetWhereCompares(time[regionRetract],
                                  retrRegion,timeConst,
                                  rawMedianRetr,True)[-1] + retrOffset
        return TouchOffObj(time[approachIdx],approachIdx,time[retrIdx],retrIdx,
                           halfwayTime,halfwayIdx)


def FilterDataY(timeY,DataY,timeFilter,MaxNPoints=20000):
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
    nPointsByDelta = int(np.ceil(timeFilter/deltaTForY))
    # cant filter more data points  than our actual data
    n = min(DataY.size-1,nPointsByDelta)
    # have some maximum threshhold.
    n = min(n,MaxNPoints)
    return IgorUtil.savitskyFilter(DataY,nSmooth=n,degree=2)

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
    # want two conditions: on the derivatve and the aboslute value
    # condAboveMed will contain the condition on the abolute value
    condition = (regionFiltered >= threshold)
    n = regionFiltered.size
    tol = int(np.ceil(n/20))
    deriv = FilterDataY(time,np.gradient(regionFiltered),
                        timeFilter=timeFilter)
    if (np.sum(condition) <= tol):
        pct80 = np.percentile(regionFiltered,80)
        condAboveMed = (regionFiltered >= threshold)
        derivCond = (deriv <= 0) 
        condition = condAboveMed & derivCond
        if (np.sum(condition) <= tol):
            condition = condAboveMed
        if (np.sum(condition) <= tol):
            condition = derivCond    
    # for gt, we want where the derivative and the valus are large (ish)
    # ls, oppotie
    if (gt):
        idx = np.where(condition)[0]
    else:
        # note: '~' is pythons binary not (like ! in cs). Matlab-like, ick.
        idx = np.where(condition)[0]
    """
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(regionData)
    plt.plot(regionFiltered)
    plt.plot(idx,regionData[idx],'.')
    plt.axhline(threshold,color='r',linestyle='--',linewidth=2.0)
    plt.subplot(2,1,2)
    plt.plot(deriv)
    plt.axhline(0,color='r',linestyle="--")
    plt.show()
    """
    return idx

    

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
    # some minimum time, accounting for possible delays between low and hi res
    minT = 20e-3
    window = max([minT,deltaT])
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
