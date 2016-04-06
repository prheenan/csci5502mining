# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append("../")

import DataMiningUtil.Caching.PreProcessCacher as Caching
from DataMining._2_PreProcess.PreProcessPlotting import PlotWindowsWithLabels
import PyUtil.CheckpointUtilities as pCheckUtil
from DataMining._4_Learn.NeuralLearner import NeuralLearner


def run(limit=1):
    """
    Runs the main algorithm
    
    Args:

        limit: the number of files we limit ourselves to 
    """
    # get where the raw data and pre-processed data are
    dataBase = "./DataCache/"
    cacheSub = dataBase + "2_ProcessedData/"
    # how many pre-processed objects to use
    limit =1
    # where the (cached) feature maks should go
    featureCache = dataBase + "3_FeatureMask/FeatureMask.pkl"
    # get the feature mask, False means dont force regeneration
    matr = pCheckUtil.getCheckpoint(featureCache,Caching.GetFeatureMask,True,
                                    cacheSub,limit=limit)
    # create the learner
    mLearner = NeuralLearner(matr)
    # get the predictions (binary array for each point)
    predictIdx = mLearner.FitAndPredict()
    predEval = mLearner.Evaluate(predictIdx)
    print(predEval.__dict__)
    # get the *actual* 'gold standard' event labels.
    eventIdx = mLearner.IdxWhereEvent
    toPlot = mLearner.FeatureMask.SepStd
    # find where we predict an event
    eventPredicted = np.where(predictIdx==1)[0]
    plt.plot(toPlot,alpha=0.3,label="Feature")
    plt.plot(eventPredicted,toPlot[eventPredicted],'b.',
             label="Predicted (Neural Network)")
    plt.plot(eventIdx,toPlot[eventIdx],'r.',
             linewidth=3.0,label="Labelled Events")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    run()
