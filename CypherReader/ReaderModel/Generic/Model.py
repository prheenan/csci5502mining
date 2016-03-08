# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
import PyUtil.CypherUtil as CypherUtil
import Parameter 
import abc
import os
import CypherReader.ReaderModel.SqlDataModel.SqlDataModel as SqlDataModel
from PyUtil import SqlUtil
from CypherReader.IgorAdapter.BinaryHDF5Io import ConcatenateWaves
from CypherReader.IgorAdapter.ProcessSingleWave import WaveObj
from CypherReader.UnitTests.TestingUtil.UnitTestUtil import AssertIntegral

from WaveDataGroup import WaveDataGroup
import CypherReader.ReaderModel.DataCorrection.CorrectionMethods as \
    CorrectionMethods
import CypherReader.ReaderModel.LargeDataManagement.LargeDataManager as \
    LargeDataManager


class ModelOpt(object):
    def __init__(self,IndexAfterMinOnly=False):
        self.IndexAfterMinOnly = IndexAfterMinOnly
        
# Class for the default model with lots of features
class Model(object):
    __metaclass__  = abc.ABCMeta

    def __init__(self):
        """
        Initialization for (base) model class.

        Args:
             None
        Returns:
             Instantiated Model object (must inherit; this class is abstract)
        """
        self.View = None
        self.Waves = LargeDataManager.LargeDataManager()
        # get the meta parameters and the (possible trivial) meta dictionary
        self.ParamMeta,self.StateDict = self.GetParameterMetaInfo()
        self.CurrentParams = []
        self.CurrentParamNum = 0
        # initially, nothing selected (empty string OK? XXX) 
        self.CurrentWaveName = ""
        # XXX TODO add in option to not always auto-update. Safer this way
        self.AutoUpdate = True
        self.ModelOpt = ModelOpt()
        # start off with no group selected
        self.CurrentAssociatedWaveGroup = None
    @abc.abstractmethod
    def GetParameterMetaInfo(self):
        """
        Gets a ParameterMeta object associated with this model. Abstract!
        Args:
             None
        Returns:
             A ParameterMeta Object
        """
        return None
    @abc.abstractmethod
    def ModelName(self):
        """
        Gets the name of this model. Abstract; real models must give a name
        Args:
             None
        Returns:
             String, model name
        """
        return "Abstract Model"
    def ParameterMade(self,PrevParamNum,CurrentParamNum):
        """
        State machine to take care of all the creation of parameters

        Args:
            PrevParamNum: the previous prameter number. Between 0 and 
            len(paramMeta)

            PrevParamNum: the current parameter number. This parameter has just
            been created. Between 0 and len(paramMeta)

        Returns:
             None
        """
        # see if we have to make a transition
        # XXX add in current state to dictionry
        if CurrentParamNum in self.StateDict:
            # then make the transition!
            mObj = self.StateDict[CurrentParamNum]
            # call the function
            mObj.func()
            # set the state
            self.currentState = mObj.stateToSet
            self.CurrentX,self.CurrentY = self.getDataToPlot(self.CurrentWave())
            # plot everything again...
            self.PlotCurrentXandY()
    def PlotCurrentXandY(self):
        """
        Plots the current X and Y as *new plots* on the view. Destroys whatever
        was there...
        """
        self.View.Plot(self.CurrentX,self.CurrentY,ForceFirstPlot=True)
    def ResetForNewWave(self):
        """
        For overloading, state machines may want to know if we select a new wave
        (only called when the wave is changing...)

        Args:
            None

        Returns:
             None
        """
        pass
    def getDataToPlot(self,WaveDict):
        """
        Given a set of associated waves, get the X and Y data to plot. Specific
        Models may want to overridee
        
        Args:
             WaveDict:WaveDataGroup. Has not and high-resolution data
        Returns:
            X,Y: Data to plot on x and y axis
        """
        return CypherUtil.GetSepForce(WaveDict)
    def SetView(self,View):
        """
        Function to set the view. Must be called before messing with events
        
        Args:
             View: output from PxpLoader.LoadPxp
        Returns:
            None
        """
        self.View = View
    def AddNewWaves(self,waves,SourceFile):
        """
        Add non-duplicates present in 'Waves' to the wave list.
        Args:
            Waves: two-level dict of <WaveId:<Dict of associated waves>>. Only
            add waves with non-duplicate IDs

            SourceFile: Where the data is coming from (full Path)
        """
        # only add non-duplicates
        keys = waves.keys()
        uniqueWaves = dict([(key,wave)
                            for key,wave in waves.items()\
                            if key not in self.Waves])
        # get the waves we want to add from the list
        wavesToAdd = self.CustomGetWaves(uniqueWaves,SourceFile)
        addMethod = lambda name: self.View.waveList.addItem(name)
        # add to the cache
        self.Waves.AddData(wavesToAdd,addMethod)
    def CustomGetWaves(waves,SourceFile):
        """
        Function which gets new waves, from a loaded file. Should *not*
        Alter self.Waves...
        
        Args:
             waves : output from PxpLoader.LoadPxp
             SourceFile : Full path where the wave originated from
        Returns:
            Waves which should be added to the cache
        """
        Waves = dict()
        for name,associatedWaves in waves.items():
            # add in the new wave
            Waves[name] = WaveDataGroup(associatedWaves,SourceFile)
        return Waves
    def CurrentWave(self):
        """
        Returns the current WaveObject we have right now. raises an error if
        there aren't any waves
        
        Args:
            None
        Returns:
            The wave object
        """
        mKeys = self.Waves.keys()
        if (self.CurrentWaveName not in mKeys):
            raise KeyError("Couldn't find {:s} in Waves".\
                           format(self.CurrentWaveName))
        # POST: the wave exists
        return self.CurrentAssociatedWaveGroup
    def SetCurrentWaveByKey(self,waveName):
        """
        See SelectWaveByKey. This does *not* update the view
        
        Args:
             waveName: String used for the wave name 
        Returns:
            None
        """
        # if we aren't actually changing the wave, dont do anything.
        if (waveName.lower() == self.CurrentWaveName.lower()):
            return
        if (self.CurrentAssociatedWaveGroup is not None):
            # update the old data (maybe cached), switching to new
            self.Waves.UpdateData(self.CurrentWaveName,
                                  self.CurrentAssociatedWaveGroup)
        # POST: new wave, something to do.
        # reset all the parameters, set the wave
        self.CurrentWaveName = waveName
        self.CurrentParams = []
        self.CurrentParamNum = 0
        self.ResetForNewWave()
        self.CurrentAssociatedWaveGroup = self.Waves[self.CurrentWaveName]
        self.CurrentX,self.CurrentY = \
                self.getDataToPlot(self.CurrentAssociatedWaveGroup)
    def SelectWaveByKey(self,waveName):
        """
        Select the wave with the given key from the dictionary. If the wave is
        already selected, does nothing. *Updates the view*
        
        Args:
             waveName: String used for the wave name 
        Returns:
            None
        """
        self.SetCurrentWaveByKey(waveName)
        # POST: the X and Y to plot are set
        self.PlotCurrentXandY()
    def SelectWave(self,ItemName):
        """
        Select a wave from a list. For more complicated functions, this might
        involve some pre-processing step. Here, we just plot y vs x
        
        Args:
             ItemName: name (key into self.Waves) to plot
        Returns:
            None
        """
        self.SelectWaveByKey(str(ItemName))
    def IndexXY(self,X,Y=None):
        """
        Given an X and an (optional) Y in the dataspace, 
        gets the index associated with the data. This is useful for if (e.g.)
        we only want indices from the approach
        
        Args:
             Index: an integer index into the data associated with x and y. By
             defauly, assumes we want the approach portion... 
        Returns:
            None
        """
        if (self.ModelOpt.IndexAfterMinOnly):
            minIdx = np.argmin(self.CurrentX)
            mSlice = slice(minIdx,)
            xToCheck = self.CurrentX[mSlice]
        else:
            xToCheck = self.CurrentX
        # evidently numpy is smart enough to figure out what we mean when
        # we use a slice here -- this gives the *absolute* index, even if we
        # slice
        index = np.argmin(np.abs(xToCheck-X))                      
        return index
    def NParams(self):
        """
        Returns the number of parameters associated with this model
        
        Args:
            None
        Returns:
            integer number of parameters
        """
        return len(self.ParamMeta.mParams)
    def PushToDatabase(self):
        """
        Pushes all of the current data to the database. If necessary, saves
        out the binary files as well. 
        
        Args:
            None
        Returns:
            the id values returned by this
        """
        # get all of the meta information we need to uniquely identify
        # this data
        ModelName = self.ModelName()
        AssociatedWaveData = self.CurrentWave()
        MetaViewParams = self.View.GetSqlMetaParams()
        ParameterDescriptions =  self.ParamMeta
        CurrentParams =  self.CurrentParams
        mSqlObj = SqlUtil.InitSqlGetSessionAndClasses()
        namespace = SqlDataModel.PushToDatabase(ModelName,
                                                AssociatedWaveData,
                                                MetaViewParams,
                                                ParameterDescriptions,
                                                CurrentParams,
                                                SqlObj=mSqlObj)
        AssociatedWaveData.SetSqlIds(namespace)
        return namespace
    def AddParameterToModelFromIndex(self,index):
        """
        See AddParameterFromIndex. This does *not* update the view.
        
        Args:
            Index: the in-range location of the data click
        Returns:
            wrapIdx, the index of the parameter (possibly an update)
        """
        n = self.CurrentX.size
        if (not (index < n)):
            raise IndexError("No index {:d} in array of size {:d}".\
                             format(index,n))
        x = self.CurrentX[index]
        y = self.CurrentY[index]
        newDat = Parameter.ParameterData(index,x,y)
        ParamMetaList = self.ParamMeta.mParams
        nParams = len(ParamMetaList)
        if (nParams == 0):
            raise ValueError("Model instantiated without Parameters")
        wrapIdx = self.CurrentParamNum % nParams
        if (self.CurrentParamNum >= nParams):
            # then all the parameter are here. 'Wraparound'
            self.CurrentParams[wrapIdx] = newDat
        else:
            # can simply add
            self.CurrentParams.append(newDat)
        # let the specific model know what parameters we just used.
        self.CurrentParamNum += 1
        self.ParameterMade(wrapIdx, self.CurrentParamNum % nParams)
        if (self.AutoUpdate and self.CurrentParamNum >= nParams):
            self.PushToDatabase()
        return wrapIdx
    def AddParameterFromIndex(self,index):
        """
        Given an index where a user clicked (in between 0 and N-1, N is current
        X and Y data), save a parameter associated with the current model.
        * Updates the View * 
        
        Args:
            Index: the in-range location of the data click
        Returns:
            None
        """
        AssertIntegral(index)
        # POST: index is integral
        # XXX TODO: check in bounds? 
        # determine if we need to 'wraparound'
        wrapIdx =self.AddParameterToModelFromIndex(index)
        # POST: model updated. update the view accordingly.
        # call the view back to plot the parameters
        self.View.PlotParameterLine(index,
                                    self.ParamMeta.mParams[wrapIdx]["Name"])

