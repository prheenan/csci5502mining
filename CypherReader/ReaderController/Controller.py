# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import FileLoader
import ReaderSqlInterface.MetaParamOpt as MetaParamOpt
from ControllerEventHandler import EventWindow
import ReaderView.View
import ReaderModel.HighBandwidthFoldUnfold.HighBandwidthModel as HighBwModel
import ReaderModel.Generic.Model as GenericModel


# -*- coding: utf-8 -*-
"""
This example demonstrates the use of pyqtgraph's parametertree system. This provides
a simple way to generate user interfaces that control sets of parameters. The example
demonstrates a variety of different parameter types (int, float, list, etc.)
as well as some customized parameter types

"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import ParamUtil
# for multi-threaded applications
import threading

def runGUI(win):
    """
    Blocking function which runs the GUI

    Args:
        win: The Qt Window to show
    
    Returns:
        Nothing
    """
    win.show()
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()    


def run(Model,DebugCallbackOnLoad = None):
    """
    Non-Blocking function which runs the GUI and has a callback it calls once 
    the logic and windon are fully loaded

    Args:
        DebugCallbackOnLoad: an optional callback on window loading. Should 
        accept the event handler       
    
    Returns:
        None
    """
    # start up the app
    app = QtGui.QApplication([])
    import pyqtgraph.parametertree.parameterTypes as pTypes
    from pyqtgraph.parametertree import Parameter, ParameterTree,\
        ParameterItem, registerParameterType
    # create the view
    mView = ReaderView.View.View()
    mModel =Model
    # get the event handler..
    mHandlerWindow = EventWindow(mView,mModel,DebugCallbackOnLoad)
    ## Create tree of Parameter objects
    MetaOpt = MetaParamOpt.GetMetaTableOptions()
    # set up the GUI with the event functions...
    treeLayout = mView.GetParameterLayoutAndSetHandlers(MetaOpt,mHandlerWindow)
    # set up the plot
    plotLayout = mView.GetPlotLayoutAndSetHandlers(mHandlerWindow)
    layout = QtGui.QGridLayout()
    mHandlerWindow.setLayout(layout)
    nRows = 3 # two plots
    # parameter tree is leftmost
    layout.addLayout(treeLayout,0,0,nRows,1)
    layout.addLayout(plotLayout,0,1,nRows,1)
    # split off a thread for the GUI.
    mHandlerWindow.resize(1000,800)
    runGUI(mHandlerWindow)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    run()
