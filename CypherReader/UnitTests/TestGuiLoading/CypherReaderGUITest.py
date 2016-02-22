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
import ReaderController.Controller as Controller
from ReaderModel.HighBandwidthFoldUnfold import HighBandwidthModel as HighBw


def GuiLoaded(EventWindow):
    # assume we have some test data with multiple waves here
    FileToLoad = "./LocalData/NUG2TestData.pxp"
    EventWindow.LoadPxpAndAddToModel(FileToLoad)
    # POST: wavs loaded, select the 'first' one (keys unordered)
    Wave = EventWindow.Model.Waves.keys()[0]
    EventWindow.Model.SelectWaveByKey(Wave)
    # POST: all done... just checking the GUI loads, really.

    
def run():
    Controller.run(Model=HighBw.HighBandwidthModel(),
                   DebugCallbackOnLoad=GuiLoaded)

if __name__ == "__main__":
    run()
