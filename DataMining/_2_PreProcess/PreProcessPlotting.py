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
    pPlotUtil.lazyLabel("Time (s)","Force (pN)",
                        "Correcting Interference Artifact")
    pPlotUtil.savefig(fig,saveName + ".png")


def PlotRegionDistributions(inf,saveName,decimate):
    """
    Plots the region distributions for the low and high resolution
    """
    summ = inf.Meta.Summary
    PlotRegionDist(inf.OriginalHi,
                   inf.Meta.Correction.SplitAfterCorrection.TouchoffObjHi,
                   summ.RawDist,
                   saveName + "HiResOrig.png",\
                   decimate)
    PlotRegionDist(inf.Data.HiResData,
                   inf.Meta.Correction.SplitAfterCorrection.TouchoffObjHi,
                   summ.CorrectedDist,
                   saveName + "HiResCorrected.png",\
                   decimate)
    
def PlotRegionDist(mData,correctIdx,stats,saveName,decimate):
    """
    Plots the distributions of the approach, dwell, and retraxt
    
    Args:
        mData: DataObj (ie: with time,sep,force)
        correctIdx: the indices correcsponding to the regions we want
        stats: the stats we will display above the (hopefully matching) 
        distributions
       
        saveName: path to save output
        decimate: decimation factor
    """
    mCorrectedRegions = GetRegions(correctIdx)
    fig = pPlotUtil.figure(figsize=(18,18))
    nRegions = 3
    nStats = 3
    nBins = 30
    toPn = 1e12
    for i,(region,style,mStat) in enumerate(zip(mCorrectedRegions,regionStyles,
                                                stats)):
        mTimes = mData.time[region]
        force = mData.force[region]
        forcePn = force * toPn
        plt.subplot(nStats,nRegions,i+1)
        # plot the decimated force
        plt.plot(SafePlot(mTimes,decimate),
                 SafePlot(force,decimate,toPn),**style)
        # only label the first
        yLabel = "Force (pN)" if i ==0 else ""
        pPlotUtil.lazyLabel("Time ",yLabel,"")
        plt.subplot(nStats,nRegions,nRegions+i+1)
        # next plot is a histogram of the forces
        plt.hist(forcePn,nBins,**style)
        ylabelHist = "Histogram" if i == 0 else ""
        title = r"${:3.1f}\pm{:3.1f}$pN".format(mStat.RawY.mean*toPn,
                                               mStat.RawY.std*toPn)
        pPlotUtil.lazyLabel("Force (pN)",ylabelHist,title)
        # finally, a histogram of the filtered forces
        plt.subplot(nStats,nRegions,2*nRegions+i+1)
        gradY = np.gradient(forcePn)
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
    plt.plot(timeAppr,filterApprY*toPn,'b-',lw=2,label="Filtered Approach")
    plt.axvline(**styleAppr)

    pPlotUtil.lazyLabel("Time (s)","Force (pN)","",legendBgColor='w',
                        frameon=True)
    plt.subplot(3,1,3)
    timeRetr= lowRes.time[idxRetr]
    plt.plot(timeRetr,retrY*toPn,'r-',label="Retract")
    filterApprY = mFiltering.FilterDataY(timeRetr,retrY)
    plt.plot(timeRetr,filterApprY*toPn,'b-',lw=2,label="Filtered Retract")
    plt.axvline(**styleRetr)
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
    corrForceRetrRaw = corrForce[retr]
    timeRetrRaw = timeCorr[retr]
    timeRetrDeci = timeRetrRaw[::decimate]
    filterRetr = mFilter.FilterDataY(timeRetrDeci,corrForceRetrRaw[::decimate])
    nSlices = len(finalSlices)
    nPlots = 3
    fig = pPlotUtil.figure(xSize=16,ySize=12)
    toPn = 1e12
    plt.subplot(nPlots,1,1)
    plt.plot(timeOrig[retr],toPn*rawData.force[retr],'k,',alpha=0.7,
             label="Raw Retract")
    pPlotUtil.lazyLabel("","Force (pN)",
                        "Automatic Identification of Ruptures")
    plt.subplot(nPlots,1,2)
    plt.plot(timeRetrRaw,toPn*corrForceRetrRaw,'r,',
             label="Interference Corrected")
    plt.plot(timeRetrDeci,toPn*filterRetr,'b-',
             linewidth=1.0,label="Filtered")
    pPlotUtil.lazyLabel("Time","Force (pN)","")
    # slices are absolute; we are plotting against just the retraction,
    # so subtrace off the trraction start
    offset = retr.start
    for i,s in enumerate(finalSlices):
        plt.subplot(nPlots,nSlices,nSlices*(nPlots-1)+i+1)
        relativeSlice = slice(s.start-offset,
                              s.stop-offset,1)
        # get the time in ms and force in pN
        timeSlice = timeRetrRaw[relativeSlice]
        timeMsRel = (timeSlice-min(timeSlice))*1000
        forceRel = corrForceRetrRaw[relativeSlice]*toPn
        # filter the window...
        forceFiltWindow = mFilter.FilterDataY(timeSlice,forceRel)
        plt.plot(timeMsRel,forceRel,'r.',
                 ms=2.0)
        plt.plot(timeMsRel,forceFiltWindow,'b-',
                 linewidth=2.0)
        yLabel = "Force (pN)" if i ==0 else ""
        pPlotUtil.lazyLabel("Time (ms)",yLabel,
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
    PlotRegionDistributions(inf,basename + "RegionDist",decimate)
    DebugPlotTouchoffLocations(inf,basename + "Splitting.png",
                               decimate=decimate)
    DebugPlotCorrections(inf,basename+"corr",
                         decimate=decimate)
    PlotAllWindows(inf,slices,basename + "Windowing",decimate)


def PlotGivenWindows(filterV,time,sep,force,plotFunc,timeConst=1000,
                     timeStr="ms",labels=None):
    """
    Given windows and information on how to plot, plots the data and the
    filtered data.

    Args:
        filterV: FilterObj to use, 
        time: time basis to use
        sep: separation to use 
        force: force to use
        plotFunc: call this for each window, with the window number
        timeConst: what to multiply the time basis by
        timeStr: units to label the time basis 
        labels: if not None, list of elements, one per window. each element
        is a tuple of (start,end) *relative* index into the event in this window
    """
    toPn = 1e12
    for i,(time,force) in enumerate(zip(time,force)):
        n = time.size
        plotFunc(i)
        tMap = lambda x: (x-min(time))*timeConst
        timeMsRel = tMap(time)
        forcePnRel = (force - np.median(force[:int(n/2)])) * toPn
        filterPnForce =  filterV.FilterDataY(time,forcePnRel)
        rawLab = "Raw" if i ==0 else ""
        filterLab = "Filtered" if i ==0 else ""
        y = "Force (pN)" if i == 0 else ""
        plt.plot(timeMsRel,forcePnRel,'r-',label=rawLab)
        plt.plot(timeMsRel,filterPnForce,'b-',lw=3,label=filterLab)
        # add in labels, if we have them
        if (labels is not None):
            labStart =  r'Label$_i$' if (i == 0) else ""
            labEnd =  r'Label$_f$' if (i == 0) else ""
            plt.axvline(tMap(time[labels[i][0]]),label=labStart)
            plt.axvline(tMap(time[labels[i][1]]),label=labEnd)
        pPlotUtil.lazyLabel("Time ({:s})".format(timeStr),
                            y,"Event {:d}".format(i))
    
def PlotWindowsPreProcessed(mProc,outFile):
    """
    Given only the output of PreProcessMain, plots the windows

    Args:
       mProc: (second) output of PreProcessMain
       outFile: where to save
    """
    timeWindowLo,sepWindowLo,forceWindowLo = \
            mProc.LowResData.GetTimeSepForce()
    timeWindowHi,sepWindowHi,forceWindowHi = \
            mProc.HiResData.GetTimeSepForce()
    filtering = mProc.Meta.Correction.FilterObj
    nWindows = len(timeWindowHi)
    subPlotLo = lambda x: plt.subplot(3,nWindows,(x+1))
    subPlotHi = lambda x: plt.subplot(3,nWindows,nWindows+(x+1))
    fig = pPlotUtil.figure(ySize=12,xSize=24)
    PlotGivenWindows(filtering,timeWindowLo,sepWindowLo,forceWindowLo,
                    subPlotLo)
    PlotGivenWindows(filtering,timeWindowHi,sepWindowHi,forceWindowHi,
                     subPlotHi)
    if (mProc.HasLabels()):
        labels = mProc.GetLabelIdxRelativeToWindows()
        # fudge is how many points to left or right of labels to go
        fudge = 100
        getByLabelledEvt = lambda x: \
            [np.concatenate(x)[l.start-fudge:l.end+fudge] for l in labels]
        # labels rel is the location of the labels relative to the windows
        # we just made
        labelsRel = [ (fudge,fudge+(l.end-l.start)) for l in labels]
        catTime = getByLabelledEvt(timeWindowHi)
        catForce   =getByLabelledEvt(forceWindowHi)
        catSep = getByLabelledEvt(sepWindowHi)
        subplotLab = lambda x: plt.subplot(3,nWindows,2*nWindows+(x+1))
        # for this one only, go ahead and change the filtering time constant.
        # XXX should fix
        hiResFilter = copy.deepcopy(filtering)
        hiResFilter.timeFilter = 5e-6
        PlotGivenWindows(hiResFilter,catTime,None,catForce,
                         subplotLab,timeConst=1e6,timeStr=r"$\mu s$",
                         labels=labelsRel)
    pPlotUtil.savefig(fig,outFile)
    


def PlotWindowsWithLabels(processedObj,figsize=(24,18),fontsize=20):
    """
    Given a processed object, plots the windows with the labels. Does *not*
    save, just creates the figure

    Args:
       processedObj: a PreProcesedObject
    Returns:
       the figure reference created
    """
    # loop through and plot just the regions around the events
    fig = plt.figure()
    # get every window
    timeWindow,sepWindow,forceWindow = \
        processedObj.HiResData.GetTimeSepForce()
    # plot the individual windows
    fig = pPlotUtil.figure(figsize=figsize)
    nWindows = len(sepWindow)
    # loop through *each* window and plokt
    timeConst = 8e-5
    labels = processedObj.Labels
    # print off the label information, relative to the windows
    labelsRelativeToIndex = processedObj.GetLabelIdxRelativeToWindows()
    for window,labelRel,labelAbs in zip(processedObj.WindowBounds,
                                        labelsRelativeToIndex,
                                        labels):
        print("Label at idx: {:s}, relative to start of {:s}: {:s}".\
              format(labelAbs,window,labelRel))
    mFiltering = FilterObj.Filter(timeConst = timeConst)
    for i,(time,sep,force) in enumerate(zip(timeWindow,sepWindow,forceWindow)):
        # convert force to pN (just for plotting)
        force *= 1e12
        # also normalize it so the median before the event is zero (again,
        # just to make the plot pretty)
        deltaT = time[1]-time[0]
        startIdxInWindow = int((labels[i].StartTime-time[0])/(deltaT))
        force -= np.median(force[:startIdxInWindow])
        # get the filtered version too!
        filteredForce=mFiltering.FilterDataY(time,force)
        # this would be a great feature -- the derivative of the filtered force,
        # normalized to a standard normal curve
        filteredGradient = np.gradient(filteredForce)
        stdV= np.std(filteredGradient)
        zGrad = (filteredGradient - np.mean(filteredGradient))/stdV
        # convert time to ms (just for plotting). Also just offset the time
        # to zero (again, just to make it easier to look at)
        toMs = 1e3
        minT = min(time)
        time *= toMs
        time -= min(time)
        plt.subplot(2,nWindows,i+1)
        plt.plot(time,force,'b-',ms=2,label="Window {:d}".format(i))
        pPlotUtil.lazyLabel("Time (ms)","Force (pN)","",fontsize=fontsize) 
        plt.plot(time,filteredForce,'r-',lw=2,
                 label="Filtered Data")
        plt.subplot(2,nWindows,nWindows+i+1)
        plt.plot(time,zGrad,color='r',label="Gradient, z scored")
        # normalize the events to this window
        norm = lambda x: (x-minT) * toMs
        plt.axvline(norm(labels[i].StartTime),label="Start of Event")
        plt.axvline(norm(labels[i].EndTime),label="End of Event")
        pPlotUtil.lazyLabel("Time (ms)","dForce (pN)","",frameon=True,
                            legendBgColor='w',fontsize=fontsize,
                            loc='lower center')
    return fig
