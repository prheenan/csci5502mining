# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

import PyUtil.CheckpointUtilities as pCheckUtil

from DataMining._2_PreProcess.PreProcessInterface import PreProcessMain,\
    PreProccessOpt
import DataMining._2_PreProcess.PreProcessPlotting as PrePlot
import DataMining._1_ReadInData.DataReader as DataReader
import os
from DataMining._3_ConvertToFeatures.FeatureGenerator import FeatureMask


def GetPreProcessed(Data,PreProcessOpt,outBase,UseLowOnly=False):
    """
    Given a data set and options, gets the preprocseed set, an saves

    Args:
        Data: DataObject to use
        PreProcessOpt: the PreProcssInterface.PreprocessOptions to use
        OutBase:  base to save to
        UseLowOnly: if true, over-write the high-res data. see PreProcessMain
    """
    # process everything
    inf,mProc = PreProcessMain(PreProcessOpt,Data,UseLowOnly=UseLowOnly)
    # profile...
    n = inf.OriginalHi.force.size
    # how many points we want to plot at once, maximally
    maxPoints = 2e5
    # want to decimate to that n/deci = maxPoints is 1, or so. 
    decimate = max(1,int(n/maxPoints))
    PrePlot.PlotProfile(outBase,inf,mProc,decimate)
    return mProc

def PreProcessAndPlot(obj,BaseDirOut,Opt,UseLowOnly=False):
    """
    Args:
        Obj: the object to pre-process
        BaseDirOut: see: GetOrCreatedPreProcessed
        Opt: see: GetOrCreatedPreProcessed
        UseLowOnly: see GetPreProcessed
    """
    # get the (low res for now) objects to plot
    mProc = GetPreProcessed(obj,Opt,BaseDirOut,UseLowOnly=UseLowOnly)
    PrePlot.PlotWindowsPreProcessed(mProc,BaseDirOut+"PreProcWindows.png")
    return mProc

def ReadAndProcess(BaseDirIn,SourceName,BaseDirOut,Opt,Labels,
                   UseLowOnly=False):
    """
    Reads in a source file and Pre-Processes it.

    Args:
        see GetOrCreatedPreProcessed
    """
    obj = DataReader.GetDataObjectFromFileAndLabels(BaseDirIn + SourceName,
                                                    Labels)
    return PreProcessAndPlot(obj,BaseDirOut,Opt,UseLowOnly=UseLowOnly)

def GetOrCreatedPreProcessed(BaseDirIn,SourceName,BaseDirOut,Opt,Labels=None,
                             ForceUpdate=False,UseLowOnly=False):
    """
    Given a source name to read, reads from the pre-processed 
    cache, it if exists. Otherwise, creates the data object and pre-processes

    Args:
        BaseDirIn: Base directory of where to look for the SourceFiles
        BaseDirOut: Base directory of where to look for the saved files
        SourceName: the name of the source
        Opt: Pre-processing options
        Labels: the labels of the data object. 
        ForceUpdate: if true, forces an update of the pre-processed data 
        UseLowOnly: see GetPreProcessed
    
    Returns:
        the Pre Processed Object
    """
    outPath = BaseDirOut + SourceName + ".pkl"
    return pCheckUtil.getCheckpoint(outPath,ReadAndProcess,ForceUpdate,
                                    BaseDirIn,SourceName,BaseDirOut,Opt,
                                    Labels=Labels,UseLowOnly=UseLowOnly)


def GetListOfProcessedFiles(DataCacheDir):
    """
    Given the base location of all the cached folders, gets the list of all
    the available cached files

    Args:
        DataCacheDir: Lists of folders where the processed data lives
    """
    dirContents = [x for x in os.listdir(DataCacheDir)]
    dirs = [x for x in dirContents
            if os.path.isdir(os.path.join(DataCacheDir, x))]
    return dirs

def ReadProcessedFileFromDirectory(BaseDir,DirectoryPath):
    """
    Given a single element from the output of GetListOfCacheFilesDirectory,
    returns the pre-processed data

    Args:
        BaseDir: the base data directory
        DirectoryPath: single element of output from GetListOfProcessedFiles
    Returns:
        PreProcessedObject corresponding to the file
    """
    filePath = BaseDir + DirectoryPath + "/" + DirectoryPath + ".pkl"
    return pCheckUtil.loadFile(filePath,useNpy=False)

def GetProcessedObjectsAndLabels(cacheSub,limit):
    """
    Get the Processed objects and files, up to limit, in cachesub

    Args: See GetFeatureMask

    Returns:
        tuple of Processed objects / labels in the window
    """
    # get the list of pre-processed files
    files = GetListOfProcessedFiles(cacheSub)
    allObj =[]
    allLabels = []
    # Read all the pre-processed files
    offset = 0
    for i,fileN in enumerate(files):
        if (i == limit):
            break
        mProc = ReadProcessedFileFromDirectory(cacheSub,fileN)
        allObj.append(mProc)
        allLabels.append(mProc.GetLabelIdxRelativeToWindows())
    return allObj,allLabels


def GetFeatureMask(cacheSub,limit):
    """
    Gets the feature mask (essentially the feature matrix) for up to limit
    pre-processed objects in 'cachesub' 

    Args:
        cacheSub: where the cached, pre-processed objects are 
        limit: maximum number of objects to use to get the feature matrix.
    Returns:
        the FeatureMask object, constructed from all the examples
    """
    # construct the measure matrix
    allObj,allLabels = GetProcessedObjectsAndLabels(cacheSub,limit)
    matr = FeatureMask(allObj,allLabels)
    return matr