def CreateWaveObjsForCorrectedHiResSepForce(waveDataGroup,idxLowResTouch,
                                            idxHiResTouch):
    """
    Given a WaveDataGroup, and a set of correction indices into the data,
    returns the separation and force as waveObj

    Args:
        See GetCorrectedHiResSepForce
    Returns:
        tuple of <sepArray,forceArray>
    """
    sep,force = GetCorrectedHiResSepForce(waveDataGroup,idxLowResTouch,
                                          idxHiResTouch)
    # set the wave data group stuff of the object to the new high res d
    hiResNote = waveDataGroup.HighBandwidthWaves.values()[0].Note
    return WaveObj(DataY=sep,Note=hiResNote),\
        WaveObj(DataY=force,Note=hiResNote)

def GetCorrectedHiResSepForce(waveDataGroup,idxLowResTouch,idxHiResTouch):
    """
    Given a WaveDataGroup, and a set of correction indices into the data,
    returns the corrected Hi resolultion separation and force as single arrays

    Args:
        waveDataGroup :  the WaveDataGroup object to use. Should have low+ high 
        res data. 

        idxLowResTouch : a 2-dimensional index array into the *low res* data, 
        element [0] is the start of dwell, element [1] is the end of dwell

        idxHiResTouch : a 2-dimensional index array into the *hi res* data, 
        element [0] is the start of dwell, element [1] is the end of dwell

    Returns:
        tuple of <sepArray,forceArray>
    """
    # make sure the indices are correct, and we have high-bandwidh data
    assert len(idxLowResTouch) == len(idxHiResTouch)
    assert len(idxLowResTouch) == 2
    assert waveDataGroup.HasHighBandwidth()
    sliceLowResCorrect,sliceHiResCorrect = \
    CorrectionMethods.GetCorrectionSlices(idxLowResTouch[0],idxHiResTouch[1])
    # use the elementwise average differences to get the time offset
    deltaLow = waveDataGroup.AssociatedWaves.values()[0].DeltaX()
    deltaHi = waveDataGroup.HighBandwidthWaves.values()[0].DeltaX()
    timeOffset = CorrectionMethods.GetTimeOffset(deltaLow,idxLowResTouch,
                                                 deltaHi,idxHiResTouch)
    # ... should make sure the deltas arent the same
    assert not np.allclose(deltaLow,deltaHi) , \
        "High resolution shouldn't have the same delta" 
    return CorrectionMethods.GetCorrectedAndOffsetHighRes(waveDataGroup,
                                                          sliceLowResCorrect,
                                                          sliceHiResCorrect,
                                                          timeOffset)

