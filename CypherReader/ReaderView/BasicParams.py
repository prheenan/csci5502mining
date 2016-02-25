# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree,\
    ParameterItem, registerParameterType


# Methods to get the basic parameters associated with meta data
# that the Cypher can't get.

def PopulateMetaParams(MetaClass):
    # get each table as a separate group
    MetaParams = []
    params = []
    for tableObj in MetaClass:
        # get the name, add each column
        tableName = tableObj.Name
        tmpParams = []
        for i,col in enumerate(tableObj.Cols):
            # get each of the possible options
            mVals = [d.__dict__[col] for d in tableObj.Data]
            # first column is read-only (id)
            isId =(col.lower().startswith('id'))
            # first value it default
            defVal = mVals[0]
            mOpts = {'name':col,'type':'list','values':mVals,'value':defVal,
                     'readonly':isId,'enabled':(not isId),'default':defVal,
                     'visible':(not isId)}
            tmpParams.append(mOpts)
        # make a new subgroup for each table.
        # XXX TODO: defaults?
        newTable = {'name':tableName,'type':'group','children':tmpParams}
        params.append(newTable)
    return params

def MakeParameterTree(params):
    ## Create tree of Parameter objects
    params = Parameter.create(name='params', type='group', children=params)
    tree = ParameterTree()
    tree.setParameters(params, showTop=False)
    return params,tree

    
