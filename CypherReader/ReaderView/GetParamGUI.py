# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
import BasicParams

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import ParamUtil

def GetParameterLayout(MetaOpt,FuncParamChange,FuncLoadFileClick):
    """
    Returns the GUI associated with the parameter GUI, given the 
    options for the parameters. 

    Args:
        MetaOpt: List of options, like return MetaParamOpt.GetMetaTableOptions()
        ParamChange: Function to connect for parameters changes
    Returns:
        layout: The GUI Object
    """
    layout = QtGui.QGridLayout()
    MParams = BasicParams.PopulateMetaParams(MetaOpt)
    params,tree = BasicParams.MakeParameterTree(MParams)
    
    btn = QtGui.QPushButton('Load File')
    # connect the parameter change signal
    params.sigTreeStateChanged.connect(FuncParamChange)
    # connect the file load button
    btn.clicked.connect(FuncLoadFileClick)
    layout.addWidget(btn, 0, 0)   # button goes in upper-left
    layout.addWidget(tree, 1, 0)   # button goes in upper-left
    return layout
    
if __name__ == "__main__":
    run()
