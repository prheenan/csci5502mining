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
from DataMining._2_PreProcess.ProcessingMethods import ProcessByLabels
from DataMining._2_PreProcess.PreProcessedObject import ProcessedObj
from DataMining.DataMiningUtil.Filtering import FilterObj as FilterObj
from CypherReader.Util import CheckpointUtilities as pCheckUtil
from CypherReader.Util import PlotUtilities as pPlotUtil

def GetPreProcessExample():
    data = GetLabelledExample()
    processedObj = ProcessedObj(data,ProcessByLabels)
    return processedObj

def run():
    """
    <Description>

    Args:
        param1: This is the first param.
    
    Returns:
        This is a description of what is returned.
    """
    # we use my checkpointing, which just pickles objects.
    # you give it a file name and a function to call. If the file
    # doesnt exist, it calls the function, then saves out the result as the file
    whereToSave = "../../../DataMining/DataCache/2_ProcessedData/tmp.pkl"
    # if you make this true, forces it to run
    forceRun = True
    processedObj = pCheckUtil.getCheckpoint(whereToSave,GetPreProcessExample,
                                            forceRun)
    # loop through and plot just the regions around the events
    fig = plt.figure()
    # get every window
    timeWindow,sepWindow,forceWindow = \
        processedObj.HiResData.GetTimeSepForce()
    # plot the individual windows
    fig = pPlotUtil.figure(24,18)
    nWindows = len(sepWindow)
    # loop through *each* window and plokt
    timeConst = 8e-5
    labels = processedObj.Labels
    mFiltering = FilterObj.Filter(timeConst = timeConst)
    for i,(time,sep,force) in enumerate(zip(timeWindow,sepWindow,forceWindow)):
        # convert force to pN (just for plotting)
        force *= 1e12
        # also normalize it so the median before the event is zero (again,
        # just to make the plot pretty)
        deltaT = time[1]-time[0]
        startIdxInWindow = int((labels[i].StartTime-time[0])/(deltaT))
        force -= np.median(force[:startIdxInWindow])
        # this would be a great feature -- the derivative of the filtered force,
        # normalized to a standard normal curve
        filteredGradient = np.gradient(filteredForce)
        stdV= np.std(filteredGradient)
        zGrad = (filteredGradient - np.mean(filteredGradient))/stdV
        # plot the filtered version too!
        filteredForce=mFiltering.FilterDataY(time,force)
        # convert time to ms (just for plotting). Also just offset the time
        # to zero (again, just to make it easier to look at)
        toMs = 1e3
        minT = min(time)
        time *= toMs
        time -= min(time)
        plt.subplot(2,nWindows,i+1)
        plt.plot(time,force,'b-',ms=2,label="Window {:d}".format(i))
        pPlotUtil.lazyLabel("Time (ms)","Force (pN)","") 
        plt.plot(time,filteredForce,color='r',lw=5,
                 label="Filtered Data")
        plt.subplot(2,nWindows,nWindows+i+1)
        plt.plot(time,zGrad,color='r',label="Gradient, z scored")
        # normalize the events to this window
        norm = lambda x: (x-minT) * toMs
        plt.axvline(norm(labels[i].StartTime),label="Start of Event")
        plt.axvline(norm(labels[i].EndTime),label="End of Event")
        pPlotUtil.lazyLabel("Time (ms)","dForce (pN)","",frameon=True,
                            legendBgColor='w') 
    pPlotUtil.savefig(fig,"./ProcessOut.png")
if __name__ == "__main__":
    run()
