# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")
import ReaderController.Controller as Controller
from ReaderModel.HighBandwidthFoldUnfold import HighBandwidthModel as HighBw
import pyqtgraph as pg
from UnitTests.TestingUtil.GuiInteractions import AddIndicesToGuiAndCheck
from UnitTests.TestDataCorrections.HighbandwidthCorrectionGroundTruth.\
    HighbandwidthCorrectionGroundTruth import idxLowRes,idxHighRes,\
    idxRuptureEvents

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
    Model = EventWindow.Model
    Wave = Model.Waves.keys()[0]
    # select this wave...
    EventWindow.Model.SelectWaveByKey(Wave)
    # make an array of indices for where we clicked
    idx = list(idxLowRes) + list(idxHighRes) + list(idxRuptureEvents)
    AddIndicesToGuiAndCheck(Model,EventWindow,idx)
    # POST: all done
    exit(1)

def run():
    Controller.run(Model=HighBw.HighBandwidthModel(),
                   DebugCallbackOnLoad=GuiLoaded)

if __name__ == "__main__":
    run()
