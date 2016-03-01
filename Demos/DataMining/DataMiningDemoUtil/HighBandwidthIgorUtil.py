from CypherReader.UnitTests.TestDataCorrections.ModelCorrections.\
    Main_ModelCorrections import GetOriginalAndCorrected,LoadHiResData
    
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

def SaveOutFiles(outPath):
    """
    Only run this if you are patrick. 

    Args:
        outPath: where  to save the file

    Returns:
        where we saved the file (full name)
    """
    return SaveOutHighResData(outPath)
