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
import igor
import ProcessSingleWave
import IgorUtil

from pprint import pformat
from igor.binarywave import load as loadibw
from igor.packed import load as loadpxp
from igor.record.wave import WaveRecord

# import the patrick-specific utilities
import GenUtilities  as pGenUtil
import PlotUtilities as pPlotUtil
import CheckpointUtilities as pCheckUtil
import re
import collections


def LoadAllWavesFromPxp(filepath):
    """
    Given a file path to an igor pxp file, loads all waves associated with it

    Args:
        filepath: path to igor pxp file
    
    Returns:
        list of WaveObj (see ParseSingleWave), containing data and metadata
    """
    # XXX use file system to filter?
    records,_ = loadpxp(filepath)
    mWaves = []
    for i,record in enumerate(records):
        # if this is a wave with a proper name, go for it
        if isinstance(record, WaveRecord):
            mWave =record.wave
            # determine if the wave is something we care about
            if (not ProcessSingleWave.ValidName(mWave)):
                continue
            WaveObj = ProcessSingleWave.WaveObj(record=mWave,
                                                SourceFile=filepath)
            mWaves.append(WaveObj)
    return mWaves


def GroupWavesByEnding(WaveObjList,recquiredEndings=None):
    """
    Given a list of waves and (optional) list of endings, groups the waves

    Args:
        WaveObjList: List of wave objects, from LoadAllWavesFromPxp
        recquiredEndings: optional list of endings for grouping
    
    Returns:
        dictionary of lists; each sublist is a 'grouping' of waves by extension
    """
    # get all the names of the wave objects
    names = [o.Name() for o in WaveObjList]
    # assumed waves end with a number, followed by an ending
    # we need to figure out what the endings and numbers are
    digitEndingList = map(ProcessSingleWave.IgorNameRegex,names)
    # first element gives the (assumed unique) ids
    preamble = [ele[0] for ele in digitEndingList]
    ids = [ele[1] for ele in digitEndingList]
    endings = [ele[2] for ele in digitEndingList]
    # following (but we want all, not just duplicates):
#stackoverflow.com/questions/5419204/index-of-duplicates-items-in-a-python-list
    counter=collections.Counter(ids) 
    idSet=[i for i in counter]
    result={}
    for item in idSet:
        result[item]=[i for i,j in enumerate(ids) if j==item]
    # POST: result has waves grouped by ids. Just need to check all
    # the recquired endings are there, if need be
    if (recquiredEndings is not None):
        for key,val in result.items():
            # do everything in lowercase
            mEndings = [endings[i].lower() for i in val]
            for ext in recquiredEndings:
                # if the extension isnt found, give up on the key
                if (ext.lower() not in mEndings):
                    result.pop(key, None)
                    break
    # POST:
    # (1) each key in the result corresponds to a specific ID (with extensions)
    # (2) each value associated with a key is a list of indices
    # Go ahead and group the waves (remember the waves? that's what we care
    # about) into a 'master' dictionary, indexed by their names
    finalList ={}
    for key,val in result.items():
        tmp = {}
        # append each index to this list
        for idx in val:
            tmp[endings[idx].lower()] = WaveObjList[idx]
        finalList[preamble[idx] + key] = tmp
    return finalList
    
def LoadPxp(inFile):
    """
    Convenience Wrapper. Given a pxp file, reads in all data waves and
    groups by common ID

    Args:
        Infile: file to input
    
    Returns:
        dictionary: see GroupWavesByEnding, same output
    """
    mWaves = LoadAllWavesFromPxp(inFile)
    return GroupWavesByEnding(mWaves)
