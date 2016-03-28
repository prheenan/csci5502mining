# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

sys.path.append("../")
sys.path.append("../../")
import IgorAdapter.ProcessSingleWave as ProcessSingleWave
import IgorAdapter.PxpLoader as PxpLoader
import IgorAdapter.BinaryHDF5Io as BinaryHDF5Io
import CypherReader.Util.IgorUtil as IgorUtil
import CypherReader.Util.PlotUtilities as pPlotUtil
import PyUtil.CypherUtil as CypherUtil
import PyUtil.HDF5Util as HDF5Util
import copy
from ReaderModel.Generic import Model



from UnitTests.TestingUtil.UnitTestUtil import ArrClose

def GetDeflVObj(DeflObj):
    """
    Gets the 'DeflV' from the defl 

    Args:
        deflObj : Wave Data Object associated with deflObj. Assumes invols are 
        set 

    Returns:
        deflection in volts
    """
    deflVObj = copy.deepcopy(DeflObj)
    deflVObj.DataY = DeflObj.DataY * 1/DeflObj.Invols()
    return deflVObj

def CheckSingleConversions(sepObj,forceObj,zsnsrObj,deflObj):
    """
    Tests certain common single conversion works 

    Args:
        sepObj : Wave Data Object associated with separation
        force : Wave Data Object associated with force
        zsnsrObj : Wave Data Object associated with zsnsr    
        deflObj : Wave Data Object associated with deflObj    

    Returns:
        None
    """
    deflVObj = GetDeflVObj(deflObj)
    ZsnsrConv,DeflVConv = CypherUtil.ConvertSepForceToZsnsrDeflV(sepObj,
                                                                 forceObj)
    # check the converted ones match the cypher-converted ones
    assert ArrClose(ZsnsrConv,zsnsrObj.DataY)
    assert ArrClose(DeflVConv,deflVObj.DataY)
    # check "reverse": {ZSnsr,DeflV} to {Sep,Force}
    # note we have converted deflObj to deflV, above
    SepConv,ForceConv = CypherUtil.ConvertZsnsrDeflVToSepForce(zsnsrObj,
                                                               deflVObj)
    # check the converted ones match the cypher-converted ones
    sepDat = sepObj.DataY
    forceDat = forceObj.DataY
    assert ArrClose(SepConv,sepDat)
    assert ArrClose(ForceConv,forceDat)

def CheckSepForceConversions(sepObj,forceObj,zsnsrObj,deflObj):
    """
    Tests conversions to separation and force

    Args:
        See CheckSingleConversions

    Returns:
        None
    """
    deflVObj = GetDeflVObj(deflObj)
    # test a variety of dictionaries, ensure we can convert properly
    # for many different types 
    mDicts = [
            # Separation and force (ie: idempotent)
            {'sep':sepObj,'force':forceObj},
            # A vareity of 'normal' combinations
            {'sep':sepObj,'defl':deflObj},
            {'zsnsr':zsnsrObj,'deflV':deflVObj},
            {'sep':sepObj,'deflV':deflVObj},
            {'zsnsr':zsnsrObj,'defl':deflObj},
            # the entire kitchen sink
            {'zsnsr':zsnsrObj,'defl':deflObj,'sep':sepObj,'force':forceObj,
             'deflV':deflVObj},
            # capitalize stuff weird
            {'zSNsr':zsnsrObj,'deFL':deflObj,'sEP':sepObj,'foRCe':forceObj,
             'dEFlV':deflVObj}
        ]
    sepDat = sepObj.DataY
    forceDat = forceObj.DataY
    for d in mDicts:
        Sep,Force = CypherUtil.GetSepForce(d)
        ErrorMsg = "Combination of {:s} didn't work!".format(d.keys())
        assert ArrClose(Sep,sepDat) , ErrorMsg
        assert ArrClose(Force,forceDat) , ErrorMsg
    # POST: all cobinations work. Check conversion of just force
    forceDicts = [{"deflv":deflVObj},
                  {"defl":deflObj},
                  {"force":forceObj}]
    for d in mDicts:
        Force = CypherUtil.GetForce(d)
        ErrorMsg = "Combination of {:s} didn't work!".format(d.keys())
        assert ArrClose(Force,Force) , ErrorMsg

def ChekcWaveGroupMatches(mGroup,GroupNote,NoteExpected,Time,Sep,Force):
    """
    Tests that given wave group has the give note and data

    Args:
        mGroup:  dictionary of <name>:<WaveObj>, with Sep and Force
        GroupNote: note of the group
        NoteExpected; Expected note
        Time: Time we should have (array)
        Sep: Separation we should have (array)
        Force: Force we should have (array)

    Returns:
        None
    """
    # make sure the force and sep are as we expect
    forceRead = mGroup['force']
    sepRead = mGroup['sep']
    assert ArrClose(Sep,sepRead.DataY) , "Separation Incorrect"
    assert ArrClose(Force,forceRead.DataY) , "Separation Incorrect"
    # construct the time
    timeRead = forceRead.GetXArray()
    assert ArrClose(Time,timeRead) , "Time Incorrect"
    # POST: data saved OK. how about the notes?
    assert (ProcessSingleWave.NotesEqual(GroupNote,NoteExpected)) ,\
        "Notes not saved"
    
