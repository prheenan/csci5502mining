# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append("../")

import DataMiningUtil.Caching.PreProcessCacher as Caching
from DataMining._2_PreProcess.PreProcessPlotting import PlotWindowsWithLabels


def run(limit=1):
    """
    Runs the main algorithm
    
    Args:

        limit: the number of files we limit ourselves to 
    """
    # get where the raw data and pre-processed data are
    dataBase = "./DataCache/"
    cacheSub = dataBase + "2_ProcessedData/"
    # get the list of pre-processed files
    files = Caching.GetListOfProcessedFiles(cacheSub)
    # Read all the pre-processed files
    for i,fileN in enumerate(files):
        if (i == limit):
            break
        mProc = Caching.ReadProcessedFileFromDirectory(cacheSub,fileN)
        # just for proof of concept, show the windows for this pre-processed
        PlotWindowsWithLabels(mProc,figsize=(16,8),fontsize=10)
        plt.show()
        

if __name__ == "__main__":
    run()
