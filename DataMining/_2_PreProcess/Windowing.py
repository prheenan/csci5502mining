# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
import PyUtil.PlotUtilities as pPlotUtil

from PreProcessor import GetRegions

def GetWindowIndices(inf,idx,rawData,correctedObj,minZ=3,minTime=1e-2):
    """

    Args:
        inf: see GetWindowsFromPreprocessed
        idx: where the approach, dwell,retract etc are
        rawData: the raw data (DataObj), before any correction
        corrObj: the corrected data (DataObj), after correction
        minZ: minimum Z score where we want to start a window
        minTime: minimum time 
    Return:
        
    """
    filterObj = inf.Meta.Correction.FilterObj
    corrData = correctedObj.force
    appr,dwell,retr = GetRegions(idx)
    # just care about the retract, look at the filtered version
    timeCorr = correctedObj.time
    timeOrig = rawData.time
    filterRetr = filterObj.FilterDataY(timeCorr,
                                       corrData[retr])
    # get where the filtered object is over N sigma away ...
    filteredDist = inf.Meta.Summary.CorrectedAndFilteredDist.retract.GradY
    zscore = (np.gradient(filterRetr) - filteredDist.mean)/(filteredDist.std)
    idxAbove = np.where(np.abs(zscore) > minZ)[0]
    deltaT = timeCorr[1]-timeCorr[0]
    minNum = int(minTime/deltaT)
    diff = np.diff(idxAbove)
    # get where we 'jump' in space -- this is (almost certainly) a
    # different region
    idxShifting  =np.where(diff > minNum)[0]
    windowEnds = idxAbove[idxShifting]
    # next window starts one after this ends
    windowStarts = idxAbove[idxShifting+1]
    # that this this ignores the first window... which should
    # start at the first index of idxAbove
    windowStarts = np.insert(windowStarts,0,idxAbove[0])
    windowEnds = np.insert(windowEnds,windowEnds.size,idxAbove[-1])
    # get the window slices as start/end pairs
    offset = retr.start
    slices = [ slice(start,end,1)
               for start,end in zip(windowStarts,windowEnds)]
    N = filterRetr.size
    # add in 'padding' so we have minNum around each event.
    finalSlices = []
    offset = retr.start
    for s in slices:
        start = s.start 
        end = s.stop
        lenV = (end-start)+1
        toAdd = max(0,(minNum-lenV))
        # get the final start and end
        startF = max(0,start-toAdd)
        stopF = min(N,end+toAdd)
        finalSlices.append(slice(startF+offset,stopF+offset,1))
    return finalSlices,offset
    

def GetWindowsFromPreprocessed(inf,windowTime=5e-3,minZ=3):
    """
    Given pre-processed data (see PreProcess Preprocessor.py), gets the indices
    for the high and low resolution windows

    Args:
        inf: output of PreProcess
        minTime: minimum time to save around the window
        minZ: minimum Z score to start condidering something an event.
    Returns:
        indices for hi-res windows
    """
    minTime =windowTime
    splits = inf.Meta.Correction.SplitAfterCorrection
    idxArr = [ splits.TouchoffObjLo, splits.TouchoffObjHi]
    rawDataArr = [ inf.OriginalLo, inf.OriginalHi]
    correctedArr = [inf.Data.LowResData , inf.Data.HiResData]
    # loop through, get the slices (relative indices into data) we care about,
    # as well as the final offsets
    slices = []
    offsets = []
    lowRes = inf.Data.LowResData
    lowSlices,lowOffset = GetWindowIndices(inf, splits.TouchoffObjLo,
                                           inf.OriginalLo,
                                           lowRes,
                                           minZ=minZ,minTime=minTime)
    # we know the low slices (indices) and the time offsets.
    # convert to hi-resolution indices
    deltaLo = lowRes.time[1] - lowRes.time[0]
    deltaHi = inf.Data.HiResData.time[1] - inf.Data.HiResData.time[0]
    hiPointsPerLo = deltaLo/deltaHi
    # get the offset by index
    offsetTime = inf.Meta.Correction.FitObj.TimeOffset
    offsetIdx = int(offsetTime/deltaHi)
    # convert the indices; make sure we round the lower bound *down*,
    # the upper bound *up*
    convSlice = lambda x: slice(int(hiPointsPerLo*x.start)+offsetIdx,
                                np.ceil(hiPointsPerLo*x.stop)+offsetIdx,
                                1)
    hiSlices = [ convSlice(s) for s in lowSlices]
    hiOffset = offsetIdx + int(hiPointsPerLo*lowOffset) 
    return [lowSlices,hiSlices],[lowOffset,hiOffset]

