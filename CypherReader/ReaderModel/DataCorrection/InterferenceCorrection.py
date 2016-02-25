# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("../../../")
import warnings
DEF_POLYFIT = 40

def GetCorrectedY(X,Y,PolynomalDegree=DEF_POLYFIT):
    """
    Given an uncorrect X and Y (e.g. time and DeflV), fits a polynomial 
    to them both and returns the corrected result and fitting coeffs.
    Fits the *entirety* of X and Y in that order. Eventually support other
    fits...

    Args:
        X: in-order x values (e.g. time) to fit
        Y: in-order (e.g. DeflV) to fit. 
        PolynomalDegree : The degree of the polynomial to fit
    
    
    Returns:
        tuple of <correctedDeflV,DeflV>
    """
    polyFit = np.polyfit(X,Y,PolynomalDegree)
    return polyFit

def GetCorrectedHiRes(XLow,YLow,LowSlice,XHigh,YHigh,HighSlice,
                      correction=None,strict=False,SafeCorrection=True):
    """
    Given an uncorrect X and Y (e.g. time and DeflV) in X and Y,
    and an uncorrect high-resolution wave, corrects the high resolution
    based on given indices (slices) to fit

    Args:
        XLow: in order low resolution x values (e.g. time)
        YLow: in order low resolution y values (e.g. force)
        LowSlice : slice for xlow/ylow to fit. Note that this will probably be 
        the approach curve for low res (ie: you will want to reverse it)

        XHigh: in order high resolution x values
        YHigh: in order high resolution y values

        HighSlice: slice for xhigh/yhigh to fit to 

        correction : type of correction to use.

        strict : If true, explodes if there is a rank-fitting problem.
        These are usually red herrings, but may indicate over-fitting...

        SafeCorrection : If true, if the LowSlice has range (in X units) of x',
        only fits the same range on your slice (this is safer, avoids 
        polynomials doing something crazy)
    Returns:
        tuple of <correctedDeflV,DeflV>
    """
    if (correction is not None):
        assert False , "No other corrections supported except default"
    with warnings.catch_warnings():
        # determine how to deal with the rank errors...
        if (not strict):
            warnings.simplefilter("ignore")
        else:
            warnings.filterwarnings('error')
        # get the low resolution fit
        deg = DEF_POLYFIT
        xLowSliceRel = XLow[LowSlice]
        xLowStart = xLowSliceRel[0]
        coeffsLow = GetCorrectedY(xLowSliceRel-xLowStart,YLow[LowSlice],
                                  PolynomalDegree=deg)
        # correct the low res
        YLowCorrect = np.copy(YLow)
        YLowCorrect[LowSlice] -= np.polyval(coeffsLow,
                                            xLowSliceRel-xLowStart)
        # determine if we need to correct the slice
        if (SafeCorrection):
            delta = XHigh[1]-XHigh[0]
            deltaSlice = max(xLowSliceRel)-min(xLowSliceRel)
            maxPoints = int(deltaSlice/delta)
            startHighIdx = HighSlice.start
            idxEnd = min(XHigh.size,startHighIdx+maxPoints)
            # XXX assumes indices are forward
            HighSlice = slice(startHighIdx,idxEnd,1)
        # correct the high res
        xHighSliceRel = XHigh[HighSlice]
        YHiResCorrect = np.copy(YHigh)
        # if the slices are reversed in direction,
        # need to multiply by -1; otherwise the poylnomial evaluation goes
        # the wrong direction and is very screwed up.
        factor = 1 if LowSlice.step*HighSlice.step > 0 else -1
        YHiResCorrect[HighSlice] -= np.polyval(coeffsLow,
                                    factor* (xHighSliceRel-xHighSliceRel[0]))
        return YLowCorrect,YHiResCorrect
    
    
    
