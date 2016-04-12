
from CypherReader.ReaderModel.Generic.WaveDataGroup import WaveDataGroup
from CypherReader.ReaderModel.Generic.TimeSepForceObj import TimeSepForceObj
import CypherReader.IgorAdapter.BinaryHDF5Io as BinaryHDF5Io
from CypherReader.IgorAdapter.ProcessSingleWave import WaveObj

from DataMining._1_ReadInData.DataObject import DataObject
import PyUtil.CheckpointUtilities as pCheckUtil

import DataMining.DataMiningUtil.Caching.PreProcessCacher as Caching


# hand-given labels for examples 
EventLabels = [ [9606314,9606338],[9714802,9714831],[9881233,9881346],
                [10100413,10100757],[10354853,10355079] ]

EXAMPLE_FILE = "DataMining/DataCache/1_RawData/" +\
               "XNUG2TestData_3512133158_Image1334DeflV.hdf"

def GetLabelledExample(base ="../../../",fileN=EXAMPLE_FILE ):
    outPath = base + fileN
    data = GetLabelledObject(outPath)
    return data

def GetHighResData(filePath):
    """
    Given a file path, reads the data into a TimeSepForceObj, for easy reading.

    Args:
        filePath: where to get the data from 
    
    Returns:
        A timeSepForceObj, presummabyly with high resolution data
    """
    dataGroup = BinaryHDF5Io.ReadWaveIntoWaveGroup(filePath)
    return TimeSepForceObj(dataGroup)

def GetLabelledObject(fileOut):
    """
    Get the labelled object we want

    Args:
        filePath: where the '.hdf' file is.
    """
    mObj = GetHighResData(fileOut)
    # now make a Data Object ...
    return DataObject(TimeSepForce=mObj,Labels=EventLabels)


def GetData(base,**kwargs):
    data = GetLabelledExample(base,**kwargs)
    return data

def GetLowResData(base,**kwargs):
    Data = GetData(base,**kwargs)
    Data.Data.HiResData =Data.Data.LowResData
    return Data

def CachedLowRes(base="../../../",**kwargs):
    return pCheckUtil.getCheckpoint("./lowCache.pkl",GetLowResData,False,base,
                                    **kwargs)

