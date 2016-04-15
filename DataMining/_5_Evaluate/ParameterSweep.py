# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

DEF_CONST = [3,5,8,9,10,11,12,13,16,17,18,19,20,22,25,27,30,35,45,50,\
             75,100,200]

from sklearn.cross_validation import KFold
import PyUtil.PlotUtilities as pPlotUtil
from DataMining._3_ConvertToFeatures.FeatureGenerator import FeatureMask

class CrossVal:
    """
    Class for keeping track of cross validation scores
    """
    def __init__(self,TrainingScores,TestScores):
        self.TrainingScores = TrainingScores
        self.TestScores = TestScores

def GetFittedObj(LearnerToUse,obj,Labels,**kwargs):
    # create the learner
    mask = FeatureMask(obj,Labels,**kwargs)
    mLearner = LearnerToUse(mask)
    return mLearner

def Predict(mLearner,Objects):
    predictIdx = mLearner.Predict(Objects)
    predEval = mLearner.Evaluate(predictIdx)
    print("{:d}\t{:.4f}\t{:.4f}\t{:.4f}".format(
        const,predEval.f_score,predEval.precision,predEval.recall))
    return predEval

def GetEvaluation(obj,Labels,LearnerToUse,filteringConst=DEF_CONST,
                  FoldObj=None):
    """

    """
    if (FoldObj is None):
        # use 75-25 split, so 3 samples is 2-1
        n = len(obj)
        nFolds = max(2,int(n * 0.75))
        FoldObj = KFold(n, n_folds=nFolds,random_state=42,shuffle=True)
    trainingScores = []
    testScores = [] 
    print("FilterN\tF_Sco\tPreci.\tRecall")
    for const in filteringConst:
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
            print("Training...")
            trainObj = GetFittedObj(LearnerToUse,trainingSet,trainingLabels)
            # get the score for the training set
            trainPred = Predict(trainObj,trainingLabels)
            trainEval = trainObj.Evaluate_Predictions(trainingLabels,
                                                      trainPred)

            # get the predictions for the test set
            testPredictions = trainObj.Predict(testSet)
            # get the score
            print("Testing...")
            testEval =trainObj.Evaluate_Predictions(testLabels,testPredictions)
            # record the scores
            trainV.append(trainEval)
            testV.append(testEval)
        trainingScores.append(trainV)
        testScores.append(testV)
    return toRet

def MakeEvalutionPlot(evalObj,outName,filteringConst=DEF_CONST):
    fScores = [e.f_score for e in evalObj]
    recall = [e.recall for e in evalObj]
    precision = [e.precision for e in evalObj]
    roc_scores = [e.roc_auc_score for e in evalObj]
    fig = pPlotUtil.figure()
    ax = plt.subplot(2,1,1)
    plt.plot(filteringConst,fScores,label="F Score",linewidth=2.0)
    plt.plot(filteringConst,recall,label="Recall",linestyle="--")
    plt.plot(filteringConst,precision,label="Precision",linestyle="-.")
    pPlotUtil.lazyLabel("Filtering Value","Score","",frameon=True)
    plt.ylim([0,1])
    #ax.set_xscale("log")
    ax2 = plt.subplot(2,1,2)
    plt.plot(filteringConst,roc_scores,'ro-',label="AUC / ROC")
    pPlotUtil.lazyLabel("Filtering Value","Score","",frameon=True)
    #ax2.set_xscale("log")
    plt.ylim([0,1])
    pPlotUtil.savefig(fig,outName)
