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

def GetHDF5Note(mFile):

def run():
    inFile = "/Users/patrickheenan/Documents/education/boulder_files/4_fall_2015/csci_5654_lin_prog/csci5654-finalProj/TestData/X151022-3528356043-Image0040Force.hdf"

if __name__ == "__main__":
    run()
