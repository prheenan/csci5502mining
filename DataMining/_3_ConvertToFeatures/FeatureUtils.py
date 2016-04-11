# Force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes
import numpy as np
import matplotlib.pyplot as plt
import sys
import DataMining.DataMiningUtil.Filtering.FilterObj as FilterObj

def TestFunction(obj):
	'''
	Returns a flattened window
	Args:
		obj: preprocessed object with the windows we want
	Returns a flattaned list of hi res data from the window
	'''
	return [data for window in obj.HiResData.HiResData\
			for data in window]

def grad_std(filtered_obj):
	'''
	Normalizes to a standard curve
	'''
	filteredGradient = np.gradient(filtered_obj)
	stdV = np.std(filteredGradient)
	zGrad = (filteredGradient - np.mean(filteredGradient))/stdV
	return zGrad

def grad_minmax(filtered_obj):
	'''
	Normalizes via Min-Max
	'''
	filteredGradient = np.gradient(filtered_obj)
        minV = filteredGradient.min()
        maxV = filteredGradient.max()
	norm = (filteredGradient - minV) / (maxV-minV)
	return norm

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
        deltaT = time[1] - time[0]
        filterTau = tauMultiple * deltaT
        filterData = FilterObj.FilterDataY(time,force,filterTau)
        # get the filtered graient
        grad = np.gradient(filterData)
        # get the z score of this, relative to itself
        gradZLocal = (grad - np.mean(grad))/np.std(grad)
        # get the z score of this, relative to 'global' information
        gradZDwell = (grad - dwellMean)/dwellStd
        # combine the local and global information
        zScore =   np.minimum(np.abs(gradZLocal),np.abs(gradZDwell))
        return  zScore

def pFeatureGen(obj,func,*args,**kwargs):
        """
        Patrick-style feature generator

        Args: 
           obj: PreProcessedObject
           func: function of the form <time,sep,force,meta>, where
           time,sep, and force are per-window, meta is all the meta information
        """
        meta = obj.Meta
        timeWindow,sepWindow,forceWindow =  obj.HiResData.GetTimeSepForce()
        toRet = [func(time,sep,force,meta,*args,**kwargs) \
                 for time,sep,force in zip(timeWindow,sepWindow,forceWindow)]
        return toRet
        
def featureGen(obj, data_type, norm,timeMultiple=400):
	'''
	Function finds features of force derivative objects based on arguments
	Args:
		obj : Preprocessed data
                data_type : Type of data give. Options - 'force' or 'separation'
		norm : Type of normalization fo be used. Options - 'std' or 
                'minmax'
                timeMultiple: amount to filter, in units of the time basis
	'''
	progs = {
			'std' : grad_std,
			'minmax' : grad_minmax
			}
	features = list()
	timeWindow,sepWindow,forceWindow = \
		obj.HiResData.GetTimeSepForce()
	nWindows = len(sepWindow)
        # time is uniform; should just be the step [1]-[0] for any window
        # (say, the first)
        timeDelta = timeWindow[0][1] - timeWindow[0][0]
	timeConst = timeMultiple*timeDelta
	mFiltering = FilterObj.Filter(timeConst = timeConst)
	if data_type.lower() == 'force':
		for i,(time,sep,force) in enumerate(zip(timeWindow,sepWindow,
                                                        forceWindow)):
			filteredForce = mFiltering.FilterDataY(time,force)
			features.append(progs[norm](filteredForce))

	elif data_type.lower() == 'separation':
		for i,(time,sep,force) in enumerate(zip(timeWindow,sepWindow,
                                                        forceWindow)):
			filteredSep = mFiltering.FilterDataY(time,sep)
			features.append(progs[norm](filteredSep))

	else:
		print "Error: Invalid data type input." +\
                        "Valid inputs are 'force' or 'separation'"
		return

	return features
