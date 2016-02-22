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

defRelTol = 1e-6

def AssertIntegral(v1,tol=defRelTol):
    """
    Asserts a number is integral, to some relative tolerance

    Args:
        v1: first scalar-like to check
        tol: relative error tolerance to check

    Returns:
        None
    """
    floatV = float(v1)
    intV = int(v1)
    assert ArrClose(floatV,intV,tol=tol) , \
        "Expected {:.6g} to be integral".format(floatV)

def ArrClose(v1,v2, tol=defRelTol):
    """
    Tests that two arrys (or numbers) are equal within a relative error of tol.
    The intention of this is to compare both arrays, allowing for dimensionful 
    offsets (e.g., a force array with a range between 10 and 150 pN, so 10e-12)

    Args:
        v1: first array-like to check
        v2: second array-like to check
        tol: relative error tolerance to check

    Returns:
        None
    """
    # numpy.isclose() demands lengths are the same.
    isScalar = False
    try:
        # are we a numpy array?
        if (v1.shape != v2.shape1):
            return False
    except AttributeError:
        # not a numpy-like array... hw about just an array?
        try:
            if (len(v1) != len(v2)):
                return False
        except TypeError:
            # just single element scalars. Numpy can deal with these
            # cast to float just to be sure.
            v1 = float(v1)
            v2 = float(v2)
            isScalar = True
    # POST: lengths match. Use equal_nan to account for dividing by zero.
    mRet = np.isclose(v1,v2,atol=0,equal_nan=True,rtol=tol)
    if (isScalar):
        return mRet
    else:
        # every elemenet should be close
        return mRet.all()
