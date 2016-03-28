# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
from DataMining.DataMiningUtil.Filtering import FilterObj as FilterObj
from DataMining.DataMiningUtil.Filtering.FilterObj\
    import TouchOffObj as TouchOffObj
from CypherReader.ReaderModel.DataCorrection.CorrectionMethods \
    import GetCorrectedFromArrays,GetCorrectionSlices
from CypherReader.ReaderModel.Generic.TimeSepForceObj import TimeSepForceObj
from CypherReader.ReaderModel.Generic.DataObj import DataObj
import copy

class DataStats:
    def __init__(self,dist):
        """
        Args: 
            dist: the distribution we want the summary of
        Returns:
            object with the desired properties
        """
        self.mean = np.mean(dist)
        self.std = np.std(dist)
        self.median = np.median(dist)
        # see:
        #docs.scipy.org/doc/numpy/reference/generated/numpy.percentile.html
        q1,q3 = np.percentile(dist,[25,75])
        self.q1 = q1
        self.q3 = q3
        self.iqr = q3-q1
        self.distMin = min(dist)
        self.distMax = max(dist)


class DistributionSummary:
    """
    Encapsulates a distribution simmary
    """
    def __init__(self,dist):
        self.RawY = DataStats(dist)
        self.GradY = DataStats(np.gradient(dist))

class CurveSummary:
    def __init__(self,
                 ApproachSummary,
                 DwellSummary,
                 RetractSummary):
        """
        Args:
            ApproachSummary: Summary of the distribution of change in *force* in
            the approach (before hitting the surface) of the curve 

            DwellSummary: Summary of the distribution of change in *force* in
            the dwell (after hitting the surface, before leaving) of the curve 

            RetractSummary: Summary of the distribution of change in *force* in
            the retract (after leaving the surface) of the curve 
        """
        self.approach = ApproachSummary
        self.dwell = DwellSummary
        self.retract = RetractSummary
    def __getitem__(self,index):
        if (index == 0):
            return self.approach
        elif (index == 1):
            return self.dwell
        elif (index == 2):
            return self.retract
        assert False , "Only have stats on 3 regions (Approach, dwell, retract)"
        
class ExperimentSummary:
    """
    Summary of the raw data 
    """
    def __init__(self,CurveRaw,CurveCorrected,CurveCorrectedAndFiltered):
        """
        Initialize a summary of all the distributions
        
        Args:
            CurveRaw: the raw data's CurveSummary 
            CurveCorrected: the corrects data's curve summary
            CurveCorrectedAndFiltered : the corrected *and* filtered
            distribution
        """
        self.RawDist = CurveRaw
        self.CorrectedDist = CurveCorrected
        self.CorrectedAndFilteredDist = CurveCorrectedAndFiltered

class SplitInfo:
    def __init__(self,LowTouchoffIdx,HiTouchoffIdx):
        self.TouchoffObjLo = LowTouchoffIdx
        self.TouchoffObjHi = HiTouchoffIdx
        
class CorrectionInfo:
    def __init__(self,SplitBeforeCorrection,SplitAfterCorrection,
                 InterferenceFittingObj,FilterObj):
        """
        Records the steps towards corrections
        
        Args:
            SplitBeforeCorrection : before the correction, where the split 
            between approach, retract, dwell, etc. Instance of TouchOffObj

            SplitAftertCorrection : before the correction, where the split 
            between approach, retract, dwell, etc. Instance of TouchOffObj. 
            May be different, due to 

        """
        self.SplitBeforeCorrection = SplitBeforeCorrection
        self.SplitAfterCorrection = SplitAfterCorrection
        self.FitObj = InterferenceFittingObj
        self.FilterObj = FilterObj

class MetaPreProcInfo:
    def __init__(self,Summary,Correction):
        """
        Constructs object with the meta information associated with a 
        pre-processing step

        Args:
            Summary: CurveSummary object
            Correction: CorrectionInfo object.
        """
        self.Summary = Summary
        self.Correction = Correction
        
