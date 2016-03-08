# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np

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
        self.Labels = Labels
        self.PreProcessed = PreProcessed
    def HasLabels(self):
        return self.Labels is not None
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
        return self.Labels
    @property
    def Raw(self):
        """
        Returns (a reference to) the raw data. Throws an error if there isnt 
        any (ie: if only processed)
        """
        return self.Data
    
if __name__ == "__main__":
    run()
