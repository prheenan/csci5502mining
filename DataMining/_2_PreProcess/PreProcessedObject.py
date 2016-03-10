# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

from DataMining._1_ReadInData.DataObject import DataObject

class DistInfo:
    def __init__(self):
        pass
class CorrectionInfo:
    def __init__(self):
        pass

class ProcInfo:
    def __init__(self,ApproachDistInfo):
        """
        Args:
            ApproachDistInfo: Distribution (DistInfo) of approach curve

            CorrectionInfo: The correction applied to the data
        """
        self.ApproachDistInfo=ApproachDistInfo
        self.CorrectionInfo = CorrecitonInfo

class ProcessedObj(object):
    def __init__(self,obj,ProcessingMethod):
        """
        Initialized a processed data object from raw data, using the specified
        method. 
        
        Args:
            obj: _1_ReadInData.DataObject type
            ProcessingMethod: a method which takes in a DataObject,
            and returns a tuple of <lowResIdx,highResIdx,ProcInfo>
        """
        # get the indices
        lowResIdx,highResIdx,ProcInfo = ProcessingMethod(obj)
        # get the filtered version of the objects
        slicedTimeSepForce = obj.Data.CreatedFiltered(lowResIdx,
                                                      highResIdx)
        # Create our internal data object, using the same labels as before
        labs = obj.Labels
        self.ProcessedData = DataObject(TimeSepForce=slicedTimeSepForce,
                                        Labels=labs,PreProcessed=True)
    """
    Following properties just delegate appropriately.
    """
    @property
    def HiResData(self):
        return self.ProcessedData.Data.HiResData
    @property
    def LowResData(self):
        return self.ProcessedData.Data.LowResData
    @property
    def MetaData(self):
        return self.ProcessedData.MetaData()
    @property
    def Labels(self):
        return self.ProcessedData.Labels
