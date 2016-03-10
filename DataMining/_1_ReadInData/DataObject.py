# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np

class LabelObj:
    def __init__(self,listV,time):
        self.start = listV[0]
        self.end = listV[1]
        self.listV = listV
        self.StartTime = time[self.start]
        self.EndTime = time[self.end]
    def __getitem__(self,idx):
        """
        return the *index* (in 'raw' data) associated with 0/1
        Args:
            idx: if 0/1, returns index of start/end of event
        """
        return self.listV[idx]
    def __str__(self):
        return "[{:d}/{:d}]".format(self.start,self.end)
    def __repr__(self):
        return str(self)
    def __iter__(self):
        return iter(self.listV)
    @property
    def StartTime(self):
        """
        Returns the start *time* (in seconds) of the label
        """
        return self.StartTime
    @property
    def EndTime(self):
        """
        Returns the end *time* (in seconds) of the label
        """
        return self.EndTime

class DataObject(object):
    """
    This is the class which we will use to pass around data
    """
    def __init__(self,TimeSepForce=None,Labels=None,PreProcessed=False):
        """
        Constructor. Allows for constructing either a Raw or processed data 
        object
        
            Args:
                RawTimeSepForce : The Raw TimeSepForce Object, an instance like
                /CypherReader/ReaderModel/Generic/TimeSepForceObj
        
                Labels: if preprocessed is false, a list of <start,end> indices.
                Otherwise, a list of LabelObj (from an already made dataObj)
        
                PreProcessed: is pre-processed
        """
        assert TimeSepForce is not None
        # POST: at least some raw data or processed data
        self.Data = TimeSepForce
        if (PreProcessed):
            self.Lab = Labels
        else:
            self.Lab = [LabelObj(l,self.Data.HiResData.time) for l in Labels]
        self.PreProcessed = PreProcessed
    def HasLabels(self):
        return self.Lab is not None
    @property
    def MetaData(self):
        """
        Returns (a reference to) the *low resolution* meta data. Note that this
        is usually the same as the high-resolution
        """
        return self.Data.LowResData.meta
    @property
    def Labels(self):
        """
        Returns (a reference to) the Labelling object, as long as it exists
        """
        assert self.HasLabels()
        return self.Lab
    @property
    def Raw(self):
        """
        Returns (a reference to) the raw data. Throws an error if there isnt 
        any (ie: if only processed)
        """
        return self.Data
    
if __name__ == "__main__":
    run()
