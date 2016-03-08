# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")
import ReaderModel.LargeDataManagement.LargeDataManager as \
    LargeDataManager
import IgorAdapter.PxpLoader as PxpLoader
from ReaderModel.Generic.WaveDataGroup import WaveDataGroup 

class foo:
    def method(self,x):
        # can uncommen to make sure procesing is working
        #print("Foo.method: {:s}".format(x))
        pass

def run():
    """
    Tests that the larger data manager is doing what it should 
    """
    # first, just check that the data is doing what it should in isolation,
    # regardless of the model
    FileToLoad = "./LocalData/ParseWaveTest.pxp"
    WaveDict = PxpLoader.LoadPxp(FileToLoad)
    mgr = LargeDataManager.LargeDataManager()
    f = foo()
    method = lambda x: f.method(x)
    mgr.AddData(WaveDict,method)
    for idV,WaveGroup in WaveDict.items():
        assert idV in mgr , "Id not added to {:s}".format(mgr.keys())
        # get the data as a wavedatagroup (time,sep,force)
        data = mgr[idV]
        # convert to time sep and force.
        expectedData = WaveDataGroup(WaveGroup)
        # check that the data and expected data have the same time,sep,force
        expectedData.EqualityTimeSepForce(data)

        
if __name__ == "__main__":
    run()
