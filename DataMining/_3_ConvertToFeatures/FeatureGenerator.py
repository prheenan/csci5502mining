# force floating point division. Can still use integer with //
from __future__  import division
from FeatureUtils import *
from pFilters import pFeatureGen,ZScoreByDwell,ForceFiltered,CannyFilter,\
    ForwardWaveletTx

class PerWindowFeatureData:
    def __init__(self,FeatureByWindow):
        self.MaxInWindow = [np.max(window) for window in FeatureByWindow]
        self.MinInWindow = [np.min(window) for window in FeatureByWindow]
        


def GetFeatureMatrix(PreProcessedObjects,ListOfFunctions):
    """
    Returns the NxF Matrix, where N is the size of all data in windows of
    PreProcessedObjects, F is number of feature functions in ListOfFunctions

    Args:
        PreProcessedObjects: list of PreProcessedObjects
        ListOfFunctions: each element is a function taking in a single data
        object (with D total window elements) and returning a list of D floats
        (XXX probably a bad idea to go between windows, we will see)
    
    Returns:
        NxF feature matrix
    """
    featuresByWindows = [map(function, PreProcessedObjects)
                         for function in ListOfFunctions]
    feature_matrix = [np.concatenate(feat) for feat in featuresByWindows]
    feature_info = [PerWindowFeatureData(feat[0])
                    for feat in featuresByWindows]
    return feature_matrix,feature_info


class FeatureMask:
    def SetFeature(self,name,idx,matrix,meta):
        featureRow = np.concatenate(matrix[idx][:])
        setattr(self,name,featureRow)
        setattr(self,name+"_Meta",meta[idx])
    def __init__(self,PreProcessedObjects,Labels,FilterConst=400):
        myFuncs = [ lambda obj: featureGen(obj,'force','std',FilterConst),
                    lambda obj: featureGen(obj,'force','minmax',FilterConst),
                    lambda obj: pFeatureGen(obj,CannyFilter,FilterConst),
                    lambda obj: pFeatureGen(obj,ForwardWaveletTx,FilterConst),
                    lambda obj: pFeatureGen(obj,ZScoreByDwell,FilterConst)
                    ]
        matrix,metaInf = GetFeatureMatrix(PreProcessedObjects,myFuncs)
        flattenedByFeatures = [np.concatenate(objectV) for objectV in matrix]
        # Matrix: rows are the feature, columns are the (concatenated 
        Matrix = np.array(flattenedByFeatures)
        # dynamically set the attributes, can get them from self.<Name>
        self.SetFeature("ForceStd",0,matrix,metaInf)
        self.SetFeature("ForceMinMax",1,matrix,metaInf)
        self.SetFeature("CannyFilter",2,matrix,metaInf)
        self.SetFeature("Forward_Wavelet",3,matrix,metaInf)
        self.SetFeature("ForceDwellNormed",4,matrix,metaInf)
        self.N = self.ForceStd.size
        # save out label information
        # raw labels is just a copy of all the labels.
        self._LabelsRaw = Labels
        # now set the array equal to one where we have events
        windows = []
        offset = 0
        for i,obj in enumerate(Labels):
            offsetAdd = 0 if (i == 0) else \
                        sum(f.size
                            for f in PreProcessedObjects[i-1].HiResData.force)
            offset += offsetAdd
            windows.append([np.arange(window.start+offset,
                                      window.end+1+offset,step=1,
                                      dtype=np.int64)
                            for window in obj])
        self.IdxWhereEvent = np.concatenate(np.concatenate(windows))
                
    @property
    def LabelsForAllPoints(self):
        """
        returns a binary matrix of labels for each element in the mask matrix
        """
        LabelsForAllPoints = np.zeros(self.N,dtype=np.int64)
        LabelsForAllPoints[self.IdxWhereEvent] = 1
        return LabelsForAllPoints





