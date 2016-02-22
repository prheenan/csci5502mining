# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
# need to add the utilities class. Want 'home' to be platform independent
from os.path import expanduser
home = expanduser("~")
# get the utilties directory (assume it lives in ~/utilities/python)
# but simple to change
path= home +"/utilities/python"
import sys
sys.path.append(path)
# import the patrick-specific utilities
import GenUtilities  as pGenUtil
import PlotUtilities as pPlotUtil
import CheckpointUtilities as pCheckUtil

sys.path.append(path)
sys.path.append("../")
sys.path.append("../../")
# import the patrick-specific utilities
import GenUtilities  as pGenUtil
import PlotUtilities as pPlotUtil
import CheckpointUtilities as pCheckUtil
import IgorUtil 
import IgorAdapter.ProcessSingleWave as ProcessSingleWave
import IgorAdapter.PxpLoader as PxpLoader
import IgorAdapter.BinaryHDF5Io as BinaryHDF5Io


from UnitTests.TestingUtil.UnitTestUtil import ArrClose

def run():
    """
    Tests saving and loading of a pxp file is idempotent and preserves the 
    'normal' data and meta data

    Args:
        None
    Returns:
        None
    """            
    # dont raise anything on an error. we will handle not being able to connect
    # to jila
    demoName = "IgorPythonReader"
    localPath = "./LocalData/"
    inDir,outDir = IgorUtil.DemoJilaOrLocal(demoName,localPath)
    inFileMultiple = inDir + "ParseWaveTest.pxp"
    inFileSingle = inDir + "SingleWaveTest.pxp"
    # readin the 'multiple wave' file:
    mWaves = PxpLoader.LoadAllWavesFromPxp(inFileMultiple)
    n = len(mWaves)
    # Save them out as hdf5 files
    BinaryHDF5Io.MultiThreadedSave(mWaves,outDir)
    # Read them back; make sure we have the same thing. Note we assume the
    # initial read went OK (see the igor.py project)
    FileNames = [outDir + BinaryHDF5Io.GetFileSaveName(w) for w in mWaves]
    reRead = [BinaryHDF5Io.LoadHdfFileIntoWaveObj(f)
              for f in FileNames]
    # make sure we get the same thing reading back as what we loaded.
    # note that this test saving *and* loading.
    numMatches = sum(reRead[i] == mWaves[i] for i in range(n))
    assert numMatches == n , "File IO broken; waves saved or loaded improperly"
    # POST: saving and loading doesn't alter the original data
    # group them all
    mGrouping = PxpLoader.GroupWavesByEnding(mWaves)
    # loop through all the groupings and save them off
    ConcatData = []
    match = True
    for traceId,assocWaves in mGrouping.items():
        mArrs = assocWaves.values()
        tmpConcat = BinaryHDF5Io.ConcatenateWaves(mArrs)
        nEle = len(mArrs)
        for i in range(nEle):
            # skipe the first element (time) in concatenated
            concatDat = tmpConcat.DataY[:,i+1]
            originalDat = mArrs[i].DataY
            assert ArrClose(concatDat,originalDat) , \
                "Concatenated Data doesn't match."
        # check that the time is correct
        reference = mArrs[0]
        nY = reference.DataY.size
        time = np.linspace(0,nY,nY,endpoint=False)*reference.DeltaX()
        # first is time
        assert (nY == time.size) and ArrClose(tmpConcat.DataY[:,0],time) , \
            "Time doesn't match."
        # check all the times are consistent (transitive betwen first column
        # of dataY, time, and tmpConcat.GetXArray())
        timeConcat = tmpConcat.GetXArray()
        assert (nY == timeConcat.size) and (ArrClose(timeConcat,time)) ,\
            "Time doesn't match"
        ConcatData.append(tmpConcat)
    # save the concatenated files. Since saving works (first test)
    # and concatenation works (second test), woo!
    BinaryHDF5Io.MultiThreadedSave(ConcatData,outDir)

if __name__ == "__main__":
    run()
