# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np

class LabelObj:
    def __init__(self,listV):
        self.start = listV[0]
        self.end = listV[1]
        self.listV = listV
    def __getitem__(self,idx):
        return self.listV[idx]
    def __str__(self):
        return "[{:d}/{:d}]".format(self.start,self.end)
    def __repr__(self):
        return str(self)
    def __iter__(self):
        return iter(self.listV)


class DataObject:
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
        
                Labels: A LabelObject, For determining where events happen
        
                PreProcessed: is pre-processed
        """
        assert TimeSepForce is not None
        # POST: at least some raw data or processed data
        self.Data = TimeSepForce
        if Labels is not None:
            self.Lab = [LabelObj(l) for l in Labels]
        else:
            print("labels not existing... XXX debugging...")
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
