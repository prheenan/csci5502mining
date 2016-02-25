# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
# need to add the utilities class. Want 'home' to be platform independent
from os.path import expanduser
home = expanduser("~")
# get the utilties directory (assume it lives in ~/utilities/python)
# but simple to change
path= home +"/utilities/python"
import sys
sys.path.append(path)
sys.path.append("../../../")
sys.path.append("../../../../")
# import the patrick-specific utilities
import GenUtilities  as pGenUtil
import PlotUtilities as pPlotUtil
import CheckpointUtilities as pCheckUtil
from CypherReader.IgorAdapter import PxpLoader,ProcessSingleWave
from PyUtil import CypherUtil
from CypherReader.ReaderModel.DataCorrection.InterferenceCorrection import \
    GetCorrectedHiRes,DEF_POLYFIT

from CypherReader.ReaderModel.DataCorrection.OffsetCorrection import \
    CorrectAndInteprolateZsnsr

from CypherReader.ReaderModel.DataCorrection import \
    CorrectionMethods as CorrectionMethods

# indices of everything, absolute, of high and low res
idxLowRes = np.array([37430,86999])
idxHighRes = np.array([3773000,8729900])

def GetZsnsr(allData):
    """
    Gets the zsnsr from a pxp file read in from PxpLoader

    Args:
        allData: dict of <id>:<WaveDataGroup>
    Return:
        Zsnsr WaveObj
    """
    zsnsr = allData['Image1334']['zsnsr']
    return zsnsr


def GetTimesAndForce(allData):
    """
    Gets time an force (for low and high resolution) for the test data

    Args:
        allData: dict of <id>:<WaveDataGroup>
    Return:
        tuple of lowResTime,lowResForce,highRestime,highResForce.
    """
    deflStr = 'deflv'
    datHigh = allData['Image1335']
    NoteHi = datHigh.values()[0].Note
    highResForce = ProcessSingleWave.WaveObj(DataY=CypherUtil.GetForce(datHigh),
                                             Note=NoteHi)
    highResTime =datHigh[deflStr].GetXArray()
    datLow = allData['Image1334']
    NoteLow = datLow.values()[0].Note
    lowResForce = ProcessSingleWave.WaveObj(DataY=CypherUtil.GetForce(datLow),
                                            Note=NoteLow)
    lowResTime = datLow[deflStr].GetXArray()
    return lowResTime,lowResForce,highResTime,highResForce

def PlotIdxAndTimes(allData):
    """
    Reads in 'alldata' plots against the indices (for sanity checking)

    Args:
        allData: dict of <id>:<WaveDataGroup>
    Return:
        None
    """
    lowResTime,lowResForce,highResTime,highResForce = GetTimesAndForce(allData)
    timeDeltaLow = lowResTime[1]-lowResTime[0]
    timeDeltaHi = highResTime[1]-highResTime[0]
    print("Delta Low / Hi Res Time is {:8.06g}/{:8.06g}".\
          format(timeDeltaLow,timeDeltaHi))
    #get hand-labelled indices for the low and high res
    fig = pPlotUtil.figure(ySize=12,xSize=8)
    plt.subplot(3,1,1)
    plt.plot(highResTime,highResForce.DataY,'r,',label="hiRes")
    plt.plot(lowResTime,lowResForce.DataY,label="lowRes")
    pPlotUtil.lazyLabel("time","deflV","Overlay of plots")
    rangeV = max(np.max(lowResTime),np.max(highResTime))
    deltaX = rangeV/200
    for i,(low,high) in enumerate(zip(idxLowRes,idxHighRes)):
        plt.subplot(3,1,i+2)    
        plt.plot(highResTime,highResForce.DataY,'r,',label="hiRes")
        plt.plot(lowResTime,lowResForce.DataY,label="lowRes")
        lowTime = low * timeDeltaLow
        highTime = high * timeDeltaHi
        plt.axvline(lowTime,label="low res, idx {:d}, time {:.4g}".\
                    format(int(low),lowTime))
        plt.axvline(highTime,label="hi res, idx {:d}, time {:.4g}".\
                    format(int(high),highTime))
        plt.xlim([lowTime-2*deltaX,
                  highTime+2*deltaX])
        plt.ylim([5.5e-10,7e-10])
        pPlotUtil.lazyLabel("time","deflV","Overlay of plots")
    pPlotUtil.savefig(fig,"./output_idx.png")

