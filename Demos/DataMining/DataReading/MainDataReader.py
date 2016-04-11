# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

base = "../../../"
sys.path.append(base)
import DataMining._1_ReadInData.DataReader as DataReader
from DataMining._2_PreProcess.PreProcessInterface import PreProccessOpt
from DataMining.DataMiningUtil.Caching.PreProcessCacher import \
    GetOrCreatedPreProcessed
import DataMining.DataMiningUtil.Filtering.FilterObj as FilterObj
import PyUtil.GenUtilities as pGenUtil
import PyUtil.IgorUtil as IgorUtil
import matplotlib
matplotlib.rcParams['agg.path.chunksize'] = int(1e5)

def run():
    source,labels = DataReader.GetAllSourceFilesAndLabels()
    DataDir = base + "DataMining/DataCache/1_RawData/"
    # get the pre-processing options object
    timeConst = 1e-3
    mFiltering = FilterObj.Filter(timeConst)
    opt = PreProccessOpt(mFiltering)
    limit = None
    start=0
    for i,(sourceFile,label) in enumerate(zip(source[start:],labels[start:])):
        print(label)
        if (i == limit):
            break
        fullPath = DataDir + sourceFile
        outPath = "./out/" + sourceFile + "/"
        # make sure we have a separate directory for each source.
        mDir = pGenUtil.ensureDirExists(outPath)
        proc = GetOrCreatedPreProcessed(DataDir,sourceFile,mDir,opt,label,
                                        ForceUpdate=False,UseLowOnly=False)
        

if __name__ == "__main__":
    run()
