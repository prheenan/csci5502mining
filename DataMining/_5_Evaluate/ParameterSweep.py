# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

DEF_CONST_FULL = [3,5,8,9,10,11,12,13,16,17,18,19,20,22,25,27,30,35,45,50,\
                  75,100,200]

DEF_CONST = [35,40,45,55,60,70,75,85,100,115,130,150]
from sklearn.cross_validation import KFold
import PyUtil.PlotUtilities as pPlotUtil
from DataMining._3_ConvertToFeatures.FeatureGenerator import FeatureMask

class CrossVal:
    """
    Class for keeping track of cross validation scores
    """
    def __init__(self,TrainingScores,TestScores,FilteringConst):
        self.TrainingScores = TrainingScores
        self.TestScores = TestScores
        self.FilteringConst = FilteringConst
    def GetMeans(self):
        """
        Returns: the means of the training / testing folds
        """
        meanTrain = [np.mean([run.f_score for run in t])
                     for t in self.TrainingScores]
        meanTest  = [np.mean([run.f_score for run in t])
                     for t in self.TestScores]
        return meanTrain,meanTest
    def GetStdevs(self):
        """
        Returns: the standard deviations of the training / testing folds
        """
        stdevTrain = [np.std([run.f_score for run in t])
                     for t in self.TrainingScores]
        stdevTest  = [np.std([run.f_score for run in t])
                     for t in self.TestScores]
        return stdevTrain,stdevTest
        


def GetFittedObj(LearnerToUse,obj,Labels,FilterConst):
    """
    Given a learner, objects, and filtering, gets the fitted learner

    Args:
        LearnerToUse,obj,Labels: see GetEvaluation
        FilterConst: single filtering constant to use
    """
    # create the learner
    mask = FeatureMask(obj,Labels,FilterConst=FilterConst)
    mLearner = LearnerToUse(mask)
    mLearner.Fit(mask)
    return mLearner

def GetEvaluation(obj,Labels,LearnerToUse,FilterConst=DEF_CONST,
                  FoldObj=None):
    """
    Gets the cross-validation scores on the data provided
    
    Args:
        obj: PreProcessedObjects:
        labels: List of labels, same same as obj
        LearnerToUse: class to instatiate the learner, assume it follows same
        construction as Learner

        FilterConst: the filtering constant to use
        FoldObj: the kfold object
    Returns:
        CrossVal, inclluding list of scores
    """
    if (len(obj) == 1):
        print("WARNING!")
        print(("Short-ciricuiting KFold; only using one file;"+
               "not really cross validating"))
        FoldObj = [ [[0],[0]] ]
    if (FoldObj is None):
        # how many object do we have?
        n = len(obj)
        # (k=10)-fold validation, or the n, whichever is smaller
        nFolds = n
        # create the actual folding object.
        FoldObj = KFold(n, n_folds=nFolds,random_state=42,shuffle=True)
    trainingScores = []
    testScores = []
    print("Printing test score as we go.")
    print("\tFilterN\tF_Sco\tPreci.\tRecall")
    for const in FilterConst:
        # set up new training and testing ...
        trainV = []
        testV = []
        for train,test in FoldObj:
            atIndex = lambda x,idx: list([x[i] for i in idx])
            # get the training set
            trainingSet = atIndex(obj,train)
            trainingLabels = atIndex(Labels,train)
            # get the test set
            testSet = atIndex(obj,test)
            testLabels = atIndex(Labels,test)
            trainObj = GetFittedObj(LearnerToUse,trainingSet,trainingLabels,
                                    FilterConst=const)
            # get the score for the training set
            trainPredictions = trainObj.Predict(trainObj.FeatureMask)
            trainEval = trainObj.\
                        Evaluate_Predictions(trainObj.LabelsForAllPoints,
                                             trainPredictions)
            testMask = FeatureMask(testSet,testLabels,FilterConst=const)
            # get the predictions for the test set
            testPredictions = trainObj.Predict(testMask)
            # get the score
            testEval =trainObj.Evaluate_Predictions(testMask.LabelsForAllPoints,
                                                    testPredictions)
            print("TRAIN:\t{:d}\t{:.4f}\t{:.4f}\t{:.4f}".format(
                const,trainEval.f_score,trainEval.precision,trainEval.recall))
            print("TEST:\t{:d}\t{:.4f}\t{:.4f}\t{:.4f}".format(
                const,testEval.f_score,testEval.precision,testEval.recall))
            # record the scores
            trainV.append(trainEval)
            testV.append(testEval)
        trainingScores.append(trainV)
        testScores.append(testV)
    return CrossVal(trainingScores,testScores,FilterConst)

def MakeEvalutionPlot(evalObj,outName):
    """
    Given a cross validation object, makes a plot of the results

    Args:
        evalObj: output of GetEvaluation
        outName: what to save the file as 
    """
    fTraining,fTesting = evalObj.GetMeans()
    stdevTraining,stdevTesting = evalObj.GetStdevs()
    filteringConst = evalObj.FilteringConst
    fig = pPlotUtil.figure()
    ax = plt.subplot(1,1,1)
    plt.errorbar(filteringConst,fTraining,stdevTraining,fmt="bo-",
                 label="Training F Score",linewidth=2.0)
    plt.errorbar(filteringConst,fTesting,stdevTesting,fmt="rx-",
                 label="Testing F Score",linewidth=2.0)
    pPlotUtil.lazyLabel("Filtering Value","Score","",frameon=True)
    ax.set_xscale('log')
    plt.ylim([0,1])
    pPlotUtil.savefig(fig,outName)

def PlotMask(mask,feature1,feature2):
    """
    For deugging. given  mask and two features, plot the split
    """
    plt.figure()
    eventIdx = mask.IdxWhereEvent
    N = mask.N
    nonEventIdx = np.array(list(set(list(np.arange(N,dtype=np.int64))) - \
                                set(eventIdx))).astype(np.int64)
    plt.subplot(4,1,1)
    plt.plot(mask.ForceStd,'b-')
    plt.subplot(4,1,2)
    plt.plot(mask.ForceDwellNormed,'b-')
    plt.plot(eventIdx,mask.ForceDwellNormed[eventIdx],'r.')
    plt.subplot(4,1,3)
    plt.plot(feature2,'r-')
    plt.plot(feature1,'k--')
    plt.plot(eventIdx,feature2[eventIdx],'r.')
    plt.plot(eventIdx,feature1[eventIdx],'k.')
    plt.subplot(4,1,4)
    plt.plot(feature1[eventIdx],feature2[eventIdx],'ro')
    plt.plot(feature1[nonEventIdx],feature2[nonEventIdx],'b,')
    plt.show()