def PlotCorrections(allData):
    """
    Reads in 'alldata', corrects with a high degree polynomal.

    Args:
        allData: dict of <id>:<WaveDataGroup>
    Return:
        None
    """
    lowResTime,lowResForce,highResTime,highResForce = GetTimesAndForce(allData)
    # first just check we can generally correct...
    idxTouch1 = idxLowRes[0]
    idxTouch2 = idxLowRes[1]
    # fit from the first touch backwards
    slice1 = slice(idxTouch1,0,-1)
    # ... and correct from the second touch forwards
    slice2 = slice(idxTouch2,None,1)
    lowResForceArray= lowResForce.DataY
    lowCorr,highCorr = GetCorrectedHiRes(lowResTime,lowResForceArray,slice1,
                                         lowResTime,lowResForceArray,slice2)
    # do the same, with the high res data
    sliceHigh = slice(idxHighRes[1],None,1)
    highResForceArray = highResForce.DataY
    lowCorrHiRes,highCorrRes = GetCorrectedHiRes(lowResTime,lowResForceArray,
                                                 slice1,highResTime,
                                                 highResForceArray,sliceHigh)
    fig = pPlotUtil.figure(xSize=6,ySize=8)
    plt.subplot(2,1,1)
    plt.plot(lowResTime,lowResForceArray,label="raw")
    plt.plot(lowResTime,lowCorr,'b-',lw=2,label="Corrected, Appr")
    plt.plot(lowResTime,highCorr,'g--',lw=2,label="Corrected, Retr")
    pPlotUtil.lazyLabel("time","Force [pN]","")
    plt.subplot(2,1,2)
    plt.plot(highResTime,highResForceArray,'r,',label="raw")
    plt.plot(lowResTime,lowResForceArray,'b-',lw=2,label="Raw, Low Res")
    plt.plot(lowResTime,lowCorrHiRes,'b-',lw=2,label="Corrected, Appr")
    plt.plot(highResTime,highCorrRes,'g,',lw=2,label="Corrected, High Res")
    pPlotUtil.lazyLabel("time","Force [pN]","")
    plt.show()
    pPlotUtil.savefig(fig,"./output_corrected.png")
    np.savez_compressed("./Corrected_Low.npy",lowCorr)
    np.savez_compressed("./Corrected_High.npy",highCorrRes)

def PlotZsnsrOffsetAndInterpolation(allData):
    """
    Plots the zsnsr and interpolated / corrected version, giving our indices.
    Saves out the corrected Zsnsr in a .npy folder
 
    Assumes that offset has been saved

    Args:
        allData: data to use
    """
    lowResTime,lowResForce,highResTime,highResForce = GetTimesAndForce(allData)
    # first get the zsnsr..
    zsnsr = GetZsnsr(allData)
    zsnsrTime = zsnsr.GetXArray()
    # get the time difference
    timeDiff = 0
    for low,high in zip(idxLowRes,idxHighRes):
        timeDiff += abs(highResTime[high]-lowResTime[low])
    timeDiff = timeDiff/len(idxLowRes)
    interpZ = CorrectAndInteprolateZsnsr(zsnsr.DataY,zsnsrTime,timeDiff,
                                         highResTime)
    np.savez_compressed("./Zsnsr_Interp.npy",interpZ)
    fig = pPlotUtil.figure()
    ax = plt.subplot(3,1,1)
    plt.plot(zsnsrTime,zsnsr.DataY,'r,',label="original")
    plt.plot(highResTime,interpZ,'b,',label="shifted and interpolated")
    pPlotUtil.lazyLabel("time (s)","zsnsr","")
    ax = plt.subplot(3,1,2)
    plt.plot(zsnsrTime,zsnsr.DataY,'r,',label="original")
    plt.plot(highResTime,interpZ,'b,',label="shifted and interpolated")
    # zoom in ... 
    idxZoom = idxHighRes[0]
    idxDiff = 100000
    timeZoom = highResTime[idxZoom]
    plt.xlim([timeZoom-3*timeDiff,timeZoom+3*timeDiff])
    plt.ylim([interpZ[idxZoom-idxDiff],interpZ[idxZoom+idxDiff]])
    pPlotUtil.lazyLabel("time (s)","zsnsr","")
    plt.subplot(3,1,3)
    plt.plot(zsnsr.DataY,lowResForce.DataY,'r,')
    plt.plot(interpZ,highResForce.DataY,'b,')
    pPlotUtil.lazyLabel("time (s)","force","")
    pPlotUtil.savefig(fig,"./output_zsnsr.png")
    
