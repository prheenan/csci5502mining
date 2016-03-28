from DataMining.DataMiningUtil.Filtering import FilterObj as FilterObj
from PreProcessor import GetRegions,GetDataRegions
from DataMining._2_PreProcess import Windowing as Win

import PyUtil.PlotUtilities as pPlotUtil
import matplotlib.pyplot as plt
import numpy as np
import copy 
regionStyles = [
    dict(color='r',label="Approach"),
    dict(color='g',label="Dwell"),
    dict(color='k',label="Retract")
]


def SafePlot(x,decimate,convert=1):
    return x[::decimate]*convert

def PlotOriginalAndCorrections(orig,corr,saveName,decimate):
    """
    Plots the original and corrected data ontop of each other
    Args:
        orig: original data (DataObj)
        corr: corrections (DataObj)
        savename: base name to save as
        decimate: decimation factor
    """
    fig = pPlotUtil.figure()
    toPn = 1e12
    plt.plot(SafePlot(corr.time,decimate),
             SafePlot(corr.force,decimate,toPn),label="Corrected")
    plt.plot(SafePlot(orig.time,decimate),
             SafePlot(orig.force,decimate,toPn),label="Original")
    pPlotUtil.lazyLabel("Time (s)","Force (pN)","")
    pPlotUtil.savefig(fig,saveName + ".png")


def PlotRegionDistributions(inf,saveName):
    summ = inf.Meta.Summary
    PlotRegionDist(inf.OriginalHi,
                   inf.Meta.Correction.SplitAfterCorrection.TouchoffObjHi,
                   summ.RawDist,
                   saveName + "HiResOrig.png")
    PlotRegionDist(inf.Data.HiResData,
                   inf.Meta.Correction.SplitAfterCorrection.TouchoffObjHi,
                   summ.CorrectedDist,
                   saveName + "HiResCorrected.png")
    
def PlotRegionDist(mData,correctIdx,stats,saveName):
    mCorrectedRegions = GetRegions(correctIdx)
    fig = pPlotUtil.figure(figsize=(14,14))
    nRegions = 3
    nStats = 3
    nBins = 100
    toPn = 1e12
    for i,(region,style,mStat) in enumerate(zip(mCorrectedRegions,regionStyles,
                                                stats)):
        mTimes = mData.time[region]
        force = mData.force[region] * toPn
        plt.subplot(nStats,nRegions,i+1)
        plt.plot(mTimes,force,**style)
        # only label the first
        yLabel = "Force (pN)" if i ==0 else ""
        pPlotUtil.lazyLabel("Time ",yLabel,"")
        plt.subplot(nStats,nRegions,nRegions+i+1)
        # next plot is a histogram of the forces
        plt.hist(force,nBins,**style)
        ylabelHist = "Histogram" if i == 0 else ""
        title = r"${:3.1f}\pm{:3.1f}$pN".format(mStat.RawY.mean*toPn,
                                               mStat.RawY.std*toPn)
        pPlotUtil.lazyLabel("Force (pN)",ylabelHist,title)
        # finally, a histogram of the filtered forces
        plt.subplot(nStats,nRegions,2*nRegions+i+1)
        gradY = np.gradient(force)
        plt.hist(gradY,nBins,**style)
        title = r"${:3.1f}\pm{:3.1f}$pN".\
                format(mStat.GradY.mean*toPn,
                       mStat.GradY.std*toPn)
        pPlotUtil.lazyLabel("Force Differential (pN)",ylabelHist,title)
    pPlotUtil.savefig(fig,saveName)


def PlotRegions(idxOffset,corr,saveName,decimate):
    """
    Plots the three regions (approach, dwell, retratc)

    Args:
        idxOffset: TouchOffObj to use to get the indices
        corr: see PlotOriginalAndCorrections
        saveName:see PlotOriginalAndCorrections
        decimate:see PlotOriginalAndCorrections
    """
    fig = pPlotUtil.figure(figsize=(16,12))
    mCorrectedRegions = GetRegions(idxOffset)
    toPn = 1e12
    # plot each region on the bottom
    nRegions = 3
    for i,(sliceV,style) in enumerate(zip(mCorrectedRegions,
                                              regionStyles)):
        plt.subplot(2,nRegions,nRegions+(i+1))
        mForce = corr.force[sliceV]
        mTime = corr.time[sliceV]
        plt.plot(SafePlot(mTime,decimate),
                 SafePlot(mForce,decimate,toPn),
                 **style)
        # only label the lowest plot
        ylab = "Force (pN)" if (i==0) else ""
        pPlotUtil.lazyLabel("Time (s)",ylab,"")
    plt.subplot(2,1,1)
    plt.plot(SafePlot(corr.time,decimate),
             SafePlot(corr.force,decimate,toPn),label="Corrected Data")
    # plot each region here, colored
    for i,(sliceV,style) in enumerate(zip(mCorrectedRegions,regionStyles)):
        plt.plot(SafePlot(corr.time[sliceV],decimate),
                 SafePlot(corr.force[sliceV],decimate,toPn),
                 **style)
    pPlotUtil.lazyLabel("Time (s)","Force (pN)",
                        "Automatically Finding Curve Regions")
    pPlotUtil.savefig(fig,saveName + "Regions.png")
    
