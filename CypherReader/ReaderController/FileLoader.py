# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt

import sys
import pyqtgraph as pg
import IgorAdapter.PxpLoader

def InteractivePxpLoad():
    """
    Function to handle a file load button click. loads waves in a pxp file

    Args:
        None
    Returns:
        None
    """
    fn = str(pg.QtGui.QFileDialog.getOpenFileName(
        caption="Load an Igor File",
        directory="",
        filter="Packed Experiment Files (*.pxp)"))
    if fn == '':
        return
    mWaves = PxpLoader.LoadPxp(fn)
    
if __name__ == "__main__":
    run()
