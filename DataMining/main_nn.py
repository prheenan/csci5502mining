# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

# baseDir is where the DataCache folder is 
baseDir = "../"
sys.path.append(baseDir)
import PyUtil.CheckpointUtilities as pCheckUtil
from DataMining._4_Learn.NeuralLearner import NeuralLearner
from DataMining._5_Evaluate.ParameterSweep import GetEvaluation,\
    MakeEvalutionPlot
from DataMiningUtil.Caching import PreProcessCacher as Cacher
from DataMining._5_Evaluate.ParameterSweep import GetEvaluation,\
    MakeEvalutionPlot

def run(limit=3):
    outDir = "./DataCache/4_EvalSweeps/"
    # get where the raw data and pre-processed data are
    obj,Labels = Cacher.ReadProcessedFiles(baseDir,limit=limit)
    evalObj = pCheckUtil.getCheckpoint(outDir + "eval_nn.pkl",
                                       GetEvaluation,True,
                                       obj,Labels,NeuralLearner)
    MakeEvalutionPlot(evalObj,outName=outDir + "nnPlot.png")


if __name__=="__main__":
    run()