def TestOffsetAndInterpolation(allData):
    """
    Ensures the interpolator/offset correction is working well

    Args:
        allData: data to use
    """
    zsnsr = GetZsnsr(allData)
    zsnsrTime = zsnsr.GetXArray()
    timeDiff = zsnsrTime[1]-zsnsrTime[0]
    timeEnd = zsnsrTime[-1]
    nInterp = [1,2,10,100]
    zArray = zsnsr.DataY
    # get a n-x interpolation factor
    for n in nInterp:
        newTimes = np.linspace(0,timeEnd,n*zsnsrTime.size,endpoint=True)
        # do interpolation without correction
        interpZ = CorrectAndInteprolateZsnsr(zArray,zsnsrTime,0,
                                             newTimes)
        # get the down-sampled array...
        downSamp = interpZ[::n]
        assert np.allclose(downSamp,zArray) , "Interpolation-only is broken"
    print("Interpolation-only passed")
    # POST: just correction worked fine.
    # try using offsets now
    nMax = zArray.size
    # make the offsets exact, dont worry about that kind of extreme edge case
    idxOffsets = np.linspace(0,nMax,num=10,endpoint=False,dtype=np.uint64)
    timeOffsets = idxOffsets * timeDiff
    for i,timeDiff in enumerate(timeOffsets):
        # do correcion without interpolation
        offIdx = idxOffsets[i]
        # note we interpolate onto zsnsrTime, so we need to offset that too,
        # to avoid any interpolation stuff
        interpZ = CorrectAndInteprolateZsnsr(zArray,zsnsrTime,timeDiff,
                                             zsnsrTime)
        # get the part of the array which wasn't offset
        zSize = zArray.size
        trueOffset = zArray[:(zSize-offIdx)]
        # get the actual offset array
        toCheck = interpZ[offIdx:]
        # make sure they match. note we only look after offIdx
        assert np.allclose(trueOffset,toCheck) ,\
            "Offset-only is broken {:s} / {:s}".format(trueOffset,toCheck)
    print("Offset-only passed")
    # now the real deal: interpolation and offsetting...
    for n in nInterp:
        for i,timeDiff in enumerate(timeOffsets):
            offIdx = idxOffsets[i]
            # get the new interpolated times
            newTimes = np.linspace(0,timeEnd,n*zsnsrTime.size,endpoint=True)
            # get the associated delta
            deltaTimes = newTimes[1] - newTimes[0]
            # do interpolation with offset correction
            interpOffIdx = int(np.round(timeDiff/deltaTimes))
            interpZ = CorrectAndInteprolateZsnsr(zArray,zsnsrTime,timeDiff,
                                                 newTimes)
            # get the arrays we want...
            downSamp = zArray[:(zSize-offIdx)]
            # get the actual offset array
            offIdxHiRes = np.round(timeDiff/deltaTimes)
            trueSamp = interpZ[offIdxHiRes::n]
            assert np.allclose(downSamp,trueSamp) ,\
                "Interpolation-offset is broken"
    print("interpolation-offset passed")

    
