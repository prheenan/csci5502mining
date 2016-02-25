# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

def change(params, changes):
    """
    Given a pyqtgraph param object associated with part of a table 
    and change object, updates all the parameters (ie: SQL row) for consistency

    Args:
         param: Parameter Object (PyQtGraph) 
         changes: List of tuples describing all changes that have been made in 
         this event: (param, changeDescr, data)
    Returns:
        Nothing
    """
    for param, change, data in changes:
        path = params.childPath(param)
        delim = "."
        if path is not None:
            childName = delim.join(path)
        else:
            childName = param.name()
        # function to get the initial value set used by the dictionary.
        getVal = lambda x: x.opts['values']
        # get the options for this parameter
        mOpt = getVal(param)
        # get which option we are
        mIdx = mOpt.index(data)
        # get the parent (larger table)
        mParent = param.parent()
        # block updates until we are all done (prevent recursion)
        with param.treeChangeBlocker() and mParent.treeChangeBlocker():
        # update all the children to match the index...
            updateOpt = lambda x : x.setValue(getVal(x)[mIdx])
            map(updateOpt,mParent.children())
