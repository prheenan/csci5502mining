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
from UnitTestUtil import ArrClose


from numpy.random import rand

def run():
    """
    Tests the utility functions

    Args:
        None
    
    Returns:
        None
    """
    nTrials = 100
    n = 2000
    amp = 1000
    arr1 = rand(n,1) * amp
    tol = 1e-6
    for i in range(nTrials):
        assert not ArrClose(arr1,arr1[:-1]) , "Arrays unequal length"
        assert ArrClose(arr1,arr1) , "Array should be equal to itself"
        # add on some random noise, slightly too-small tolerance; should fail
        # with extremely high probability. uniform range, expect to see
        # E[x] = (N * range) within some range, so expect n/100 to be in
        # top 1% or above. As long as n >> 100, should work always
        assert not ArrClose(arr1,arr1 + rand(n,1)*tol*arr1,
                            tol=tol*0.99) ,\
            "Array within tolerance"
        # increase the tolerance so it is A-OK (should pass!)
        assert ArrClose(arr1,arr1 + rand(n,1)*tol*arr1,tol=tol) ,\
            "Array within tolerance"
        # odds of this not being bad are very low, given n >> 1
        bogus = rand(n,1)*3*tol
        assert (not ArrClose(arr1,bogus,tol=tol)) ,\
            "Array not within tolerance"
        assert (not ArrClose(arr1,arr1 + amp)) , "Array not within tolerance"
    # POST: random testing looks good. try some hand-picked arrays
    assert (not ArrClose([1],[2,3])), "Arrays not the same size"
    assert (not ArrClose([0],[1e-3],tol=tol)) , "arrays not within tolerance"
    assert (not ArrClose([1e-12],[1e-13],tol=tol)) ,\
        "arrays not within tolerance"    
    assert (ArrClose([1 + tol],[1],tol=tol)) , "arrays within tolerance"
    
if __name__ == "__main__":
    run()
