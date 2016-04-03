# Force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes
import numpy as np
import matplotlib.pyplot as plt
import sys

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
	norm = (filteredGradient - filteredGradient.min()) / (filteredGradient.max() - filteredGradient.min())
	return norm

def featureGen(obj, data_type, norm):
	'''
	Function finds features of force derivative objects based on arguments
	Args:
		obj : Preprocessed data
                data_type : Type of data give. Options - 'force' or 'separation'
		norm : Type of normalization fo be used. Options - 'std' or 'minmax'
	'''
	progs = {
			'std' : grad_std,
			'minmax' : grad_minmax
			}
	features = list()
	time,sepWindow,forceWindow = \
		obj.HighResData.GetTimeSepForce()
	nWindows = len(sepWindow)
	timeConst = 8e-5	#Keep this in?
	mFiltering = FilterObj.Filter(timeConst = timeConst)
	if data_type.lower() == 'force':
		for i,(time,sep,force) in enumerate(zip(timeWindow,sepWindow,forceWindow)):
			filteredForce = mFiltering.FilterDataY(time,force)
			features.append(progs[norm](filteredForce))

	elif data_type.lower() == 'separation':
		for i,(time,sep,force) in enumerate(zip(timeWindow,sepWindow,forceWindow)):
			filteredSep = mFiltering.FilterDataY(time,sep)
			features.append(progs[norm](filteredSep))

	else:
		print "Error: Invalid data type input. Valid inputs are 'force' or 'separation'"
		return

	return features