def DebugPlotCorrections(inf,saveName,decimate=1):
    """
    Demontrates how the corrections are taking place
    Args:
        inf: return of PreProcess
        savename: base name to save this under. adds lots of suffixes
        decimate: how much to down-sample the data.
    """
    hiResData = inf.Data.HiResData
    correctIdx = inf.Meta.Correction.SplitAfterCorrection.TouchoffObjHi
    PlotRegions(correctIdx,hiResData,saveName+"_RegionSplit",decimate)
    PlotOriginalAndCorrections(inf.OriginalLo,inf.Data.LowResData,
                               saveName + "_LoRes",1)
    PlotOriginalAndCorrections(inf.OriginalHi,hiResData,
                               saveName + "_HiRes",decimate)
    
def DebugPlotTouchoffLocations(inf,saveName,decimate=1):
    """
    Plots how the touchoff in low and high resolution were identified

    Args:
        inf: see DebugPlotCorrections
        savename: see DebugPlotCorrections
        decimate: see DebugPlotCorrections
    """
    mFiltering = inf.Meta.Correction.FilterObj
    # hi has decimation
    PlotTouchoff(inf.OriginalHi,
                 inf.Meta.Correction.SplitBeforeCorrection.TouchoffObjHi,
                 mFiltering,
                 saveName + "HiRes",decimate)
    # low has no decimation
    PlotTouchoff(inf.OriginalLo,
                 inf.Meta.Correction.SplitBeforeCorrection.TouchoffObjLo,
                 mFiltering,
                 saveName + "LoRes",1)


def PlotTouchoff(lowRes,timeObj,mFiltering,saveName,decimate):
    """
    Plots how the touchoff for 'lowRes' was idenfitied

    Args:
        lowRes: DataObj we want to plot (unfilered 
        timeObj: the TouchoffObj associated with this 
        mFiltering: the filtering object to use 
        savename: see DebugPlotCorrections
        decimate: see DebugPlotCorrections
    """
    rawY = lowRes.force
    meta = lowRes.meta
    time = lowRes.time
    halfwayTime = timeObj.halfwayTime
    startMedTime = timeObj.apprTime
    startMedIdx = timeObj.apprIdx
    endMedTime = timeObj.retrTime
    endMedIdx = timeObj.retrIdx
    # plotting stuff is decimated
    rawYDeci = rawY[::decimate]
    timeDeci = time[::decimate]
    filteredY = mFiltering.FilterDataY(timeDeci,rawYDeci)
    # get the regions that the filtering object is using for the
    idxAppr,idxRetr= \
        FilterObj.GetApproxTouchoffRegions(lowRes,mFiltering.surfaceThickness)
    apprY = rawY[idxAppr]
    retrY = rawY[idxRetr]
    filterYDeci = filteredY
    fig = pPlotUtil.figure(xSize=12,ySize=12)
    # styles for the various line markers
    styleAppr = dict(x=startMedTime,
                     linestyle='--',
                     linewidth=3,
                     color='g',
                     label="End of Approach")
    styleRetr = dict(x=endMedTime,
                     linestyle='-.',
                     linewidth=3,
                     color='r',
                     label="Start of Retract")
    plt.subplot(3,1,1)
    toPn = 1e12
    plt.plot(timeDeci,rawYDeci * toPn,'r-',label="Raw Data")
    plt.plot(timeDeci,filterYDeci * toPn,'b-',label="Filtered Data")
    plt.axvline(halfwayTime,label="Halfway point")
    plt.axvline(**styleAppr)
    plt.axvline(**styleRetr)
    pPlotUtil.lazyLabel("Time (s)","Force (pN)",
                        "Breaking up force versus time",legendBgColor='w',
                        frameon=True)
    plt.subplot(3,1,2)
    # plot around the approach touchoff
    timeAppr = lowRes.time[idxAppr]
    plt.plot(timeAppr,apprY*toPn,'r-',label="Approach")
    filterApprY = mFiltering.FilterDataY(timeAppr,apprY)
    plt.axvline(**styleAppr)
    plt.plot(timeAppr,filterApprY*toPn,'b-',lw=2,label="Filtered Approach")
    
    pPlotUtil.lazyLabel("Time (s)","Force (pN)","",legendBgColor='w',
                        frameon=True)
    plt.subplot(3,1,3)
    timeRetr= lowRes.time[idxRetr]
    plt.axvline(**styleRetr)
    plt.plot(timeRetr,retrY*toPn,'r-',label="Retract")
    filterApprY = mFiltering.FilterDataY(timeRetr,retrY)
    plt.plot(timeRetr,filterApprY*toPn,'b-',lw=2,label="Filtered Retract")
    pPlotUtil.lazyLabel("Time (s)","Force (pN)","",legendBgColor='w',
                        frameon=True)
    pPlotUtil.savefig(fig,saveName + ".png")


