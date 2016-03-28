from DataMining._2_PreProcess import PreProcessor as PreProcessor
from DataMining._2_PreProcess import Windowing as Win
from DataMining._2_PreProcess.PreProcessedObject import ProcessedObj


def PreProcessMain(mFiltering,DataObj,UseLowOnly=False):
    """
    Returns a Processed object, giving a data object and way to filter it.

    Args:
         mFiltering: filerning object to use
         DataObject: which object to use. 
         UseLowOnly: For debugging, only use the low resolution data
    Returns:
         tuple of PreProcessingInformation Object (only for debugging/plotting),
         and PreProcessedObject to use downstream
    """
    # get the pre-processing information
    if (UseLowOnly):
        hiRes = DataObj.Data.HiResData
    else:
        hiRes = DataObj.Data.LowResData
    lowRes = DataObj.Data.LowResData
    # set the trigger times to be itdentical.
    hiRes.meta.TriggerTime = lowRes.meta.TriggerTime
    inf = PreProcessor.PreProcess(lowRes,
                                  hiRes,
                                  mFiltering)
    slices,offsets = Win.GetWindowsFromPreprocessed(inf)
    # convert the slices to just start/end pairs
    sliceByPairs = [ [(s.start,s.stop) for s in resolutionList ] \
                     for resolutionList in slices]
    # create the processed objects we care about..
    # XXX faking the labels, need to get them from the database etc.
    inf.Labels = DataObj.Labels
    objInitialize = lambda x: (sliceByPairs[0],sliceByPairs[1],inf.Meta)
    mProc = ProcessedObj(inf,objInitialize)
    return inf,mProc
