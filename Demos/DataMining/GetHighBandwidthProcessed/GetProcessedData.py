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
    fig = plt.figure()
    nWindows = len(sepWindow)
    # loop through *each* window and plokt
    timeConst = 4e-5
    mFiltering = FilterObj.Filter(timeConst = timeConst)
    for i,(time,sep,force) in enumerate(zip(timeWindow,sepWindow,forceWindow)):
        plt.subplot(nWindows,1,i+1)
        plt.plot(time,force,'b.',ms=2,label="Window {:d}".format(i))
        # plot the filtered version too!
        plt.plot(time,mFiltering.FilterDataY(time,force),color='r',
                 label="Filtered Data")
    plt.legend()
    plt.show()
if __name__ == "__main__":
    run()