class PreProcessInfo:
    def __init__(self,ExpSummary,CorrInfo,dataToRet,originalLo,originalHi):
        """
        Args:
            ExpSummary: instance of experiment summary; tells what it 
            going on globally

            CorrectionInfo: instance of CorrectionInfo

            dataToRet: TimeSepForceObj, which has been corrected as much as
            possible, but *not* filtered

            originalLo : *view* into original low resolution data
           
            originalHi: *view* into original hi resolution data
        """
        self.Meta = MetaPreProcInfo(ExpSummary,CorrInfo)
        self.Data = dataToRet
        self.OriginalLo = originalLo
        self.OriginalHi = originalHi

def GetRegions(TouchoffTimesAndIndex):
    """
    Gets the approach, dwell, and retract Indices from TouchoffTimesAndIndex
    
    Args:
        TouchoffTimesAndIndex: see GetDistributions
    Returns:
        Tuple of *views* into data; approach,dwell,retract
    """
    approachIdx = TouchoffTimesAndIndex.apprIdx
    retrIdx = TouchoffTimesAndIndex.retrIdx
    start  = TouchoffTimesAndIndex.startIdx
    end = TouchoffTimesAndIndex.endIdx
    slices = [slice(TouchoffTimesAndIndex.startIdx,approachIdx,1),
              slice(TouchoffTimesAndIndex.dwellIdxStart,
                    TouchoffTimesAndIndex.dwellIdxEnd,1),
              slice(retrIdx,end,1)]
    return tuple(slices)

def GetDataRegions(TouchoffTimesAndIndex,Data):
    """
    Returns 'Data', grouping into approach, dwell, and retract by using
    TouchoffTimesAndIndex
    
    Args:
        Data: some 1-d array, see  GetDistributions
        TouchoffTimesAndIndex: see GetDistributions
    """
    return [Data[s] for s in GetRegions(TouchoffTimesAndIndex)]
        
def GetDistributions(TouchoffTimesAndIndex,Data):
    """
    Args:
        TouchoffTimesAndIndex: instance of TouchOffObj
        Data: the actual TimeSepForce data object
    """
    mData= GetDataRegions(TouchoffTimesAndIndex,Data.force)
    # get the force data distribution for each region
    mDist = [DistributionSummary(d) for d in mData]
    # return the distribution object...
    return CurveSummary(*mDist)

def GetCorrectionObj(sliceApprCorr,sliceRetrCorr):
    """
    Gets a single post-correction object from the pre-correction and the 
    Correction info objet

    Args:
       sliceApprCorr: approach slice from coffInfo 
       sliceRetrCorr: retraction slice from coffInfo 
    """
    t = None
    half = None
    startStop = lambda x: (x.start,x.stop)
    startIdx = min(startStop(sliceApprCorr))+1
    apprIdx = max(startStop(sliceApprCorr))-1
    retrIdx = min(startStop(sliceRetrCorr))+1
    endIdx =  max(startStop(sliceRetrCorr))-1
    toRet = TouchOffObj(apprTime=t,
                        apprIdx=apprIdx,
                        retrTime=t,
                        retrIdx=retrIdx,
                        halfwayTime=t,
                        halfwayIdx=half,
                        startIdx=startIdx,
                        endIdx=endIdx)
    # move the dwell index 'in'
    toRet.dwellIdxStart += 1
    toRet.dwellIdxEnd -= 1
    return toRet

def GetPostCorrectionObjects(preCorrObjLo,preCorrObjHi,CorrInfo):
    """
    Given the TouchOffObj from GetApproachAndRetractTouchoffTimes, 
    gets the versions of the *correction* touchoff objects, which may be 
    slightly different

    Args:
        preCorrObjLo: FilterObj.TouchOffObj associated with low res before
        the correction.

        preCorrObjHi: FilterObj.TouchOffObj associated with low res after the 
        correction 
        
        CorrInfo: information object from GetCorrectedFromArrays
    returns:
        touchoffobj for the low and hi, respectively
    """
    touchoffObjHi = GetCorrectionObj(CorrInfo.sliceHiAppr,
                                     CorrInfo.sliceHiRetr)
    touchoffObjLo = GetCorrectionObj(CorrInfo.sliceLoAppr,
                                     CorrInfo.sliceLoRetr)
    return touchoffObjLo,touchoffObjHi

    
