# force floating point division. Can still use integer with //
from __future__  import division
from FeatureUtils import *

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
    feature_matrix = [np.concatenate(map(function, PreProcessedObjects))
                      for function in ListOfFunctions]
    return feature_matrix

class FeatureMask:

    def __init__(self,PreProcessedObjects,Labels):
        myFuncs = [ lambda obj: featureGen(obj,'separation','std'),
                    lambda obj: featureGen(obj,'separation','minmax'),
                    lambda obj: featureGen(obj,'force','std'),
                    lambda obj: featureGen(obj,'force','minmax')
                    ]
        matrix = GetFeatureMatrix(PreProcessedObjects,myFuncs)
        flattenedByFeatures = [np.concatenate(objectV) for objectV in matrix]
        # Matrix: rows are the feature, columns are the (concatenated 
        Matrix = np.array(flattenedByFeatures)
        self.SepStd = Matrix[0,:]
        self.SepMinMax = Matrix[1,:]
        self.ForceStd = Matrix[2,:]
        self.ForceMinMax = Matrix[3,:]
        self.N = self.SepStd.size
        # save out label information
        # raw labels is just a copy of all the labels.
        self._LabelsRaw = Labels
        # now set the array equal to one where we have events
        self.IdxWhereEvent = np.concatenate([np.arange(l.start,l.end+1,step=1,
                                                       dtype=np.int64)
                                             for obj in Labels for l in obj])
    @property
    def LabelsForAllPoints(self):
        """
        returns a binary matrix of labels for each element in the mask matrix
        """
        LabelsForAllPoints = np.zeros(self.N,dtype=np.int64)
        LabelsForAllPoints[self.IdxWhereEvent] = 1
        return LabelsForAllPoints





