# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

baseDir = "../../../"
sys.path.append(baseDir)
sys.path.append("../../")
sys.path.append("../")
sys.path.append("./")
from DataMiningDemoUtil.HighBandwidthUtil import GetLabelledExample
from DataMining.DataMiningUtil.Filtering import FilterObj as FilterObj
from DataMining._2_PreProcess import PreProcessPlotting as PrePlot
from CypherReader.Util import CheckpointUtilities as pCheckUtil
from DataMining._2_PreProcess.PreProcessInterface import PreProcessMain,\
    PreProccessOpt
from DataMining.DataMiningUtil.Caching.PreProcessCacher import \
    GetOrCreatedPreProcessed
 
def GetData():
    data = GetLabelledExample()
    return data

def GetLowResData():
    Data = GetData()
    Data.Data.HiResData =Data.Data.LowResData
    return Data

def CachedLowRes():
    return pCheckUtil.getCheckpoint("./lowCache.pkl",GetLowResData,False)

def run():
    """
    Shows how auto-processing works
    """
    mFile = "XNUG2TestData_3512133158_Image1334Concat.hdf"
    baseDirData = baseDir + "DataMining/DataCache/1_RawData/"
    outBase = "./out/"
    timeConst = 1e-3
    mFiltering = FilterObj.Filter(timeConst)
    opt = PreProccessOpt(mFiltering)
    mProc = GetOrCreatedPreProcessed(baseDirData,mFile,outBase,opt)
    PrePlot.PlotWindowsPreProcessed(mProc,outBase+"PreProcWindows.png")
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

    
if __name__ == "__main__":
    run()