def PreProcess(LowRes,HiRes,mFiltering):
    """
    Pre-processes data, getting rid of wiggles and time offsets.
    
    Args:
        LowRes: low resolution data, as a TimeSepForce Object (XXX?)
        HiRes: high resolution data, as a TimeSepForce Object (XXX?)
        mFiltering: filtering object to use for pre-processing
    Returns:
        tuple of <PreProcessInfo,correctionObj>, where 'correctionObj'
        is the same low-resolution data, but the high resolution data has
        been corrected, with the wiggles removed
    """
    # Get the low and high resolution indices for the touchoff
    touchoffObjLow = mFiltering.GetApproachAndRetractTouchoffTimes(LowRes)
    touchoffObjHi =  mFiltering.GetApproachAndRetractTouchoffTimes(HiRes)
    # Get the distributions for the high resolution stuff
    hiResDist = GetDistributions(touchoffObjHi,HiRes)
    # Correct the hi resolution curve, using the slices we just made
    sliceLoAppr,sliceHiRetr = GetCorrectionSlices(touchoffObjLow.apprIdx,
                                                  touchoffObjHi.retrIdx)
    # correct everything we can, so get the other pair of slices
    sliceHiAppr,sliceLoRetr = GetCorrectionSlices(touchoffObjHi.apprIdx,
                                                  touchoffObjLow.retrIdx)
    # average the two offsets we found
    timeOffset = ((touchoffObjHi.retrTime-touchoffObjLow.retrTime) +
                  (touchoffObjHi.apprTime-touchoffObjLow.apprTime))/2
    corrSepHi,corrForceHi,corrLowForce,corrInf = \
            GetCorrectedFromArrays(LowRes.time,LowRes.sep,LowRes.force,
                                   HiRes.time ,HiRes.force,
                                   sliceLoAppr,sliceHiRetr,timeOffset,
                                   lowSliceRetr=sliceLoRetr,
                                   hiSliceAppr=sliceHiAppr)

    postLo,postHi = GetPostCorrectionObjects(touchoffObjLow,
                                             touchoffObjHi,
                                             corrInf)
    dataToRet = TimeSepForceObj()
    dataToRet.LowResData = copy.deepcopy(LowRes)
    dataToRet.LowResData.force = corrLowForce
    dataToRet.HiResData = DataObj(HiRes.time,corrSepHi,corrForceHi,LowRes.meta)
    splitPre = SplitInfo(touchoffObjLow,touchoffObjHi)
    splitPost = SplitInfo(postLo,postHi)
    correctionObj = CorrectionInfo(splitPre,splitPost,corrInf,
                                   mFiltering)
    # get the corrected distributions.
    correctedDist = GetDistributions(postHi,dataToRet.HiResData)
    # get the regions corresponding to the approach, dwell, and retract
    mRegions= GetRegions(postHi)
    # get the force data distribution for each filtered region
    filteredRegions = [  mFiltering.FilterDataY(dataToRet.HiResData.time[s],
                                                dataToRet.HiResData.force[s])
                         for s in mRegions]
    # get the filtered and corrected distribution per region
    # note that we filter after splitting into regions, to avoid any
    # weirdness between regions (e.g. 'discontinuous' jumps from dwell to
    # approach after correction)
    filteredDist = [DistributionSummary(region) for region in
                    filteredRegions ]
    filteredAndCorrectDist = CurveSummary(*filteredDist)
    expSummary = ExperimentSummary(hiResDist,correctedDist,
                                   filteredAndCorrectDist)
    # return all the information needed to proceed.
    return PreProcessInfo(expSummary,correctionObj,dataToRet,LowRes,HiRes)

