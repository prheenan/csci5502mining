# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys


sys.path.append("../../../")
sys.path.append("../../")
sys.path.append("../")
sys.path.append("./")
from DataMiningDemoUtil.HighBandwidthUtil import GetLabelledExample
from DataMining.DataMiningUtil.Filtering import FilterObj as FilterObj
from CypherReader.Util import CheckpointUtilities as pCheckUtil
import PyUtil.PlotUtilities as pPlotUtil
from CypherReader.ReaderModel.DataCorrection.CorrectionMethods \
    import GetCorrectedAndOffsetHighRes
 
def GetLowResData():
    data = GetLabelledExample()
    return data.Data.LowResData

def CachedLowRes():
    return pCheckUtil.getCheckpoint("./lowCache.pkl",GetLowResData,False)
    
def FullRes():
    obj = GetLabelledExample()
    lowRes = obj.Data.LowResData
    hiRes = obj.Data.HiResData
    hiRes.meta.TriggerTime = lowRes.meta.TriggerTime
    return lowRes,hiRes 

def run():
    """
    Shows how auto-processing works
    """
    # loop through *each* window and plokt
    lowRes,hiRes = FullRes()
    PlotProcessing(lowRes,1,"./outLowRes.png")
    PlotProcessing(hiRes,100,"./outHiRes.png")
    # XXX TODO;
    # (1) make a correction method which is only data-based
    # (2) Break up plotting below, cache the time offsets, get corrected
    # (3) Make a plot showing the 'full stack':
    #    (a) how we idenify start and end times
    #    (b) how we correct the approach based on retract
    #    (c) final, including zoomed in
    # need to start moving this to the filtering object...
        
def PlotProcessing(lowRes,decimate,name):
    rawY = lowRes.force
    meta = lowRes.meta
    # the time constant is approximately the time it take for the entire
    # involts curve. should be able to make this dependent on meta data. For
    # now, hard-code
    time = lowRes.time
    timeConst = 1e-3
    mFiltering = FilterObj.Filter(timeConst)
    timeConst = mFiltering.InvolsTimeConst(lowRes)
    timeObj = mFiltering.GetApproachAndRetractTouchoffTimes(lowRes)
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
    idxAppr,idxRetr= FilterObj.GetApproxTouchoffRegions(lowRes)
    apprY = rawY[idxAppr]
    retrY = rawY[idxRetr]
    filteredGrad = np.abs(np.gradient(filteredY))
    filterYDeci = filteredY
    filterYGradDeci =  filteredGrad
    fig = pPlotUtil.figure(xSize=12,ySize=12)
    plt.subplot(2,2,1)
    plt.plot(timeDeci,rawYDeci,'r-',label="Raw Data")
    plt.plot(timeDeci,filterYDeci,'b-',label="Filtered Data")
    pPlotUtil.lazyLabel("Time (s)","Force (N)",
                        "Breaking up force versus time",legendBgColor='w',
                        frameon=True)
    plt.axvline(halfwayTime,label="Halfway point")
    plt.subplot(2,2,3)
    plt.plot(timeDeci,filterYGradDeci,'r,',label="Filtered Gradient")
    pPlotUtil.lazyLabel("Time (s)","Force (N)","",legendBgColor='w',
                        frameon=True)
    plt.axvline(halfwayTime)
    plt.subplot(2,2,2)
    # plot around the approach touchoff
    timeAppr = lowRes.time[idxAppr]
    plt.plot(timeAppr,apprY,'r-',label="Approach")
    filterApprY = mFiltering.FilterDataY(timeAppr,apprY)
    plt.plot(timeAppr,filterApprY,'b-',lw=2,label="Filtered Approach")
    plt.axvline(startMedTime,color='g',label="End of Approach")
    pPlotUtil.lazyLabel("Time (s)","Force (N)","",legendBgColor='w',
                        frameon=True)
    plt.subplot(2,2,4)
    timeRetr= lowRes.time[idxRetr]
    plt.axvline(endMedTime,color='g',label="Start of retract")
    plt.plot(timeRetr,retrY,'r-',label="Retract")
    filterApprY = mFiltering.FilterDataY(timeRetr,retrY)
    plt.plot(timeRetr,filterApprY,'b-',lw=2,label="Filtered Retract")
    pPlotUtil.lazyLabel("Time (s)","Force (N)","",legendBgColor='w',
                        frameon=True)
    pPlotUtil.savefig(fig,name)

    
if __name__ == "__main__":
    run()