def PlotAllWindows(inf,finalSlices,saveName,decimate):
    """
    Plots all the windows for the low and high res

    Args:
        inf: see PlotWindowing
        finalSlices: the slices for the each
        saveName : base name to save, see PlotWindowing
        decimate: see PlotWindowing
    """
    names = ["LowRes,","HighRes"]
    decimations = [1,decimate]
    splits = inf.Meta.Correction.SplitAfterCorrection
    idxArr = [ splits.TouchoffObjLo, splits.TouchoffObjHi]
    rawDataArr = [ inf.OriginalLo, inf.OriginalHi]
    correctedArr = [inf.Data.LowResData , inf.Data.HiResData]
    for idx,rawData,corrected,s,deci,name in zip(idxArr,rawDataArr,correctedArr,
                                                 finalSlices,decimations,
                                                 names):
        PlotWindowing(inf,s,idx,rawData,corrected,
                      saveName + name + ".png",deci)

    
def PlotWindowing(inf,finalSlices,index,rawData,corrData,saveName,decimate):
    """
    Given an info object, slices, and all the specific data, plots the windows
    that were found

    Args:
        inf: PreProcess information object
        finalSlices: list of slices
        index: the indices associated with the approach,dwell,retract (eg:
        inf.Meta.Correction.SplitAfterCorrection.TouchoffObjLo

        rawData: the DataObj, before the corrections. e.g.: inf.OriginalLo
        corrData: the DataObj, after the corrections. e.g.: inf.Data.HiResData
        saveName: what to save the file as.
        decimate: how much to decimate during plotting
        
    """
    mFilter = inf.Meta.Correction.FilterObj
    appr,dwell,retr = GetRegions(index)
    timeOrig = rawData.time
    timeCorr = corrData.time
    corrForce = corrData.force
    # filter just the retraction (if we do the whole thing, get messy edge
    # effects
    filterRetr = mFilter.FilterDataY(timeCorr,corrForce[retr])
    nSlices = len(finalSlices)
    nPlots = 3
    fig = pPlotUtil.figure(xSize=16,ySize=12)
    toPn = 1e12
    plt.subplot(nPlots,1,1)
    plt.plot(timeOrig[retr],toPn*rawData.force[retr],label="Raw Retract")
    pPlotUtil.lazyLabel("","Force (pN)",
                        "Automatic Identification of Ruptures")
    plt.subplot(nPlots,1,2)
    plt.plot(timeCorr[retr][::decimate],toPn*corrForce[retr][::decimate],'b,',
             label="Interference Corrected")
    plt.plot(timeCorr[retr][::decimate],toPn*filterRetr[::decimate],'r-')
    pPlotUtil.lazyLabel("Time","Force (pN)","")
    # slices are absolute; we are plotting against just the retraction,
    # so subtrace off the trraction start
    offset = retr.start
    for i,s in enumerate(finalSlices):
        plt.subplot(nPlots,nSlices,nSlices*(nPlots-1)+i+1)
        relativeSlice = slice(s.start-offset,
                              s.stop-offset,1)
        timeSlice = timeCorr[relativeSlice]
        timeMsRel = (timeSlice-min(timeSlice))*1000
        plt.plot(timeMsRel,filterRetr[relativeSlice]*toPn,'r.',ms=2.0)
        yLabel = "Force (pN)" if i ==0 else ""
        pPlotUtil.lazyLabel("Relative Time (ms)",yLabel,
                            "Rupture {:d}".format(i+1))
    pPlotUtil.savefig(fig,saveName)


def PlotProfile(basename,inf,mProc,decimate):
    """
    Args:
       basename: base name to save
       inf/mProc: output of PreProcessMain
       decimate: decimation factor for high res. Recommend plotting less than
       O(100K) points 
    """
    slices,_ = Win.GetWindowsFromPreprocessed(inf)
    PlotAllWindows(inf,slices,basename + "WindowingLow",decimate)
    PlotRegionDistributions(inf,basename + "RegionDist")
    DebugPlotTouchoffLocations(inf,basename + "Splitting.png",
                               decimate=decimate)
    DebugPlotCorrections(inf,basename+"corr",
                         decimate=decimate)

