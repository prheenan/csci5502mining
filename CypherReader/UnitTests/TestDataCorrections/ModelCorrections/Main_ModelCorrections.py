# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
from os.path import expanduser
import sys
sys.path.append("../../../../")
sys.path.append("../../../")
sys.path.append("../../")
sys.path.append("../")

from HighbandwidthCorrectionGroundTruth.HighbandwidthCorrectionGroundTruth\
    import LoadHiResData,GetTimesAndForce,GetZsnsr,idxLowRes,idxHighRes
from PyUtil.CypherUtil import GetSepForce
from ReaderModel.DataCorrection import CorrectionMethods as CorrectionMethods
from ReaderModel.Generic.Model import CreateWaveObjsForCorrectedHiResSepForce
from ReaderModel.Generic.WaveDataGroup import WaveDataGroup

from ReaderModel.DataCorrection.InterferenceCorrection import GetCorrectedHiRes
from ReaderModel.DataCorrection.OffsetCorrection import \
    CorrectAndInteprolateZsnsr
from IgorAdapter.ProcessSingleWave import WaveObj

"""
Assuming that the 'usual' corrections work well,
checks that the model knows how to correct something, given thie indices
"""

def GetOriginalAndCorrected(allData):
    """
    Gets the low resolution time,sep,force objects, and high resolution 
    (corrected) ones, givien 'allData',and assuming the subroutines work

    Args:
        allData: pxp loaded dictionary of {id:WaveDataGroup}, must be the one
        that 'GetTimesAndForce' knows about
    
    Returns:
        <sep,time,force> for low and high res as a flat list, followed by 
        the uncorrected high res force
    """
    lowResTime,lowResForce,highResTime,highResForce = GetTimesAndForce(allData)
    zSnsrLow = GetZsnsr(allData)
    # Get Separation and time (just the data) for the low res
    lowResSepData,_ = GetSepForce({"zsnsr":zSnsrLow,"force":lowResForce})
    lowResSep = WaveObj(DataY=lowResSepData,Note=lowResForce.Note)
    # get the (assumed correct) offsets and interpolated values
    deltaLow = lowResTime[1]-lowResTime[0]
    deltaHi = highResTime[1]-highResTime[0]
    #time offset
    timeOffset = CorrectionMethods.GetTimeOffset(deltaLow,idxLowRes,deltaHi,
                                                 idxHighRes)
    # slices for correction
    idxLow = idxLowRes[0]
    idxHigh = idxHighRes[1]
    sliceLo,sliceHi = CorrectionMethods.GetCorrectionSlices(idxLow,idxHigh)
    # get the corrected Sep and force...
    lowResForceArray = lowResForce.DataY
    highResForceArray = highResForce.DataY
    lowCorr,highCorrForce = GetCorrectedHiRes(lowResTime,lowResForceArray,
                                              sliceLo,highResTime,
                                              highResForceArray,
                                              sliceHi)
    # get the corrected, interpolated sep
    sepExpected = CorrectAndInteprolateZsnsr(lowResSep.DataY,lowResTime,
                                             timeOffset,highResTime)
    return lowResTime,lowResSep,lowResForce,highResTime,sepExpected,\
        highCorrForce,highResForce
    
def run():    
    """
    Assuming that the base-level corrections work, tests the the model is still
    correct

    Args:
        param1: This is the first param.
    
    Returns:
        This is a description of what is returned.
    """
    allData = LoadHiResData()
    # now ask the model to do the same thing, using a waveDataGroup.
    # this is a much high-level operation.
    _,lowResSep,lowResForce,_,highSepCorrected,highForceCorrected,\
        highResForceUnCorr = GetOriginalAndCorrected(allData)
    mGroup = WaveDataGroup({"sep":lowResSep,"force":lowResForce})
    mGroup.HighBandwidthSetAssociatedWaves({"force":highResForceUnCorr})
    # what does the model say? for high resolution
    sepModel,forceModel = \
        CreateWaveObjsForCorrectedHiResSepForce(mGroup,idxLowRes,idxHighRes)
    # XXX just check data for now, check note later 
    sepModelData = sepModel.DataY
    forceModelData =forceModel.DataY
    decimate = 100
    deci = lambda x : x[::decimate]
    assert np.allclose(sepModelData,highSepCorrected)
    assert np.allclose(forceModelData,highForceCorrected)
    # XXX should also correct sep after correcting force (use the polynomial
    # fit to determine how much sep we removed...)

if __name__ == "__main__":
    run()
