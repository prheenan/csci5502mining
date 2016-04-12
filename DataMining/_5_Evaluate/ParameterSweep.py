# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

DEF_CONST = [3,5,8,9,10,11,12,13,16,17,18,19,20,22,25,27,30,35,45,50,\
             75,100,200]

import PyUtil.PlotUtilities as pPlotUtil
from DataMining._3_ConvertToFeatures.FeatureGenerator import FeatureMask

def GetEvaluation(obj,Labels,LearnerToUse,filteringConst=DEF_CONST):
    """

    """
    # Compute the Canny filter for two values of sigma
    toRet = []
    print("FilterN\tF_Sco\tPreci.\tRecall")
    for const in filteringConst:
        mask = FeatureMask(obj,Labels,FilterConst=const)
        # create the learner
        mLearner = LearnerToUse(mask)
        predictIdx = mLearner.FitAndPredict()
        predEval = mLearner.Evaluate(predictIdx)
        print("{:d}\t{:.4f}\t{:.4f}\t{:.4f}".format(
            const,predEval.f_score,predEval.precision,predEval.recall))
        toRet.append(predEval)
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