def TestInterferenceCorrection(allData):
    """
    Tests interference correction

    Args:
        allData: dictionary of data to use
    """
    lowResTime,lowResForce,highResTime,highResForce = GetTimesAndForce(allData)
    # first, try correcting the low resolution stuff
    idxLowStart = idxLowRes[0]
    idxHighStart = idxLowRes[1]
    maxOffset = idxLowStart
    offsets = np.linspace(0,maxOffset/10,10,dtype=np.uint64)
    lowResForceArray = lowResForce.DataY
    for o in offsets:
        # correct the low resolution stuff
        slice1,slice2 = CorrectionMethods.GetCorrectionSlices(idxLowStart-o,
                                                              idxHighStart)
        nPoints = idxLowStart-o
        degree = DEF_POLYFIT
        lowCorr,highCorr = GetCorrectedHiRes(lowResTime,lowResForceArray,slice1,
                                             lowResTime,lowResForceArray,
                                             slice2)
        # corrected high res is supposed to not go out of bounds.. make
        # sure it doesn't touch anything 'bad'
        maxN = lowResTime.size
        trueN = min(idxHighStart+nPoints,maxN)
        nPointsTrue = trueN-idxHighStart
        trueSlice2 = slice(idxHighStart,trueN,1)
        # Checking the approach was corrected properly...
        # get the predicted values of the approach slice (reverse it)
        fitXSlice = np.copy(lowResTime[slice1])[::-1]
        fitXSlice -= fitXSlice[0]
        fitYSlice = lowResForceArray[slice1][:][::-1]
        # get the fit coefficients and values
        mVals = np.polyval(np.polyfit(fitXSlice,fitYSlice,deg=degree),fitXSlice)
        # get the 'de-corrected' low Res
        deCorr = np.copy(lowCorr)
        deCorr[slice1] += mVals[::-1] 
        # now 'de-correct' the retraction
        deCorrHigh = np.copy(highCorr)
        deCorrHigh[trueSlice2] += mVals[:nPointsTrue]
        # both low and high resolution are the same here.
        assert np.allclose(deCorr,lowResForceArray) , "Low resolution broken"
        assert np.allclose(deCorrHigh,lowResForceArray) ,\
            "Hi resolution broken"
    # POST: worked fine for low and low resolution. What about low and high?
    highResForceArray = highResForce.DataY
    # idxHighStart is now the high-resolution index
    idxHighStart = idxHighRes[1]
    for o in offsets:
        # correct the low resolution stuff
        slice1,slice2 = CorrectionMethods.GetCorrectionSlices(idxLowStart-o,
                                                              idxHighStart)
        nPoints = idxLowStart-o
        # use the hi res index for the hi res force
        degree = DEF_POLYFIT
        lowCorr,highCorr = GetCorrectedHiRes(lowResTime,lowResForceArray,slice1,
                                             highResTime,highResForceArray,
                                             slice2)
        # corrected high res is supposed to not go out of bounds.. make
        # sure it doesn't touch anything 'bad'
        maxN = highResTime.size
        # get the time delta of the first slice
        deltaSmall = lowResTime[1] - lowResTime[0]
        maxTSmall = nPoints*deltaSmall
        # get the number of points that corresponds to
        deltaHigh = highResTime[1]-highResTime[0]
        maxNHighRes = np.round(maxTSmall/deltaHigh)
        trueN = min(maxN,idxHighStart+maxNHighRes)
        trueSlice2 = slice(idxHighStart,trueN,1)
        # Checking the approach was corrected properly...
        # get the predicted values of the approach slice (reverse it)
        fitXSlice = np.copy(lowResTime[slice1])[::-1]
        fitXSlice -= fitXSlice[0]
        fitYSlice = lowResForceArray[slice1][:][::-1]
        # get the fit coefficients and values
        mCoeffs = np.polyfit(fitXSlice,fitYSlice,deg=degree)
        mVals = np.polyval(mCoeffs,fitXSlice)
        # get the 'de-corrected' low Res
        deCorr = np.copy(lowCorr)
        deCorr[slice1] += mVals[::-1] 
        # now 'de-correct' the retraction
        xDeCorr = np.copy(highResTime[trueSlice2])
        xDeCorr -= xDeCorr[0]
        mValsHigh = np.polyval(mCoeffs,xDeCorr)
        deCorrHigh = np.copy(highCorr)
        deCorrHigh[trueSlice2] += mValsHigh
        assert np.allclose(deCorr,lowResForceArray) , "lo resolution broken"
        assert np.allclose(deCorrHigh,highResForceArray) ,\
            "hi resolution (2) broken"
    print("all correction tests passed.")

