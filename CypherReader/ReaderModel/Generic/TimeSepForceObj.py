# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt

from WaveDataGroup import WaveDataGroup
from DataObj import DataObj as DataObj


class Bunch:
    """
    see 
http://stackoverflow.com/questions/2597278/python-load-variables-in-a-dict-into-namespace

    Used to keep track of the meta information
    """
    def __init__(self, adict):
        self.__dict__.update(adict)

def DataObjByConcat(ConcatData,*args,**kwargs):
    """
    Initializes an data object from a concatenated wave object (e.g., 
    high resolution time,sep, and force)
    
    Args:
        ConcatData: concatenated WaveObj
    """
    Meta = Bunch(ConcatData.Note)
    time,sep,force = ConcatData.GetTimeSepForceAsCols()
    return DataObj(time,sep,force,Meta,*args,**kwargs)

class TimeSepForceObj:
    def __init__(self,mWaves=None):
        """
        Given a WaveDataGrop, gets an easier-to-use object, with low and 
        (possible) high resolution time sep and force
        
        Args:
            mWaves: WaveDataGroup. Should be able to get time,sep,and force 
            from it
        """
        if (mWaves is not None):
            self.LowResData = \
                DataObjByConcat(mWaves.CreateTimeSepForceWaveObject())
            # by default, assume we *dont* have high res data
            self.HiResData = None
            if (mWaves.HasHighBandwidth()):
                hiResConcat = mWaves.HighBandwidthCreateTimeSepForceWaveObject()
                self.HiResData = DataObjByConcat(hiResConcat)
    def CreatedFiltered(self,idxLowRes,idxHighRes):
        """
        Given indices for low and high resolution data, creates a new,
        Filtered data object (of type TimeSepForceObj)
        
        Args:
            idxLowRes: low resolution indices of interest. Should be a list;
            each element is a distinct 'window' we wan to look at

            idxHighRes: high resolution indices of interest. see idxLowRes
        """
        assert self.HiResData is not None
        # create an (empty) data object
        toRet = TimeSepForceObj()
        toRet.LowResData= self.LowResData.CreateDataSliced(idxLowRes)
        toRet.HiResData = self.HiResData.CreateDataSliced(idxHighRes)
        return toRet
    
