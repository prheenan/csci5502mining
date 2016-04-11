from DataMining._2_PreProcess import PreProcessor as PreProcessor
from DataMining._2_PreProcess import Windowing as Win
from DataMining._2_PreProcess.PreProcessedObject import ProcessedObj

class PreProccessOpt:
    """
    Class to keep track of all options used
    """
    def __init__(self,filterObj,minZ=3,windowTime=5e-3):
        """
        Args:
           filterObj: the DataMiningUtil.FilterObj class to use
           minZ: the minimum z score to start a new event
           windowTime: min length in seconds in either direction around an event
        """
        self.filterObj = filterObj
        self.minZ = minZ
        self.windowTime = windowTime

def PreProcessMain(mOpt,DataObj,UseLowOnly=False):
    """
    Returns a Processed object, giving a data object and way to filter it.

    Args:
         mOpt: filtering options to use
         DataObject: which object to use. 
         UseLowOnly: For debugging, only use the low resolution data
    Returns:
         tuple of PreProcessingInformation Object (only for debugging/plotting),
         and PreProcessedObject to use downstream
    """
    # get the pre-processing information
    if (UseLowOnly):
        hiRes = DataObj.Data.LowResData
    else:
        hiRes = DataObj.Data.HiResData
    DataObj.Data.HiResData = hiRes
    mFiltering = mOpt.filterObj
    lowRes = DataObj.Data.LowResData
    # set the trigger times to be itdentical.
    hiRes.meta.TriggerTime = lowRes.meta.TriggerTime
    inf = PreProcessor.PreProcess(lowRes,
                                  hiRes,
                                  mFiltering)
    slices,offsets = Win.GetWindowsFromPreprocessed(inf,
                                                    windowTime=mOpt.windowTime,
                                                    minZ=mOpt.minZ)
    # convert the slices to just start/end pairs
    sliceByPairs = [ [(s.start,s.stop) for s in resolutionList ] \
                     for resolutionList in slices]
    # create the processed objects we care about..
    if (DataObj.HasLabels()):
        inf.Labels = DataObj.Labels
    else:
        inf.Labels = None
    objInitialize = lambda x: (sliceByPairs[0],sliceByPairs[1],inf.Meta)
    mProc = ProcessedObj(inf,objInitialize)
    return inf,mProc

    
