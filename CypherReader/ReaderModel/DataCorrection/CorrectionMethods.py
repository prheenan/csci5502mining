# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np

from InterferenceCorrection import GetCorrectedHiRes
from OffsetCorrection import CorrectAndInteprolateZsnsr

def GetCorrectedAndOffsetHighRes(WaveDataGroup,SliceCorrectLow,SliceCorrectHi,
                                 TimeOffset):
    """
    Given a WaveDataGroup with low res an hi res data, returns the
    corrected, high resolution x and y

    Args:
        WaveDataGroup: Model.WaveDataGroup object
        SliceCorrectLow : The slice of the low resolution data to take the 
        correction from
    
        SliceCorrectHi: The slice of the high-resolution data to correct

        TimeOffset: The offset (in seconds) from low to high resolution
        (i.e. zsnsr). We always assume the high resolution data lags, so >0.
    
    Returns:
        A tuple of <Sep,Force> in the offset, corrected limit, just the data
    """
    # get the low res time,force and sep
    time,sep,force = WaveDataGroup.CreateTimeSepForceWaveObject().\
                     GetTimeSepForceAsCols()
    # get the high-res force and time 
    forceHi = WaveDataGroup.HighBandwidthGetForce()
    timeHi = WaveDataGroup.HighBandwidthWaves.values()[0].GetXArray()
    # ignore the low resolution corrected force and information object
    sep,force,_,_ = GetCorrectedFromArrays(time,sep,force,timeHi,forceHi,SliceCorrectLow,
                                           SliceCorrectHi,TimeOffset)
    return sep,force

def GetCorrectedFromArrays(timeLo,sepLo,forceLo,timeHi,forceHi,SliceCorrectLow,
                           SliceCorrectHi,TimeOffset,lowSliceRetr=None,
                           hiSliceAppr=None):
    """
    Given the arrays, gets the corrected versions, including offsetting the 
    zsnsr so that force versus zsnsr is correct

    Args:
        timeLo: the low resolution time
        sepLo: the low resolution separation
        forceLo: the low resolution force
        timeHi: ibid, hi res
        forceHi: ibid, hi res
        SliceCorrectLow: The slice of the low resolution data to fit the 
        wiggles. Typically, this is the approach
       
        SliceCorrectHi: the slice of the high resolution dta to correct. 
        typically retract
    
        TimeOffset: the time offset (hi-low) between the hi and low resolution 
        curves
        
        lowSliceRetr : see GetCorrectedHiRes

        hiSliceAppr : see GetCorrectedHiRes
    """
    # correct the force
    correctLowResForce,correctedHiResForce,info = \
            GetCorrectedHiRes(timeLo,forceLo,SliceCorrectLow,
                              timeHi,forceHi,SliceCorrectHi,
                              lowSliceRetr=lowSliceRetr,
                              hiSliceAppr=hiSliceAppr)
    # offset and interpolate the sep (zsnsr method works fine here) 
    interpHiResSep = CorrectAndInteprolateZsnsr(sepLo,timeLo,TimeOffset,timeHi)
    return interpHiResSep,correctedHiResForce,correctLowResForce,info


def GetTimeOffset(delta1,idx1,delta2,idx2):
    """
    Given two delta and indices in them, gets the average time difference
    between the indices. For example, {xArr1,xArr2} could be low/hi res time,
    and we want an absolute time offset. Assumes that xArr1 and xArr2 have
    the same units.

    Unit Tested by HighbandwidthCorectionGroundTruth

    Args:
       delta1: deltas in the first array
       idx1: indices into the first array, corresponding to specific x values
       delta2: the second array
       idx2: indices into the second array, corresponding to specific x values

    Returns:
        average difference from the indices in units of x values. Meaning,
        sum(xArr[i]-xArr[i])/len(idx1)
    """
    timeDiff = (np.array(idx2) * delta2) - \
               (np.array(idx1) * delta1)
    timeOffset = sum(timeDiff)/len(idx1)
    return timeOffset

def GetCorrectionSlices(idxLowStart,idxHighStart):
    """
    Given low resolution approach touchoff index and high resolution 
    retract touchoff index, gets the appropriate slices for correction

    Unit Tested by HighbandwidthCorectionGroundTruth

    Args:
       idxLowStart: where the low resolution data touches the surface first
       idxHighStart: where the high-resolution data touches the surface last

    Returns:
        tuple of <slicelo,sliceHi>, used by correction methods
    """
    sliceLow = slice(idxLowStart,0,-1)
    sliceHigh = slice(idxHighStart,None,1)
    return sliceLow,sliceHigh
