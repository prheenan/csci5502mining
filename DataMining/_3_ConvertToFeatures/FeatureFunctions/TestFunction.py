# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys



def TestFunction(obj):
    """
    returnsa flattened window (dumb!)
    Args:
        obj : preprocessed object with the windows we want
    returns a flattened list of hi res data from the windows
    """
    return [data for window in obj.HiResData.HiResData\
             for data in window]

