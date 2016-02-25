# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys


class StateDict:
    class EmitObj:
        def __init__(self,startState,func,emitState):
            """
            this is a convenience wrapper for the state dictionary
            
            Args:
                func: function to call before changing state
                emitState: state to change to
            Returns:
                None
            """
            self.startState = startState
            self.func = func
            self.stateToSet = emitState
    def __init__(self,ParamFunctionStateTuples):
        """
        Subclass of model which specializes in high bandwidth data.
        
        Args:
            ParamFunctionStateTuples : tuples of <CurrentState,
            ParamNum,FunctionToCall,StateToSet>
        Returns:
            None
        """
        self.mDict = dict()
        for stateInit,param,func,stateFinal in ParamFunctionStateTuples:
            assert param not in stateInit
            self.mDict[param] = StateDict.EmitObj(stateInit,func,stateFinal)
    def __getitem__(self,index):
        return self.mDict[index]
    def __contains__(self,index):
        return index in self.mDict
    def keys(self):
        return self.mDict.keys()

if __name__ == "__main__":
    run()
