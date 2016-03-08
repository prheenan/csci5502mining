# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
from os.path import expanduser
home = expanduser("~")
from multiprocessing import Pool
CacheDefLoc=home + "/CypherReaderDataCache/"
NThreads = 5
from CypherReader.IgorAdapter import BinaryHDF5Io as BinaryHDF5Io
from CypherReader.IgorAdapter import ProcessSingleWave as ProcessSingleWave
from CypherReader.ReaderModel.Generic.WaveDataGroup import WaveDataGroup \
    as WaveDataGroup
from CypherReader.Util import GenUtilities as pGenUtil

class LargeDataManager:
    """
    This class is intended to manage large data sets by saving them to
    disk individually then re-loading, if a cache is desired
    """
    def __init__(self,CacheLoc=None):
        """
        Args:
            WaveData: The raw data to save to the cache. Formatted as XXX
            AddMethod : Method to call when data is available. If no cache,
            this is all the data immediately. If we use a cache, this is 
            after we save the data

            CacheLoc: Where to save the cache. If 'None', then we don't use a 
            cache, we just save the rawdata
        """
        self.CacheLoc = CacheLoc
        self.UseCache = CacheLoc is not None
        if (self.UseCache):
            pGenUtil.ensureDirExists(CacheLoc)
        # "extensions" is used to keep track of what extensions belong to which
        # data...
        self.WaveNameMap = dict()
        self.pool = Pool(NThreads) 
    def AddData(self,DataToAdd,AddMethod):
        """
        Add dictionary 'DataToAdd' (grouped by id) to the (if self.UseCache) 
        cached data. Anytime we add a wave, we call 'AddMethod'
        Args:
            DataToAdd: Data we want to add to the cache
            AddMethod: function taking in a wavename,called after saved
        """
        # Create <name:file> pairs to save
        self.MultiThreadedSaveAndNotify(DataToAdd,AddMethod)        
    def MultiThreadedSaveAndNotify(self,GroupedData,NotifyMethod):
        """
        Given a dict of WaveDataGroups 
        saves out the data, and notifyies thatthe wave has been saved
        Args:
            GroupedData: Dictionary, each key id an ID, each value is the
            grouped data for that wave

            NotifyMethod: Method to call on update
        """
        # get the file names
        waveNames = GroupedData.keys()
        fileData = [(waveN,GroupedData[waveN],NotifyMethod)
                    for i,(waveN) in enumerate(waveNames)]
        for f in fileData:
            self.SaveAndNotify(*f)
    def SaveAndNotify(self,WaveName,Data,NotifyMethod):
        """
        Notify by "Method" that WaveName has been saved. Also adds 
        <Key:Value> of <WaveName:Value> to WaveNameMap
        Args:
            WaveName: Name of the (id) of the wave. Eg. "0020DeflV"
            FileName: Where the file was saved, full path
            Data the data to save out 
            MethodNotifyMethod: Notification method
        """
        assert WaveName not in self
        self.UpdateData(WaveName,Data)
        NotifyMethod(WaveName)
    def UpdateData(self,WaveName,Data):
        """
        Unconditionally updates the data with name wavename
        Args:
            WaveName: (key) for the wave
            Data: WaveDict or wavegroup to use
        """
        if (self.UseCache):
            FilePath = self.DataToFile(WaveName,Data)
            self.WaveNameMap[WaveName] = FilePath
        else:
            self.WaveNameMap[WaveName] = Data
    def Update(WaveName,Data):
        """
        Updates an existing wave to new data. 
        Args:
            WaveName: Wave already in the cache
            Data: Data to update to 
        """
        assert WaveName in self
        self.UpdateData(WaveName,Data)
    def DataToFile(self,WaveName,Data):
        """
        Caches 'Data' to 'FileName', notifying it is saved
        Args:
            Data: see SaveAndNotify
            FileName: see SaveAndNotify
        Returns:
            File path (actual path to the file)
        """
        # get the extensions
        assert WaveName not in self
        # get the actual data to save out
        # False: dont want to throw an error if Hi res isn't complete
        return BinaryHDF5Io.SaveWaveGroupAsTimeSepForceHDF5(self.CacheLoc,
                                                            Data,
                                                            False)
        # save out the full data
    def DataFromFileCache(self,FilePath):
        """
        Gets the cached data from 'FileName'
        Args:
            FilePath:  Where the file is located
        Returns:
            Data, formatted like a wave data group. will *always* be time,sep,
            force
        """
        # dont want to throw an error if the high res doesnt have a separation
        return BinaryHDF5Io.ReadWaveIntoWaveGroup(FilePath,ErrorOnNoSep=False)
    def keys(self):
        """
        Returns the keys of the stored data
        """
        return self.WaveNameMap.keys()
    def __contains__(self,index):
        return index in self.WaveNameMap
    def __getitem__(self,index):
        """
        Returns the data (even if cached!) associated with index
        """
        ele = self.WaveNameMap[index]
        if (self.UseCache):
            # need to read in the data (ele is the file path)
            return self.DataFromFileCache(ele)
        else:
            # element itself has what we want
            return ele
