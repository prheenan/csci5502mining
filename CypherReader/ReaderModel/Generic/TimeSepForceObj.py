# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt

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
    def __init__(self,time,sep,force,metaInfo,filterIdx=None):
        """
        Initializes an object with the given time,sep, and force. Data may
        be offset from an 'absolute' index. Default offset it zero
        
        Args:
            time,sep,force: the time,separation, and force in SI units
            metaInfo: the meta information as a dictionary 
            filterIdx: indices associated with a slice, if any.
        """
        self.time = time
        self.sep = sep
        self.force = force
        self.meta = metaInfo
        self.filterIdx = filterIdx
    def GetTimeSepForce(self):
        """
        Returns time,sep,force as a tuple
        """
        return self.time,self.sep,self.force
    def DeltaT(self):
        return self.time[1]-self.time[0]
    def HasDataWindows(self):
        return self.filterIdx is not None
    def CreateDataSliced(self,idx):
        """
        Using the data here and provided indices, 

        Args:
            idx: list of <start,end> indices for which we want to slice the 
            data, [start,end) (does *not* include end)
        """
        copyWindowData = lambda x: [x[start:end][:] for start,end in idx]
        toRet = DataObj(copyWindowData(self.time),
                        copyWindowData(self.sep),
                        copyWindowData(self.force),
                        self.meta,
                        idx)
        return toRet
    def GetWindowIdx(self):
        """
        Gets the indices of the windows as a list of arrays. For example, if
        There are two windows, one like [1,2,3], and one like [4,5,6], returns
        [[1,2,3],[4,5,6]]. Corresponds exactly to indices of data, if self
        was constructed with CreateDataSliced
        """
        assert self.filterIdx is not None
        return [np.arange(start,end) for start,end in self.filterIdx]

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
    
