# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
# need to add the utilities class. Want 'home' to be platform independent
from os.path import expanduser
home = expanduser("~")
# get the utilties directory (assume it lives in ~/utilities/python)
# but simple to change
path= home +"/utilities/python"
import sys
sys.path.append(path)
# import the patrick-specific utilities
import GenUtilities  as pGenUtil
import PlotUtilities as pPlotUtil
import CheckpointUtilities as pCheckUtil
# import the Sql Utility...
import PyUtil.SqlUtil as SqlUtil
from PyUtil.SqlAlchemyBridge import get_state_dict

def GetColName(c):
    return str(c).split(".")[1]

class TableOpts:
    def __init__(self,SqlTableObj,Data):
        # get the name name
        self.Name = SqlTableObj.__table__.name
        # get the columns, spliting on the period
        self.Cols = [GetColName(c)
                     for c in SqlTableObj.__table__.columns]
        # get the data as a serialized dictionary (so we can pickle, etc)
        self.Data = Data

def GetMetaTableFuncs():
    return [ lambda x : x.TraceRating,
             lambda x : x.Model,
             lambda x : x.User,
             lambda x : x.TipType,
             lambda x : x.TipManifest,
             lambda x : x.TipPrep,
             lambda x : x.TipPack,
             lambda x : x.Sample,
             lambda x : x.SamplePrep,
             lambda x : x.MoleculeFamily,
             lambda x : x.MolType \
    ]
        
def GetMetaTableOptions():
    """
    Get all of the meta table information, *and* their defaults.

    Args:
         None
    
    Returns:
         A list TableOpts, one for each of the meta tables
    """
    mSqlObj = SqlUtil.InitSqlGetSessionAndClasses()
    # get the session and classes
    session = mSqlObj._sess
    mCls = mSqlObj._mCls
    # get the Sql Object for each meta table
    metaTablesFuncs = GetMetaTableFuncs()
    mDefaults = []
    for mFunc in metaTablesFuncs:
        mTab = mFunc(mCls)
        #XXX assume that  there is exactly 1 primary key, the first col
        primaryCol = list(mTab.__table__.columns)[0]
        data = session.query(mTab).order_by(GetColName(primaryCol)).all()
        newObj = TableOpts(mTab,data)
        mDefaults.append(newObj)
    return mDefaults

if __name__ == "__main__":
    GetMetaTableOptions()
