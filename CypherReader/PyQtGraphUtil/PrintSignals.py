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

# see: https://groups.google.com/forum/#!msg/pyqtgraph/nI5hZJ85N7M/TsPoJfk0V8kJ
def run():
    """
    Prints all PyQtGraph Signals

    Args:
    
    Returns:

    """
    import pyqtgraph as pg
    import inspect
    for n,o in pg.__dict__.items():
        if inspect.isclass(o) and issubclass(o, pg.QtCore.QObject):
            for m,p in o.__dict__.items():
                if 'unbound signal' in str(p):
                    print n, m 


if __name__ == "__main__":
    run()
