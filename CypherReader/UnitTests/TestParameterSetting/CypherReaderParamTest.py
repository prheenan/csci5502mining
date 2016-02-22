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
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")
# import the patrick-specific utilities
import GenUtilities  as pGenUtil
import PlotUtilities as pPlotUtil
import CheckpointUtilities as pCheckUtil
import PyUtil.SqlUtil as SqlUtil
import ReaderController.Controller as Controller
from ReaderModel.HighBandwidthFoldUnfold import HighBandwidthModel as HighBw
import pyqtgraph as pg
import UnitTests.TestSqlPushing.SqlTestUtil as SqlTestUtil
from UnitTests.TestDataCorrections.HighbandwidthCorrectionGroundTruth.\
    HighbandwidthCorrectionGroundTruth import idxLowRes,idxHighRes

def GuiLoaded(EventWindow):
    """
    Runs the functions for logic behind GUI / parameter loading / pushing. 

    Args:
        EventWindow: The EventWindow loaded. Gives access to model/view
    
    Returns:
        Nothing
    """

    # assume we have some test data with multiple waves here
    FileToLoad = "./LocalData/NUG2TestData.pxp"
    EventWindow.LoadPxpAndAddToModel(FileToLoad)
    # POST: wavs loaded, select the 'first' one (keys unordered)
    waveDict = EventWindow.Model.Waves
    Wave = waveDict.keys()[0]
    # select this wave...
    EventWindow.Model.SelectWaveByKey(Wave)
    # Add a bunch of parameters at dummy indices, based on the data
    waveDataGroup = waveDict[Wave]
    associatedWaves = waveDataGroup.values()
    # get the actual y data for a wave
    mWave = associatedWaves[0]
    dataY = mWave.DataY
    dataX = mWave.GetXArray()
    n = dataY.size
    # get all of the parameters
    nParams = EventWindow.Model.NParams()
    end = n/3
    start = 1
    # make an array of indices for where we clicked (reverse just so it
    # reads properly / not so crazy)
    idx = idxLowRes + idxHighRes
    # show that the used clicked at all the indices
    map(EventWindow.UserClickedAtIndex,idx)
    # check that we actually pushed it...
    idNamespace = waveDataGroup.SqlIds
    ParamMeta = EventWindow.Model.ParamMeta
    ParamVals = EventWindow.Model.CurrentParams
    SqlObj = SqlUtil.InitSqlGetSessionAndClasses()
    SqlTestUtil.AssertCorrectlyPushed(idNamespace,waveDataGroup,ParamVals,
                                      ParamMeta,SqlObj)
    # POST: all done
    #exit(1)

def run():
    Controller.run(Model=HighBw.HighBandwidthModel(),
                   DebugCallbackOnLoad=GuiLoaded)

if __name__ == "__main__":
    run()