def CheckTimeOffsetWorks(allData):
    """
    Checks that getting the time offset and work

    Args:
        allData: dictionary of data to use
    """
    lowResTime,_,highResTime,_ = GetTimesAndForce(allData)
    timeDiff = 0
    deltaHi = highResTime[1]-highResTime[0]
    deltaLo = lowResTime[1]- lowResTime[0]
    for low,high in zip(idxLowRes,idxHighRes):
        timeDiff += abs(highResTime[high]-lowResTime[low])
    timeDiff = timeDiff/len(idxLowRes)
    assert np.allclose(timeDiff,
                       CorrectionMethods.GetTimeOffset(deltaLo,idxLowRes,
                                                       deltaHi,idxHighRes))
    # now check that the slices work
    startLo = idxLowRes[0]
    startHi = idxHighRes[1]
    low,high = CorrectionMethods.GetCorrectionSlices(startLo,startHi)
    assert low.start == startLo
    assert low.step == -1
    assert low.stop == 0
    # make sure it works for hi res too
    assert high.start == startHi
    assert high.step == 1
    assert high.stop is None

    
                                                
def DemoLowResPlot(allData):
    """
    Makes a pretty plot for the low-resolution data

    Args:
        allData: dictionary of data to use
    """
    lowResTime,lowResForce,highResTime,highResForce = GetTimesAndForce(allData)
    # first, correct the wiggles
    # fit from the first touch backwards
    slice1 = slice(idxLowRes[0],0,-1)
    # ... and correct from the second touch forwards
    slice2 = slice(idxLowRes[1],None,1)
    lowResForceArray= lowResForce.DataY
    lowCorr,highCorr = GetCorrectedHiRes(lowResTime,lowResForceArray,slice1,
                                         lowResTime,lowResForceArray,slice2)
    idxStart = slice2.start
    n = highCorr.size
    idxEnd = idxStart + int((n-idxStart)/2)
    toPlotY = highCorr[idxStart:idxEnd]
    toPlotX = lowResTime[idxStart:idxEnd]
    # correct for the force offset
    toPlotY -= np.median(toPlotY)
    toPlotX -= np.min(toPlotX)
    # convert to pN, flip about y axis
    toPlotY *= -1e12
    fig = pPlotUtil.figure()
    plt.plot(toPlotX,toPlotY)
    pPlotUtil.lazyLabel("Time (seconds)","Force [pN]","Protein Unfolding Curve")
    pPlotUtil.savefig(fig,"./output_demoFig.png")

def LoadHiResData(dataFile="../../LocalData/NUG2TestData.pxp"):
    """
    Loads in the high resolution data

    Args:
        dataFile: Where the data lives
    Returns:
        WaveGroup object of the high res data
    """
    data = dataFile
    return PxpLoader.LoadPxp(data)


def run():
    """
    Reads in the high-bandwidth data, and generates plots showing why 
    we picked the data we did... 

    Args:
        None
    """
    allData = LoadHiResData()
    # make the plots of the overlays...
    # Commenting out the plotting functions for now...
    #PlotIdxAndTimes(allData)
    #PlotCorrections(allData)
    #PlotZsnsrOffsetAndInterpolation(allData)
    #DemoLowResPlot(allData)
    # check that the time offsetting works
    CheckTimeOffsetWorks(allData)
    # #test interpolation and offsetting...
    TestOffsetAndInterpolation(allData)
    # test polynomial correction
    TestInterferenceCorrection(allData)
    
if __name__ == "__main__":
    run()
