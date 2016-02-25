from CypherReader.UnitTests.TestDataCorrections.ModelCorrections.\
    Main_ModelCorrections import GetOriginalAndCorrected,LoadHiResData
from CypherReader.ReaderModel.Generic.WaveDataGroup import WaveDataGroup
from CypherReader.ReaderModel.Generic.TimeSepForceObj import TimeSepForceObj
import CypherReader.IgorAdapter.BinaryHDF5Io as BinaryHDF5Io
from CypherReader.IgorAdapter.ProcessSingleWave import WaveObj

from DataMining._1_ReadInData.DataObject import DataObject


# hand-given labels for examples 
EventLabels = [ [9606314,9606338],[9714802,9714831],[9881233,9881346],
                [10100413,10100757],[10354853,10355079] ]

def SaveOutHighResData(filePath,\
        fileIn="../../../CypherReader/UnitTests/LocalData/NUG2TestData.pxp"):
    """
    Assuming the model corrections works, gets the Data to save out 

    Args:
        fileIn : where the pxp is coming from
        folderPath: where to save the data to (folder only)
    
    Returns:
        None
    """
    allData = LoadHiResData(fileIn)
    lowResTime,lowResSep,lowResForce,highResTime,sepExpected,\
        highCorrForce,highResForce = GetOriginalAndCorrected(allData)
    highResForceObj = WaveObj(DataY=highCorrForce,Note=highResForce.Note)
    highResSepObj = WaveObj(DataY=sepExpected,Note=highResForce.Note)
    # make a wave data group to save out
    toSave = WaveDataGroup({"sep":lowResSep,"force":lowResForce})
    toSave.HighBandwidthSetAssociatedWaves({"sep":highResSepObj,
                                            "force":highResForceObj})
    # save out the wave data as a group
    actualFilePath = \
            BinaryHDF5Io.SaveWaveGroupAsTimeSepForceHDF5(filePath,toSave)
    return actualFilePath

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

def SaveOutFiles(outPath):
    """
    Only run this if you are patrick. 

    Args:
        outPath: where  to save the file

    Returns:
        where we saved the file (full name)
    """
    return SaveOutHighResData(outPath)

def GetLabelledObject(fileOut):
    """
    Get the labelled object we want

    Args:
        filePath: where the '.hdf' file is.
    """
    mObj = GetHighResData(fileOut)
    # now make a Data Object ...
    return DataObject(RawTimeSepForce=mObj,Labels=EventLabels)
