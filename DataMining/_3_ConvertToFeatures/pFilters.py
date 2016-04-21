# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt

import DataMining.DataMiningUtil.Filtering.FilterObj as FilterObj
from scipy import ndimage as ndi
from skimage import feature
from scipy.stats import norm
from FeatureLib.step_detect import step_detect
from PyUtil.GenUtilities import digitize

#from hmmlearn import hmm
from scipy.stats import linregress

def GetFilterConst(time,Multiplier):
        """
        Given a time basis and a multiplier, gets the filtering constant in
        time units
        
        Args:
            time:  to use as a basis
            multiplier: amount to filter
        """
        delta = time[1] - time[0]
        return delta * Multiplier

def FilterToTau(time,multiplier,y):
        """
        Given a time basis and a tau, reutrns the filtered version of y 

        Args:
            time:see GetFilterConst
            multiplier:see GetFilterConst
            y: data to filter
        """
        tau = GetFilterConst(time,multiplier)
        return FilterObj.FilterDataY(time,y,tau)

def StateValueByMedian(Force,Starts,Ends):
    # get the 'state values' of all the stats
    return [np.median(Force[start:end]) \
            for start,end in zip(Starts,Ends)]

def StateValueByLinearFit(Force,Starts,Ends,fudge):
    x = np.arange(start=0,stop=Force.size,step=1)
    starts = []
    ends= []
    for start,end in zip(Starts,Ends):
        sliceV = slice(start+fudge,end-fudge,1)
        xTmp = x[sliceV]
        forceTmp = Force[sliceV]
        # fit a line to this region
        slope,intercept,_,_,_ = linregress(xTmp-xTmp[0],forceTmp)
        # get the actual change
        deltaX = (end-start+1)
        # get the y value we would see at 'end', according to the fit
        fitYEnd = intercept + slope * deltaX
        # for y, need to walk back by a factor of the fudge factor
        fitYStart = intercept - slope * fudge
        starts.append(intercept)
        ends.append(fitYEnd)
    return starts,ends

def DebugPlotStateValueByLinFit(startForce,endForce,force,starts,ends,toRet):
    plt.figure()
    plt.subplot(3,1,1)
    plt.plot(force,'b-')
    for i,(startV,endV) in enumerate(zip(startForce,endForce)):
        plt.plot(starts[i],startV,'ro')
        plt.plot(ends[i],endV,'ro')
    idxEvent = np.where(toRet > 0)[0]
    if (idxEvent.size> 0):
        plt.subplot(3,1,2)
        plt.plot(idxEvent,force[idxEvent])
        plt.subplot(3,1,3)
        plt.plot(idxEvent,toRet[idxEvent])
    plt.show()

def WalkEventIdx(force,idx,fudge=50):
    """
    Utility function. Given indices at which an event are happening, 'walks' 
    backwards and forwards to the event boundaries, setting everything to 
    one in between

    Args:
        force: the actual data; we consider the median between two events
        to be the 'stable' value for that state
     
        idx: indices into force at which we have a transition
        fudge: window around events...

    Returns:
        binary 0/1 array for all the data
    """
    # we will return 0/1 for all points
    n = force.size
    toRet = np.zeros(n)
    # we need to figure out where the event boundaries are,
    # so we continue to the 'left' and 'right' (in time)
    # from an event, until reaching the medians
    # start[i] and end[i]
    # will be the region boundaries before event [i]
    # (so start[i+1] and end[i+1] are the boundaries for event i+1)
    starts = [0] + list(idx)
    ends = list(idx) + [n-1]
    startForce,endForce = StateValueByLinearFit(force,starts,ends,fudge)
    # now we (probably) need to update the indices we are returning
    # idxArr will let us mask to the region we are about, relative to
    # our event
    idxArr = np.arange(n)
    for eventNum,i in enumerate(idx):
            # get the median 'Low' and 'hi' (before and after, respectively)
            # low is the end of the last state
            medLow = endForce[eventNum]
            # upper bound is the start of the next state
            medHi = startForce[eventNum+1]
            # last time ([-1]) we are below med, before i
            set1 = np.where( (force - medLow <= 0) & (idxArr < i))[0][-1]
            # first time ([0]) we are above med, after i
            set2 = np.where( (force - medHi >= 0) & (idxArr > i))[0][0]
            toRet[set1:set2] = 1
            # set the exponential decay on either side
            end = set2
            start = set1
            size = ((end-start)+1)
            if (end+size > toRet.size or
                start-size < 0):
                continue
            # POST: can decay to end...
            rangeV = np.arange(0,size)
            # exponentially decay away from where the think the events are...
            # after 1 size, we want to be extremely supressed (<1%)
            decay = np.exp(-10*rangeV/(size))
            toRet[start-size:start] = decay[::-1]
            toRet[end:end+size] = decay
    #DebugPlotStateValueByLinFit(startForce,endForce,force,starts,ends,toRet)
    return toRet


