# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
# need to add the utilities class. Want 'home' to be platform independent

from WaveDataGroup import WaveDataGroup

class Bunch:
    """
    see 
http://stackoverflow.com/questions/2597278/python-load-variables-in-a-dict-into-namespace

    Used to keep track of the meta information
    """
    def __init__(self, adict):
        self.__dict__.update(adict)
    

class DataObj:
    def __init__(self,time,sep,force,metaInfo,offsetIdx=0):
        """
        Initializes an object with the given time,sep, and force. Data may
        be offset from an 'absolute' index. Default offset it zero
        
        Args:
            time,sep,force: the time,separation, and force in SI units
            metaInfo: the meta information as a dictionary 
            offsetIdx: the offset, if this data is a slice from a larger set 
        """
        self.time = time
        self.sep = sep
        self.force = force
        self.meta = Bunch(metaInfo)
        self.offsetIdx = offsetIdx

def DataObjByConcat(ConcatData,*args,**kwargs):
    """
    Initializes an data object from a concatenated wave object (e.g., 
    high resolution time,sep, and force)
    
    Args:
        ConcatData: concatenated WaveObj
    """
    Meta = ConcatData.Note
    time,sep,force = ConcatData.GetTimeSepForceAsCols()
    return DataObj(time,sep,force,Meta,*args,**kwargs)

class TimeSepForceObj:
    def __init__(self,mWaves,offsetIdx=0):
        """
        Given a WaveDataGrop, gets an easier-to-use object, with low and 
        (possible) high resolution time sep and force
        
        Args:
            mWaves: WaveDataGroup. Should be able to get time,sep,and force 
            from it
            offsetIdx: if the data is all offset from some index
        """
        self.LowResData = DataObjByConcat(mWaves.CreateTimeSepForceWaveObject(),
                                          offsetIdx=offsetIdx)
        # by default, assume we *dont* have high res data
        self.HiResData = None
        if (mWaves.HasHighBandwidth()):
            hiResConcat = mWaves.HighBandwidthCreateTimeSepForceWaveObject()
            self.HiResData = DataObjByConcat(hiResConcat)
        # POST: all done... 
        
