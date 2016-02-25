# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np

class DataObject:
    """
    This is the class which we will use to pass around data
    """
    def __init__(self,RawTimeSepForce=None,Labels=None,
                 ProcessedDataObject=None):
        """
        Constructor. Allows for constructing either a Raw or processed data 
        object
        
            Args:
                RawTimeSepForce : The Raw TimeSepForce Object, an instance like
                /CypherReader/ReaderModel/Generic/TimeSepForceObj
             
                ProcessedDataObject : A processed version of the data, for 
                speeding things up. Instance like <XXX TBD>
        
                Labels: A LabelObject, For determining where events happen
        """
        assert RawTimeSepForce is not None or ProcessedDataObject is not None
        # POST: at least some raw data or processed data
        self.RawData = RawTimeSepForce
        self.Labels = Labels
        self.ProcessedData = ProcessedDataObject
    def HasLabels(self):
        return self.Labels is not None
    def HasRaw(self):
        return self.RawData is not None
    def HasProcessed(self):
        return self.ProcessedData is not None
    @property
    def MetaData(self):
        """
        Returns (a reference to) the *low resolution* meta data. Note that this
        is usually the same as the high-resolution
        """
        assert self.HasRaw()
        return self.RawData.LowResData.meta
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
        assert self.HasRaw()
        return self.RawData
    @property
    def Processed(self):
        """
        Returns (a reference to) the processed data. Throws an error if there 
        isnt any (ie: if only raw)
        """
        assert self.HasProcessed()
        return self.ProcessedData

    
if __name__ == "__main__":
    run()
