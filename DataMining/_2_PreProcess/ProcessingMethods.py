# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

def ProcessByLabels(DataObject,extraPoints=None):
    """
    Given a data object, filtered by the labels. *not* supposed to be used 
    in production, just for debugging.

    Args:
        DataObject: see _1_ReadInData. Data object to use the labels from
        extraPoints: Extra points to look at, around each event. If none, 
        works at 10x the max label (5x in either direction)
    Return:
        Tuple of <lowIdx,HighIdx,"CheatingFilter">
    """
    Labels = DataObject.Labels
    if (extraPoints is None):
        diffs = [abs(end-start) for start,end in Labels]
        extraPoints = np.ceil(max(diffs)*5)
    maxPoints = DataObject.Data.HiResData.force.size
    HighIndex = [(max(0,start-extraPoints),min(maxPoints,end+extraPoints))
                 for start,end in Labels]
    # for the low index, simply convert the time basis, assuming everything
    # is offset
    deltaLo = DataObject.Data.LowResData.DeltaT()
    deltaHi = DataObject.Data.HiResData.DeltaT()
    convert = deltaHi/deltaLo
    conv = lambda x: int(convert*x)
    LowIndex = [ (conv(start),conv(end)) for start,end in HighIndex]
    return LowIndex,HighIndex,"CheatingFilter"

