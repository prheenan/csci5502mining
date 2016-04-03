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
from DataMining._2_PreProcess.PreProcessPlotting import PlotWindowsWithLabels
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
    fig = PlotWindowsWithLabels(processedObj)
    pPlotUtil.savefig(fig,"./ProcessOut.png")
if __name__ == "__main__":
    run()
