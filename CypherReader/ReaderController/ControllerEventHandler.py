# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
import FileLoader
import ParamUtil

import IgorAdapter.PxpLoader as PxpLoader
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

class EventWindow(QtGui.QWidget):
    def __init__(self,View,Model,LoadCallBack=None):
        """
        Controller Class intended to handle all of the event logic for 
        the main window.

        Args:
            View: The View object (for populating the individual Widgets)
            Model: The model to use (to update the view)
            LoadCallBack: a function to call once the window is loaded. Note 
            that this is optional, but useful for debugging.
        Returns:
            Constructed Widget
        """
        QtGui.QWidget.__init__(self)
        self.LoadCallBack = LoadCallBack
        self.View = View
        self.Model = Model
        self.Model.SetView(View)
    def showEvent(self, QShowEvent):
        # "http://pyqt.sourceforge.net/Docs/PyQt4/qshowevent.html"
        #  Spontaneous (QEvent.spontaneous()) show events are sent just after
        # the window system shows the window (*every* time the window is shown)
        if (self.LoadCallBack is not None):
            self.LoadCallBack(self)
    def HandleSelectWave(self,*args,**kwargs):
        self.Model.SelectWave(*args,**kwargs)
    def HandleMetaParameter(self,*args,**kwargs):
        """
        Function to handle when a meta parameter is changed.
        
        Args:
             same as ParamUtil.change, or sigParamTreeChanged
        Returns:
            None
        """
        ParamUtil.change(*args,**kwargs)
    def HandleLoadFile(self):
        """
        Function to interactively (GUI window) handle a file load button click. 
        loads waves in a pxp file.
        
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
        # XXX add in support for more than just pxp
        self.LoadPxpAndAddToModel(fn)
    def LoadPxpAndAddToModel(self,FileName):
        """
        Function to load a pxp file and add associated waves
        
        Args:
            FileName : Full path to the file to load
        Returns:
            None
        """
        mWaves = PxpLoader.LoadPxp(FileName)
        # XXX call the model, which should update the view
        self.Model.AddNewWaves(mWaves,FileName)
    def GetIndexFromPlotXY(self,X,Y=None):
        """
        Given an X and (optional) Y (in abslute *data* coordinates), gets the 
        associated index according to the model
        
        Args:
            X,Y: The x and y coordinates in absolute data coordinates. In other
            words, should match whatever model things the current X and Y (no
            arbitrary offset)
        Returns:
            None
        """
        return self.Model.IndexXY(X,Y)
    def UserClickedAtIndex(self,index):
        """
        Given an index where a user clicked (in between 0 and N-1, N is current
        X and Y data), notify the model. This probably ends up saving a
        parameter.
        
        Args:
            Index: the in-range location of the data click
        Returns:
            None
        """
        return self.Model.AddParameterFromIndex(index)

        
