# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

DEF_CONST = [3,5,8,9,10,11,12,13,16,17,18,19,20,22,25,27,30,35,45,50,\
             75,100,200][:4]

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
        meanTrain = [np.mean([run.f_score for run in t])
                     for t in self.TrainingScores]
        meanTest  = [np.mean([run.f_score for run in t])
                     for t in self.TestScores]
        return meanTrain,meanTest
    def GetStdevs(self):
        stdevTrain = [np.std([run.f_score for run in t])
                     for t in self.TrainingScores]
        stdevTest  = [np.std([run.f_score for run in t])
                     for t in self.TestScores]
        return stdevTrain,stdevTest
        


def GetFittedObj(LearnerToUse,obj,Labels,FilterConst):
    # create the learner
    mask = FeatureMask(obj,Labels,FilterConst=FilterConst)
    mLearner = LearnerToUse(mask)
    mLearner.Fit(mask)
    return mLearner

def GetEvaluation(obj,Labels,LearnerToUse,FilterConst=DEF_CONST,
                  FoldObj=None):
    """

    """
    if (len(obj) == 1):
        print("WARNING!")
        print(("Short-ciricuiting KFold; only using one file;"+
               "not really cross validating"))
        FoldObj = [ [[0],[0]] ]
    if (FoldObj is None):
        # use 5-fold validation, or however long if we are smaller.
        n = min(5,len(obj))
        # use 75-25 split, so 3 samples is 2-1
        nFolds = max(3,int(n * 0.75))
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
            atIndex = lambda x,idx: [x[i] for i in idx]
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

def MakeEvalutionPlot(evalObj,outName,filteringConst=DEF_CONST):
    fTraining,fTesting = evalObj.GetMeans()
    stdevTraining,stdevTesting = evalObj.GetStdevs()
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