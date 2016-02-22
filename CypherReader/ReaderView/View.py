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
import BasicParams
import IgorUtil

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import ReaderController.ParamUtil

from PlotHandler import PlotOptions,PlotHandler


class View:
    def __init__(self,PlotOpt=PlotOptions()):
        """
        Returns a class for an IGor View
        
        Args:
            PlotOptions: PlotOptions instance to use for plotting...
        Returns:
            a constructured ViewObject
        """
        self.params = None
        self.wavelist = None
        self.PlotOpt = PlotOptions()
    def GetParameterLayoutAndSetHandlers(self,MetaOpt,EventHandler):
        """
        Returns the GUI associated with the parameter GUI, given the 
        options for the parameters. 
        
        Args:
             MetaOpt: List of options, like return of GetMetaTableOptions()
             EventHandler: A Controller EventHandler object, to hook signals to
        Returns:
            layout: The GUI Object
        """
        layout = QtGui.QGridLayout()
        MParams = BasicParams.PopulateMetaParams(MetaOpt)
        self.params,self.ParamTree = BasicParams.MakeParameterTree(MParams)
        self.handler = EventHandler
        # connect the parameter change signal
        self.params.sigTreeStateChanged.connect(
            EventHandler.HandleMetaParameter)
        # connect the file load button
        btn = QtGui.QPushButton('Load File')
        btn.clicked.connect(EventHandler.HandleLoadFile)
        # list of waves
        self.waveList = QtGui.QListWidget()
        self.waveList.currentTextChanged.connect(EventHandler.HandleSelectWave)
        layout.addWidget(btn, 0, 0)   # button goes in upper-left
        layout.addWidget(self.waveList, 1, 0)   # parameter after button...
        layout.addWidget(self.ParamTree, 2, 0)   # parameter after button...
        return layout
    def GetPlotLayoutAndSetHandlers(self,EventHandler):
        """
        Returns the GUI associated with the plot GUI, given the 
        handlers for the parameters. 
        
        Args:
             EventHandler: A Controller EventHandler object, to hook signals to
        Returns:
            layout: The GUI Object for the plot
        """
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox
        # to exclude this item when doing auto-range calculations.
        layoutTop = QtGui.QGridLayout()
        # get the 'real' layout (graphical)
        layout = pg.GraphicsLayoutWidget()
        layoutTop.addWidget(layout)
        self.label = pg.LabelItem(justify='right')
        layout.addItem(self.label)
        # XXX TODO: add in label
        # button goes in upper-left
        self.PlotTop = layout.addPlot(1, 0)
        # button goes in upper-left
        self.PlotBottom = layout.addPlot(2, 0)
        self.PlotDelegate = PlotHandler(self.PlotOpt,self.PlotTop,
                                        self.PlotBottom,self.label,self.handler)
        return layoutTop
    def Plot(self,*args,**kwargs):
        """
        Forwards plotting requests to the PlotDelegate
        
        Args:
            See PlotHandler.Plot
        """
        self.PlotDelegate.Plot(*args,**kwargs)
    def PlotParameterLine(self,*args,**kwargs):
        """
        Forwards plotting requests to PlotHandler
        
        Args:
            See PlotHandler.PlotParameterLine
        """
        self.PlotDelegate.PlotParameterLine(*args,**kwargs)
        
    def GetSqlMetaParams(self):
        """
        Returns values associated with each meta table the view (e.g. tipType)
        
        Args:
             None
        Return :
             A dictionary. Each key is a table name; each value is a dictionary
             for each field in the table
        """
        parameters = self.params.names
        tables = parameters.keys()
        # loop through eah table, get its associated values.
        toRet = dict()
        for t in sorted(tables):
            toRet[t] = self.GetTableValues(parameters,t)
        return toRet

    def GetTableValues(self,parameters,table):
        """
        Retruns a dictionary associated with a table from a Parmeter Object
        
        Args:
             parameters: a dict where key-value is tablename, 
             (group) parameter object corresponding to a single table

             table: which table we want the values of
        Return :
             A dictionary. Each key is a table name; each value is a dictionary
             for each field in the table
        """
        toRet = dict()
        mTable = parameters[table]
        fields = mTable.getValues()
        # loop through each (XXX assumed leaf) child, get its value (first ele)
        # from the tuple
        for fieldName in sorted(fields.keys()):
            toRet[fieldName] = fields[fieldName][0]
        # POST: all populated; key-value pairs...
        return toRet
