# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
import copy

from DataMining._1_ReadInData.DataObject import DataObject,LabelObj

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
    @property
    def WindowBounds(self):
        """
        Gets the window bounds, as indices, in the original data (ie:
        absolute start and end indices for the window
        """
        return self.HiResData.filterIdx
    def GetLabelIdxRelativeToWindows(self):
        """
        Returns: a 'flat' list of label objects, where the indices are relative
        to the windows. For example, if the actual labels are 1 and 12,
        and the window indices are [[1,2,3],[10,11,12]], the 'flat' indices 
        will be [0,5]. Useful for concatenating and predicting
        """
        lab = self.Labels
        idxByWindows = self.HiResData.GetWindowIdx()
        timeByWindows = self.HiResData.time
        # flattrn the window indices
        flatIdx = [int(i) for idxList in idxByWindows for i in idxList]
        flatTime = [t for timeList in timeByWindows for t in timeList]
        flatLabelIdx = []
        for l in lab:
            idxStart = flatIdx.index(l.start)
            idxEnd = flatIdx.index(l.end)
            newLab = copy.deepcopy(l)
            # only update the indices (time etc are the same)
            newLab.start = idxStart
            newLab.end = idxEnd
            flatLabelIdx.append(newLab)
        return flatLabelIdx
            
