# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

import PyUtil.SqlUtil as SqlUtil
from PyUtil.SqlAlchemyBridge import sqlSerialize
from CypherReader.IgorAdapter.BinaryHDF5Io import GetDataAsTimeSepForceObject
from DataObject import DataObject

def GetListOfFiles(mModel="HighBandwidthNUG2",mSqlObj=None):
    """
    Get the list of files associated with this model

    Args:
       mModel: the name of the model to get
       mSqlObj: output of InitSqlGetSessionAndClasses
    Returns:
       the list of data files associated with the model
    """
    if (mSqlObj is None):
        mSqlObj = SqlUtil.InitSqlGetSessionAndClasses()
    mDataFiles = SqlUtil.getModelDataFilesInfo(mModel,serialize=True,
                                               mSqlObj=mSqlObj)
    return mDataFiles

def GetAllParamValues(mDataFiles,mSqlObj):
    """
    Given a list of data files, returns the parameter values associated with
    then

    Args:
        mDataFiles: output of GetListOfFiles
        mSqlObj: connection object to use, output of InitSqlGetSessionAndClasses
    Returns:
        list; element i is the in-order list of ParameterVaue objects 
        corresponding to file i
    """
    toRet = []
    for f in mDataFiles:
        vals,_ = SqlUtil.GetTraceParams(mSqlObj,f)
        serialVal = sqlSerialize(vals)
        toRet.append([val for val in serialVal])
    return toRet

def GetLabelsFromParamVals(paramList):
    """
    Converts a list of parameter sets to event indices

    Args:
        paramList: output of GetAllParamValues
    Returns: 
        list, element i are the events occuring for the i-th element of 
        paramList
    """
    # hand-coded indices, based on the models.
    firstStart = 5
    firstEnd = firstStart+1
    # function which, gives all the parametrs, gets the start and end indices
    labelsFromAllParams = lambda x : [(start.DataIndex,endV.DataIndex)
                                      for start,endV in zip(x[firstStart::2],
                                                            x[firstEnd::2])]
    # just transform all the parameters.
    return [labelsFromAllParams(p) for p in paramList]

def GetAllSourceFilesAndLabels(mModel="HighBandwidthNUG2"):
    """
    Gets all the source files and labels associated with thw given model

    Args:
        mModel: the model name to get
    Returns: 
        tuple of two <list of files, list of labels for each file>
    """
    mSqlObj = SqlUtil.InitSqlGetSessionAndClasses()
    mFiles = GetListOfFiles(mModel,mSqlObj=mSqlObj)
    vals = GetAllParamValues(mFiles,mSqlObj)
    labels = GetLabelsFromParamVals(vals)
    fileNames = [f.FileTimSepFor for f in mFiles]
    return fileNames,labels

def GetDataObjectFromFileAndLabels(SourceFilePath,Labels):
    """
    Given a (single) source file path and
    its labels, constructs a data object

    Args:
        SourceFilePath: the *path* to look for the data
        Labels: the labels associated with the data
    """
    timeSepForce = GetDataAsTimeSepForceObject(SourceFilePath)
    return DataObject(timeSepForce,Labels)
    