def CheckWaveGroupSave(sepObj,forceObj,zsnsrObj,deflObj,outDir):
    """
    Tests conversions and operations related to saving a WaveGroup

    Args:
        See CheckSingleConversions

    Returns:
        None
    """
    deflVObj = GetDeflVObj(deflObj)
    assocWaves = {'zSNsr':zsnsrObj,'deFL':deflObj,'sEP':sepObj,
                  'foRCe':forceObj,'dEFlV':deflVObj}
    # note we initialize with a bunk source file. we just want to check
    # concatenation works
    WaveGroup = Model.WaveDataGroup(AssociatedWaves=assocWaves)
    Group = WaveGroup.CreateTimeSepForceWaveObject()
    Time = forceObj.GetXArray()
    Sep = sepObj.DataY
    Force = forceObj.DataY
    assert ArrClose(Time,Group.DataY[:,0]),\
        "Concatenated Separation Incorrect"
    assert ArrClose(Sep,Group.DataY[:,1]) , \
        "Concatenated Separation Incorrect"
    assert ArrClose(Force,Group.DataY[:,2]) ,\
        "Concatenated Force Incorrect"
    # POST: creating the time-sep object works. now we need to test
    # saving the entire group as a group.
    mFile = BinaryHDF5Io.SaveWaveGroupAsTimeSepForceHDF5(outDir,WaveGroup)
    # read back in the file
    mGroup = BinaryHDF5Io.ReadWaveIntoWaveGroup(mFile)
    ExpectNote = Group.Note
    ActualNote = mGroup.Note()
    ChekcWaveGroupMatches(mGroup,ActualNote,ExpectNote,Time,Sep,Force)
    # POST: note is OK too. 
    # add in 'high bandwidth' (interpolated) data
    # and make sure the reading goes fine for that as well.
    # nInterp is factor to interpolate by
    nInterp =2
    deltaLow = Time[1]-Time[0]
    timeHighBW = np.arange(0,nInterp*Time.size,1) *deltaLow/nInterp
    sepHighBW = np.interp(timeHighBW,Time,Sep)
    forceHighBW = np.interp(timeHighBW,Time,Force)
    # set the high bandwidth associated waves
    Note = mGroup.Note()
    AssocHighBW = {
        'sep':ProcessSingleWave.WaveObj(DataY=sepHighBW,Note=Note),
        'force':ProcessSingleWave.WaveObj(DataY=forceHighBW,Note=Note) }
    # make the wave think it is high res so the times work out
    # (note a real high-res wave will already know its deltaX)
    AssocHighBW['force'].Note["NumPtsPerSec"] *= nInterp
    AssocHighBW['sep'].Note["NumPtsPerSec"] *= nInterp
    ExpectedHiResNote = AssocHighBW['force'].Note
    mGroup.HighBandwidthSetAssociatedWaves(AssocHighBW)
    assert mGroup.HasHighBandwidth() , "Missing High Bandwith"
    # get the force...
    forceHighBwTest = mGroup.HighBandwidthGetForce()
    assert ArrClose(forceHighBwTest,forceHighBW) , "High force wrong"
    # POST: force looks OK. Time to save the thing and check it works!
    mFileHighBw = BinaryHDF5Io.SaveWaveGroupAsTimeSepForceHDF5(outDir,mGroup)
    # read the file back in ...
    mGroupHighBW = BinaryHDF5Io.ReadWaveIntoWaveGroup(mFile)
    # Mk, check that the low-res stuff is the same
    ChekcWaveGroupMatches(mGroup,mGroup.Note(),ExpectNote,Time,Sep,Force)
    # now check the high-res stuff
    GroupNote = mGroup.HighBandwidthWaves['force'].Note
    ChekcWaveGroupMatches(mGroup.HighBandwidthWaves,GroupNote,ExpectedHiResNote,
                          timeHighBW,sepHighBW,forceHighBW)

def run():
    """
    Tests that converting between data types 
    (e.g. force<-->deflv or sep<-->zsns)  and concatenating them works properly

    Dependent on PythonReader.py test to make sure the files can
    be loaded and saved properly

    Args:
        AssociatedWaveData: a WaveDataGroup object (see Model)

    Returns:
        None
    """
    
    inDir,outDir = IgorUtil.DemoJilaOrLocal("IgorPythonConvert",
                                            localPath="./LocalData")
    inFileMultiple = inDir + "ParseWaveTest.pxp"
    # readin the 'multiple wave' file:
    mWaves = PxpLoader.LoadAllWavesFromPxp(inFileMultiple)
    # group them all
    mGrouping = PxpLoader.GroupWavesByEnding(mWaves)
    recquiredExt = ["sep","zsnsr","force","defl"]
    for waveid,associatedWaves in mGrouping.items():
        mBreak = False
        for ext in recquiredExt:
            if (ext not in associatedWaves):
                mBreak = True
        assert not mBreak , "Demo data flawed; not all needed extensions found"
        # POST: found all extensions
        # get all the 'ground truth' waves. Convert back and forth,
        # make sure everything matches..
        sepObj = associatedWaves["sep"]
        forceObj = associatedWaves["force"]
        zsnsrObj = associatedWaves["zsnsr"]
        deflObj = associatedWaves["defl"]
        # convert deflObj to deflV by mutliplying by 1/invols..
        CheckSingleConversions(sepObj,forceObj,zsnsrObj,deflObj)
        CheckSepForceConversions(sepObj,forceObj,zsnsrObj,deflObj)
        CheckWaveGroupSave(sepObj,forceObj,zsnsrObj,deflObj,outDir)
        
if __name__ == "__main__":
    # this function tests the Cypher Conversion routines, specifically
    # converting zsnsr to sep (and back) and Defl to Force (and back)
    run()
