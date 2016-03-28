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
from DataMining._2_PreProcess import PreProcessPlotting as PrePlot
from CypherReader.Util import CheckpointUtilities as pCheckUtil
from DataMining._2_PreProcess.PreProcessInterface import PreProcessMain
 
def GetLowResData():
    data = GetLabelledExample()
    # get just the low res data
    data.Data.HiResData = data.Data.LowResData
    return data

def CachedLowRes():
    return pCheckUtil.getCheckpoint("./lowCache.pkl",GetLowResData,False)
    
def run():
    """
    Shows how auto-processing works
    """
    timeConst = 1e-2
    decimate = 1
    mFiltering = FilterObj.Filter(timeConst)
    # get the (low res for now) objects to plot
    obj = CachedLowRes()
    # process everything
    inf,mProc = PreProcessMain(mFiltering,obj,True)
    # show how to get some stats
    # 'summaries' is has all three distributions (raw, corrected,
    # corrected and filtered)

    # each distribution has data on the approach, dwell, retract 
    Summaries = mProc.Meta.Summary
    # Each Distribution has distributions on gradients *and* on the raw Y
    print("The raw force distribution approach mean is {:.3g}".\
          format(Summaries.RawDist.approach.RawY.mean))
    print("The corrected force gradient retract distribution std is {:.3g}".\
          format(Summaries.CorrectedDist.retract.GradY.std))
    print("The filtered force distribution dwell min is {:.3g}".\
          format(Summaries.CorrectedAndFilteredDist.dwell.RawY.distMin))
    # profile...
    PrePlot.PlotProfile("./",inf,mProc,decimate)
    
if __name__ == "__main__":
    run()
