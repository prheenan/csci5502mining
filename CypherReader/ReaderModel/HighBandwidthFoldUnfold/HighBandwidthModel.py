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
from ReaderModel.Generic.Model import Model,WaveDataGroup,\
    CreateWaveObjsForCorrectedHiResSepForce
from ReaderModel.Generic.StateMachine import StateDict
import ReaderModel.Generic.Parameter as Parameter
from ReaderModel.Generic.Parameter import ParameterMeta
from IgorAdapter import PxpLoader,ProcessSingleWave
import PyUtil.CypherUtil as CypherUtil

class States:
    """
    enumeration of states
    """
    started = 0
    lowResOffset =1,
    hiResOffset = 2,
    hiResCorrected = 3
    
class HighBandwidthModel(Model):
    def __init__(self,nPointsHighBW=1e6,**kwargs):
        """
        Subclass of model which specializes in high bandwidth data.
        
        Args:
             nPointsHighBW : number of datapoints for a wave to be considered
             high bandwidth
        Returns:
            None
        """
        # initialize the model
        # XXX specialize to NUG2 right now
        super(HighBandwidthModel,self).__init__(**kwargs)
        self.nPointsHighBW = nPointsHighBW
        self.currentState = States.started
        # *dont* want to index after the mininimum point only
        self.ModelOpt.IndexAfterMinOnly = False
    def GetParameterMetaInfo(self):
        """
        Gets a ParameterMeta object associated with this model.  Sets the 
        State dictionary table as appropriate. 

        Args:
             None
        Returns:
             tuple of A ParameterMeta Object , state dictionary
        """
        # create the parameters, copy for the state machine
        # (so we can correct for wiggles, interpolate z snsr for high res, etc)
        ParamMeta = Parameter.ParameterMeta()
        ParamMeta.AddParamMeta("1st Surface Touch Low Res",
                                    IsPreProcess=True)
        # after we have created the low res, we should show the
        # deflV vs time
        showHiResDeflCount = ParamMeta.AddParamMeta("2nd Surface Touch Low Res",
                                                    IsPreProcess=True)
        ParamMeta.AddParamMeta("1st Surface Touch High Res",
                                    IsPreProcess=True)
        # after we have all the offset data, correct for the wiggles / offset
        # between the high and low res, always show hi res (actually gettting
        # the parameters we care about)
        correctCount = ParamMeta.AddParamMeta("2nd Surface Touch High Res",
                                                  IsPreProcess=True)
        ParamMeta.AddParamMeta("Surface Location")
        # add in all the ruptures
        for i in range(4):
            ParamMeta.AddParamMeta("Rupture {:d} Start".format(i))
            ParamMeta.AddParamMeta("Rupture {:d} End".format(i))
        # fill out the state dictionary with <param>:<function> pairs
        mTable = [(States.lowResOffset,showHiResDeflCount,
                   self.SwitchToHiResDefl,States.hiResOffset),
                  (States.hiResOffset,correctCount,
                   self.CorrectOffsetAndWiggles,States.hiResCorrected)]
        return ParamMeta,StateDict(mTable)
    def ModelName(self):
        """
        Overriding method, see Generic.Model
        """
        return "HighBandwidthNUG2"
    def SwitchToHiResDefl(self):
        """
        Switches to using hi-res DeflV (done automatically by getDataToPlot)
        """
        self.CurrentX,self.CurrentY = self.getDataToPlot(self.CurrentWave())
        pass
    def getDataToPlot(self,WaveDict):
        """
        See Model.getDataToPlot. Switches what the user sees, depending on 
        what the state is
        
        Args:
             WaveDict: see Model.getDataToPlot
        Returns:
            X,Y: Data to plot on x and y axis
        """
        if (self.currentState == States.started):
            # shouldnt ever get here... 
            assert False , "Reached plotting state when started"
        elif (self.currentState == States.lowResOffset):
            # plot low res force vs time
            time,sep,force = WaveDict.CreateTimeSepForceWaveObject().\
                             GetTimeSepForceAsCols()
            return time,force
        elif (self.currentState == States.hiResOffset):
            force = WaveDict.HighBandwidthGetForce()
            # time asscociated with force is x
            time = WaveDict.HighBandwidthWaves.values()[0].GetXArray()
            return time,force
        else:
            force = self.highForce
            time =force.GetXArray()
            # plot the (assumed saved) corrected high resolution waves
            return time,force.DataY
            
    def CorrectOffsetAndWiggles(self):
        # get the current waves and parameters
        mAssocWaves = self.CurrentWave()
        idxLowResTouch = [self.CurrentParams[0].index,
                          self.CurrentParams[1].index]
        idxHiResTouch = [self.CurrentParams[2].index,
                         self.CurrentParams[3].index]
        # get the offsets from the parameters in times
        sepHi,forceHi = \
            CreateWaveObjsForCorrectedHiResSepForce(mAssocWaves,
                                                    idxLowResTouch,
                                                    idxHiResTouch)
        # create a temporary copy of the high resolution wave for plotting
        # (this is *not* what we save -- we save the raw data )
        self.highForce = forceHi
        self.hiSep = sepHi
        # we *can* save the separation without fear, since we know it is derived
        mAssocWaves.HighBandwidthWaves['sep'] = sepHi
        self.CurrentX,self.CurrentY = self.getDataToPlot(mAssocWaves)
    def ResetForNewWave(self):
        """
        Overriding method, see Generic.Model. Sets the state to the first real
        state
        """
        self.currentState = States.lowResOffset
        # by default, plotting versus time, dont want to split
        self.View.PlotOpt.SplitIntoApprRetract = False
    def WavesValidHighBandwidth(self,dictV,keyIds,i,j):
        """
        Function which checks, given a dictionary, the set of keys,
        and two indices into the keys, if the waves belong together. We check:
        (1) Are the wave Ids sequential?
        (2) Are the proper wave endings there?
        (2a) The low bandwidth must have DeflV and Zsnsr
        (2b) The high bandwidth must have DeflV

        Does *not* 

        Args:
             dictV: a dicitonary where each key is an id, each value is 
             a dict of associated waves:

             keyIdx: the ids associated with dictV (assumed sorted for i,j)
             i,j: the two indices to compare. We assume 0 <= i < j 
        Returns:
            None
        """
        waveNameA = keyIds[i]
        waveNameB = keyIds[j]
        # get the numerical ids
        _,idA,_ = ProcessSingleWave.IgorNameRegex(waveNameA)
        _,idB,_ = ProcessSingleWave.IgorNameRegex(waveNameB)
        idA = int(idA)
        idB = int(idB)
        # check that ids are sequential
        if ( (idA-idB) != 1):
            return False
        # POST: (1) ids are sequential
        # check that the endings we need are here
        assocWavesA = dictV[waveNameA].keys()
        assocWavesB = dictV[waveNameB].keys()
        # demand that we have lower and higher waves
        # XXX make this a parameter we put in
        lowerWaves = ["deflv","zsnsr"]
        higherWaves = ["deflv"]
        # check for lower and upper waves
        for waveEndLow in lowerWaves:
            if waveEndLow not in assocWavesB:
                return False
        for waveEndHigh in higherWaves:
            if (waveEndHigh not in assocWavesA):
                return False
        # POST: (2) all endings are here.
        return True
    
    def AddNewWaves(self,waves,SourceFilePath):
        """
        Overriding Function to add new waves, from a loaded file. Recquires 
        both low and high bandwidth data to be present
        
        Args:
             waves : output from PxpLoader.LoadPxp
             SourceFilePath : where the data is coming from
        Returns:
            None
        """
        # XXX TODO: add in caching
        # get the list of (new) unique names
        uniqueNames = sorted(list(set(waves.keys()) - set(self.Waves.keys())))
        # to load the data, subsequent, unique ids should have the proper waves
        # first, look for waves with high-bandwidth data
        # to do this, we simple get the maximum size of each data for all vals
        getMaxLength = lambda listV: max([listV[ele].DataY.size
                                          for ele in listV.keys()])
        maxLengths = map(getMaxLength,waves.values())
        # look through the candidate indices (ie: where we exceed the threshold)
        for i,lenV in enumerate(maxLengths):
            # check if we have enouhg points, and we have at least one more wave
            if (lenV >= self.nPointsHighBW and i < len(maxLengths) and
                self.WavesValidHighBandwidth(waves,uniqueNames,i-1,i)):
                # then this wave works!
                name = uniqueNames[i]
                # get the low resolution and high resolution waves. we
                # cant convert to force/sep until we interpolate the high res
                # stuff.
                lowRes = waves[uniqueNames[i]]
                hiRes = waves[uniqueNames[i-1]]
                tmp = WaveDataGroup(lowRes)
                tmp.HighBandwidthSetAssociatedWaves(hiRes)
                self.Waves[name] = tmp
                self.View.waveList.addItem(name)
        # POST: all waves set up...
