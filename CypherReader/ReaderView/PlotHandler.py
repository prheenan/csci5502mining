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
import pyqtgraph as pg
import IgorUtil
from pyqtgraph.Qt import QtCore, QtGui



class PlotOptions:
    def __init__(self,XStartsAtZero=True,SavitskyFilter=0.01,ZoomFactor=20,
                 MaxNumPoints=int(2e5)):
        """
        Returns a class for Plot Options
        
        Args:
             XStartsAtZero: If true, the x of all  plots will be offset to 0
             SavitskyFilter: Factor of points to Savitsky Filter
             ZoomFactor: Displays int(N/zoomFact) points in top plot, assuming
             this dosn't screw up MaxNumPoints

             MaxNumPoints
        Returns:
            a constructured PlotOptions object
        """
        self.NormX = XStartsAtZero
        # may need to update the zoom factor so that the data demands aren't
        # too crazy
        self.ZoomFactor = ZoomFactor
        self.ZoomFactorOrig= ZoomFactor
        self.SavitskyFilter = SavitskyFilter
        self.CurrentPoint = None
        self.AbsMin = 0
        self.SplitIntoApprRetract = True
        self.MaxNumPoints = MaxNumPoints
class PlotHandler:
    # Idea of this class is to encapsulate most of the plotting logic. 
    
    def __init__(self,PlotOpt,PlotTop,PlotBottom,label,ControllerHook):
        """
        Given the top (detail) plot and bottom (all data) plot,
        Initializes all the plotting widgets, etc.
        
        Args:
             PlotOpt: A plotOptions structure to use
             PlotTop: the Detailed plot, zoomed in
             PlotBottom: All of the data to Plot
             label: Label to use on one of the plots
             ControllerHook: Hook to the controller. View will ask it for info
             such as index of a data point, given a mouse click, forward clicks
        Returns:
            layout: The GUI Object for the plot
        """
        self.label = label
        self.PlotOpt = PlotOpt
        self.PlotTop = PlotTop
        self.PlotBottom = PlotBottom
        self.PlotX = None
        self.PlotY = None
        self.PlottedParams = []
        self.PlottedParamsText = []
        #cross hair
        # stolen from 'crosshair.py'.
        self.region = pg.LinearRegionItem()
        self.region.setZValue(self.PlotOpt.ZoomFactor)
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        # POST: all decorators have been made. Re-Add
        self.AddDecorators()
        # connect the updating stuff
        self.region.sigRegionChanged.connect(self.updatePlot)
        self.PlotTop.sigRangeChanged.connect(self.updateRegion)
        self.PlotTop.scene().sigMouseMoved.connect(self.mouseMoved)
        self.PlotTop.scene().sigMouseClicked.connect(self.upperMouseClicked)
        self.PlotBottom.scene().sigMouseClicked.connect(self.lowerMouseClicked)
        self.PlotBottom.sigYRangeChanged.connect(self.BottomYChanged)
        self.handler = ControllerHook
        self.CurrentPoint = None
    def BottomYChanged(self,viewBot,yRange):
        """
        Called with the bottom y changes
        """
        pass
    def AddDecorators(self):
        """
        Assuming they have been created, adds the various plot decorators
        to the plots (e.g. crosshairs)
        
        Args:
            None
        Returns:
            None
        """
        # add the lines
        self.PlotTop.addItem(self.vLine, ignoreBounds=True)
        self.PlotTop.addItem(self.hLine, ignoreBounds=True)
        self.PlotBottom.addItem(self.region, ignoreBounds=True)
    #for next line, see (this is an undocumented function! :
    #https://groups.google.com/forum/#!msg/pyqtgraph/d2uqHW-mFxA/oYmqkTbpd1gJ
        self.PlotTop.setAutoVisible(x=True,y=True)
        self.PlotBottom.setAutoVisible(x=True,y=True)
    def SetNormedX(self,X):
        """
        Normalizes and Sets the current X. Remembers how to denorm for this X
        
        Args:
            X: the data to normalize
        Returns:
            None
        """
        self.AbsMin = np.min(X)
        self.PlotX = X - self.AbsMin
    def DeNormX(self,X):
        """
        Returns a denormalized version of X, given the current norm method.
        In the simplest case, just adds back in the minimum...
        
        Args:
            X: the data to denormalize
        Returns:
            THe denormalized X
        """
        return X + self.AbsMin
    def GetBoundingIdx(self,region):
        """
        Given a region, gets the bounding indices for it. Intended for plotting 
        only, not anything sciency (ie: this rounds and such)

        Args:
            region: the region of a plot
        Returns:
            tuple of idxI,idxF, corresponding to x values
        """
        idxI = self.handler.GetIndexFromPlotXY(self.DeNormX(min(region)),None)
        idxF = self.handler.GetIndexFromPlotXY(self.DeNormX(max(region)),None)
        return idxI,idxF

    def RefreshBottomPlot(self):
        """
        Refreshes the bottom plot only. See 'refreshPlot' for details
        
        Args:
            firstPlot: If true, resets 'zoom' region.
        Returns:
            None
        """
        nPoints = self.PlotX.size
        maxPoints = self.PlotOpt.MaxNumPoints
        bottomX,_ = self.PlotBottom.viewRange()
        if (nPoints > maxPoints):
            decimationFactor = int(np.ceil(nPoints/maxPoints))
            # get the 'decimated' versions for the bottom plot
            decimatedBottomX = self.PlotX[::decimationFactor]
            decimatedBottomY = self.PlotY[::decimationFactor]
        else:
            decimatedBottomX = self.PlotX
            decimatedBottomY = self.PlotY
        self.PlotBottom.plot(decimatedBottomX,decimatedBottomY,pen='w',
                             clear=True)
    def RefreshTopPlot(self,firstPlot=False):
        """
        Refreshes the top plot only plot only. See 'refreshPlot' for details.
        
        Args:
            firstPlot: If true, resets 'zoom' region.
        Returns:
            None
        """
        if (self.PlotOpt.SavitskyFilter is not None):
            rawColor = 0.3
        else:
            rawColor = 'b'
        # check to see if we need to decimate the data
        nPoints = self.PlotX.size
        maxPoints = self.PlotOpt.MaxNumPoints
        if (nPoints > maxPoints):
            # get the 'zoomed in' versions for the top plot
            minX,maxX = self.region.getRegion()
            idxI,idxF = self.GetBoundingIdx([minX,maxX])
            avg = (idxF+idxI)/2
            # center the indices
            minIdx =max(0,avg-maxPoints/2)
            maxIdx =min(nPoints,avg+maxPoints/2)
            # check the edge cases
            if (minIdx == 0):
                maxIdx =maxPoints
            elif (maxIdx == nPoints):
                minIdx = nPoints-maxPoints
            zoomedTopX = self.PlotX[minIdx:maxIdx]
            zoomedTopY = self.PlotY[minIdx:maxIdx]
        else:
            # good to go, don't need to worry about point stuff.
            zoomedTopX = self.PlotX
            zoomedTopY = self.PlotY
        # clear both plots.
        self.PlotTop.plot(zoomedTopX,zoomedTopY,pen=rawColor,clear=True)
        # if we also want the savitsky-filtered data, put that up as well
        # (only on the top)
        if (self.PlotOpt.SavitskyFilter is not None):
            nFilterPoints = int(zoomedTopX.size*self.PlotOpt.SavitskyFilter)
            width = 50
            if (self.PlotOpt.SplitIntoApprRetract):
                xAppr,xRetr,yAppr,yRetr = \
                    IgorUtil.SplitIntoApproachAndRetract(zoomedTopX,
                                                         zoomedTopY)
                filterAppr = IgorUtil.filterForce(yAppr,filterN=nFilterPoints)
                filterRetr = IgorUtil.filterForce(yRetr,filterN=nFilterPoints)
                self.PlotTop.plot(xAppr,filterAppr,width=width,pen='r',
                                  clear=False)
                self.PlotTop.plot(xRetr,filterRetr,width=width,pen='b',
                                  clear=False)
            else:
                 # just filter everything
                filterAll = IgorUtil.filterForce(zoomedTopY,
                                                 filterN=nFilterPoints)
                self.PlotTop.plot(zoomedTopX,zoomedTopY,filterAll,width=width,
                                  pen='r',clear=False)
        # only on the first plot do we mess with the region
        # XXX should probably make this optional...
        if (firstPlot):
            self.PlotOpt.ZoomFactor = max(self.PlotOpt.ZoomFactorOrig,
                                          nPoints/maxPoints)
            minV = min(self.PlotX)
            maxV = max(self.PlotX)
            # get the actual number of indices to plot
            minIdxX = np.argmin(self.PlotX)
            numIdx = nPoints/(self.PlotOpt.ZoomFactor)
            maxIdxX = minIdxX + numIdx
            zoomFactor = nPoints/(numIdx)
            # convert to a plot-specific range
            rangeV = [self.PlotX[minIdxX],self.PlotX[maxIdxX]]
            self.updateRegion(None,[rangeV])
    def RefreshPlot(self,firstPlot=False):
        """
        Refreshes all plots (for example, after options are changes). Plots
        the same data, just with possible new options. Must have set PlotX and
        PlotY. Note this also clears the plots (but adds back in decorators)
        
        Args:
            firstPlot: If true, resets 'zoom' region.
        Returns:
            None
        """
        # plot the 'raw' data as a different color...
        self.RefreshTopPlot(firstPlot=firstPlot)
        self.RefreshBottomPlot()
        # POST: everything else plotted, add the crosshairs
        self.AddDecorators()
    def Plot(self,X,Y,ForceFirstPlot=False):
        """
        Updates the top ('zoomed in') and bottom ('full') plots
        
        Args:
            X,Y: The x and y data to plot
            ForceFirstPlot: If true, forces the plot to totally refresh itself
        Returns:
            None
        """
        firstPlot = ((self.PlotY is None) and (self.PlotX is None)) or \
                    ForceFirstPlot
        if (self.PlotOpt.NormX):
            self.SetNormedX(X)
        else:
            self.PlotX = X
        self.PlotY = Y
        # remove all the old parameters
        self.PlottedParams = [] 
        self.PlottedParamText = []     
        self.RefreshPlot(firstPlot=firstPlot)
    def PlotParameterLine(self,index,text):
        """
        Plots a parameter (verical) line at the point given by the index,
        with a text label given by 'text'
        Args:
            index: a number between [0,N-1] specifying where the line goes
            text: the text label to put on the parameter
        Returns:
            None
        """
        TmpParam = pg.InfiniteLine(angle=90, movable=True)
        x = self.PlotX[index]
        TmpParam.setPos(x)
        mText = pg.TextItem(text=text,anchor=(1,0),angle=90)
        y = np.min(self.PlotY)
        mText.setPos(x,y)
        self.PlotTop.addItem(mText)
        self.PlotTop.addItem(TmpParam)
        # get the index where we will put these tw
        idxParm = len(self.PlottedParams)
        self.PlottedParams.append(TmpParam)
        self.PlottedParamsText.append(mText)
        # add a function to update the text with the line
        # XXX make these work together? ie: single class.
        mFunc = lambda *x,**y:self.updateText(idxParm,*x,**y)
        TmpParam.sigPositionChangeFinished.connect(mFunc)
    def updateText(self,idx,evt):
        mParam = self.PlottedParamsText[idx]
        mParam.setPos(evt.x(),np.max(self.PlotY))
    # following section adapted from 'crosshair.py' in PyQtGraph Examples.
    def updateOnMouseClicked(self,x,y):
        """
        On a mouse click, figures out where we clicked, then informs the 
        Model and Controller what happened. 
        Args:
            evt: event with interaction coordinates (e.g. mouseClicked event)
        Returns:
            None
        """
        # get the index of the associated data point
        index = self.handler.GetIndexFromPlotXY(self.DeNormX(x),y)
        # let the handler know which index we clicked
        self.handler.UserClickedAtIndex(index)
    def lowerMouseClicked(self,evt):
        """
        Wrapper for a mouse clicked event for the upper plot. Checks for the
        region being double clicked on 

        Args:
            evt: event with interaction coordinates (e.g. mouseClicked event)
        Returns:
            None
        """
        if (evt.double()):
            # double clicked somewhere
            scenePos = evt.scenePos()
            vb = self.PlotBottom.vb
            mousePoint = vb.mapSceneToView(scenePos)
            ROI = self.region.getRegion()
            minR = ROI[0]
            maxR = ROI[1]
            myX = mousePoint.x()
            if (myX < minR or myX > maxR):
                return
            # POST: within the region. zoom in by a factor
            factor = 2
            rangeV = maxR-minR
            divRange = 2*factor # we want the go symmetrically from the midpoint
            mid = (minR+maxR)/2
            newRegion = [mid-rangeV/(divRange),mid+rangeV/(divRange)]
            self.updateRegion(None,[newRegion])
            self.RefreshTopPlot(firstPlot=False)
            # check if we need to update the bottom range. say if it is 10% or
            # less XXX make this an option
            fraction = 0.1
            bottomX,_ = self.PlotBottom.viewRange()
            rangeBottom = bottomX[1]-bottomX[0]
            bottomFraction = rangeV/rangeBottom
            if bottomFraction < fraction:
                minX = mid-rangeV * (fraction/bottomFraction)
                maxX = mid+rangeV * (fraction/bottomFraction)
                # refresh the bottom plot, to decrease decimation
                self.PlotBottom.setXRange(minX, maxX, padding=0)

    def upperMouseClicked(self,evt):
        """
        Wrapper for a mouse clicked event for the upper plot
        
        Args:
            evt: event with interaction coordinates (e.g. mouseClicked event)
        Returns:
            None
        """
        self.PlotInteractionEvent(evt,self.updateOnMouseClicked)
    def PlotInteractionEvent(self,evt,callIfReal):
        """
        Given an event with coordinates in the graph, converts to data 
        coordinates and then calls 'callIfReal', if we were in the graph range
        
        Args:
            evt: event with interaction coordinates (e.g. mouseClicked event)
            callIfReal: A function to call with x and y, *in terms of plotted
            data in the top (detail) plot*. Only called if we are in range, etc
        Returns:
            None
        """
        if (self.PlotY is None or self.PlotX is None):
            # no data; nothing to do
            return
        try:
            x = evt.x()
            y = evt.y()
            pos = pg.QtCore.QPointF(x, y)
        except AttributeError:
            # if we dont have a 'normal' x-y, use the scene position
            pos = evt.scenePos()
            x = pos.x()
            y = pos.y()
        if self.PlotTop.sceneBoundingRect().contains(pos):
            # deterine if the positions are actually in the coordinates
            vb = self.PlotTop.vb
            mousePoint = vb.mapSceneToView(pos)
            x = mousePoint.x()
            y = mousePoint.y()
            # call the function with whatever the user wants
            callIfReal(x,y)
    def updateOnMouseMoved(self,x,y):
        fmtStr = "<span style='font-size: 12pt'>idx=%07d,   " +\
                 "<span style='color: red'>x=%0.4g</span>,   "+\
                 "<span style='color: green'>y=%0.4g</span>"
        # get the index into the data based on the x and y points
        absX = self.DeNormX(x)
        index = self.handler.GetIndexFromPlotXY(absX,y)
        # get the *plotted* data at the index (closest to what the user wants)
        dataX = self.PlotX[index]
        dataY = self.PlotY[index]
        # set the legend...
        if index > 0 and index < len(self.PlotY):
            self.label.setText(fmtStr % (index, dataX,dataY))
        self.vLine.setPos(dataX)
        self.hLine.setPos(dataY)
        # Remove the old marker, if there is one.
        if (self.CurrentPoint is not None):
            self.PlotTop.removeItem(self.CurrentPoint)
        # put a marker on the dataset, save it so we can remove it later.
        self.CurrentPoint = self.PlotTop.plot([dataX],[dataY],
                                              symbol='o')
    def mouseMoved(self,evt):
        """
        Plot the crosshairs, data marker, and update the labels for this point
        
        Args:
            evt: event with interaction coordinates (ie mouseMoved event)
        Returns:
            None
        """
        # if we are dealing with normalized x values, then we
        # convert back to absolute to get the index.
        # formatting string for printing out the indices...
        self.PlotInteractionEvent(evt,self.updateOnMouseMoved)
    def updatePlot(self):
        """
        Signal handler for updating (top) plot after a region change. Uses
        the current zoom factor and (lower) plot region)
        
        Args:
            None
        Returns:
            None
        """
        minX, maxX = self.region.getRegion()
        viewX,_ = self.PlotTop.viewRange()
        minView,maxView = viewX
        if (minX < minView or  maxX > maxView):
            self.RefreshTopPlot(firstPlot=False)
        self.region.setZValue(self.PlotOpt.ZoomFactor)
        self.PlotTop.setXRange(minX, maxX, padding=0)
    def updateRegion(self,window,viewRange):
        """
        Signal handler for updating the region. Updates the region (which 
        triggers the upper plot to be updated, by 'update plot)
        
        Args:
            window: from event handler
            viewRange: from event handler
        Returns:
            None
        """
        rgn = viewRange[0]
        self.region.setRegion(rgn)