def CannyFilter(time,sep,rawForce,Meta,tauMultiple=25,**kwargs):
        """
        Uses a canny filter (from image processing) to detect change points

        Args:
            time,sep,force,Meta,tauMultiple: see ZScoreByDwell
        Returns:
            0/1 matrix if we think there is or isnt an array
        """
        force = FilterToTau(time,tauMultiple,rawForce)
        n = force.size
        minV = np.min(force)
        maxV = np.max(force)
        # normalize the force 
        force -= minV
        force /= (maxV-minV)
        gradV = np.gradient(force)
        stdev = np.std(gradV)
        mu = np.mean(gradV)
        # convert the force to an image, to make Canny happy
        im = np.zeros((n,3))
        im[:,1] = force
        # set the 'sigma' value to our filtering value
        sigma = tauMultiple
        edges1 = feature.canny(im,sigma=sigma,low_threshold=0.8,
                               high_threshold=(1-10/n),use_quantiles=True)
        edges2 = feature.canny(im * -1,sigma=sigma,low_threshold=0.8,
                               high_threshold=(1-10/n),use_quantiles=True)
        # get where the algorithm thinks a transtition is happenening
        idx = np.where((edges1 == True) | (edges2 == True))[0]
        idx = WalkEventIdx(rawForce,idx)
        # switch canny to be between -0.5 and 0.5
        return idx - 0.5

def MinMaxNorm(y):
        minV = np.min(y)
        maxV = np.max(y)
        return (y - minV)/(maxV-minV)

def HmmFilter(time,step,force,Meta,tauMultiple=25,n_iter=200,n_states=2,
              nBins = 50,**kwargs):
        filterForce = FilterToTau(time,tauMultiple,force)
        filterData = filterForce
        binarized = digitize(filterData,nBins)
        toFit = np.column_stack([binarized])
        model = hmm.GaussianHMM(n_components=n_states, covariance_type="diag",
                                n_iter=n_iter)
        model.fit([toFit])
        statePredictions = model.predict(toFit)
        whereSwitchIdx = np.where(np.diff(statePredictions) > 0.5)[0]
        return WalkEventIdx(force,whereSwitchIdx)


def ForwardWaveletTx(time,sep,force,Meta,tauMultiple=25,nWaveletIters=10,
                     **kwargs):
        filterData = FilterToTau(time,tauMultiple,force)
        detected = step_detect.mz_fwt(filterData, n=nWaveletIters)
        filtered = np.abs(FilterToTau(time,tauMultiple,
                                      detected - np.median(detected)))
        # XXX for now just assumes one event
        toRet= WalkEventIdx(force,[np.argmax(filtered)])
        return toRet

def ForceFiltered(time,sep,force,Meta,tauMultiple=25,**kwargs):
        """
        Gets the filtered force as min-max amount all

        Args:
             time,sep,force,Meta,tauMultiple: see ZScoreByDwell
        """
        filterData = FilterToTau(time,tauMultiple,force)
        # normalize the data
        minV = np.min(filterData)
        maxV = np.max(filterData)
        minMax=  (filterData - minV)/(maxV-minV) - 0.5
        # now get the 'offset' minMax array
        filterDataOffset = minMax[:-tauMultiple]
        toRet = minMax.copy()
        toRet[:tauMultiple] = 0 
        toRet[tauMultiple:] *= filterDataOffset
        return toRet

def ZScoreByDwell(time,sep,force,Meta,tauMultiple=25,**kwargs):
        """
        Gets the z score by the product of the local and dwell zscores

        Args:
            time: the time to use
            sep: separation
            force: force
            Meta:  see pFeatureGen

            tauMultiple: tunable parameter, what fraction of the 'minimum 
            event time' (fMax-fMin)/(dfMax/dtMax) to tune to
        Returns: the feature we would like.
            
        """
        summaries = Meta.Summary
        dwellDist = summaries.CorrectedAndFilteredDist.dwell.GradY
        dwellMean = dwellDist.mean
        dwellStd = dwellDist.std
        # figure out what the tau should be
        filterData = FilterToTau(time,tauMultiple,force)
        # get the filtered graient
        grad = np.gradient(filterData)
        # get the z score of this, relative to itself
        meanV = np.mean(grad)
        gradZLocal = FilterToTau(time,tauMultiple,(grad-meanV)/np.std(grad))
        # get the z score of this, relative to 'global' information
        gradZDwell = FilterToTau(time,tauMultiple,(grad-dwellMean)/dwellStd)
        # combine the local and global information
        zScore =    FilterToTau(time,tauMultiple,gradZLocal)
        # get the survival probability
        mObj = norm()
        prob = FilterToTau(time,tauMultiple,np.abs(mObj.logsf(zScore)))
        # zero out the boundaries, where we filter
        prob[:tauMultiple] =min(prob)
        prob[-tauMultiple:] =min(prob)
        # make the probabilty a zero point
        final = prob - np.abs(mObj.logsf(0))
        return final

def pFeatureGen(obj,func,*args,**kwargs):
        """
        Patrick-style feature generator

        Args: 
           obj: PreProcessedObject
           func: function of the form <time,sep,force,meta>, where
           time,sep, and force are per-window, meta is all the meta information
        """
        meta = obj.Meta
        Name = obj.HiResData.meta.Name
        timeWindow,sepWindow,forceWindow =  obj.HiResData.GetTimeSepForce()
        toRet = [func(time,sep,force,meta,*args,**kwargs) \
                 for time,sep,force in zip(timeWindow,sepWindow,forceWindow)]
        return toRet
        
