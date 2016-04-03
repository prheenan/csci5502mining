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
import CypherReader.Util.GenUtilities  as pGenUtil
import CypherReader.Util.PlotUtilities as pPlotUtil

from sqlalchemy.sql import select
# import sqlacademy stuff
from sqlalchemy.ext.automap import automap_base # for dynamic class generation
from sqlalchemy.orm import Session # for session generation
from sqlalchemy import create_engine # for creating the engine.
SQL_BASE_LOCAL ='mysql+pymysql://root:@localhost/'
CONNECT_STR = SQL_BASE_LOCAL+'CypherAfm'
DefaultDataDir = '/Volumes/group/4Patrick/PRH_AFM_Databases/BinaryFilesTimeSeparationForce/'
DefaultWorkDir = '/Volumes/group/4Patrick/PrhWorking/'

DnaWlcModel = "DNAWLC"
SurfaceModel = "SurfDetect"

# we need the HDF5 routines  to read in files
import HDF5Util
# We need the sql alchemy bridge for some help functions
from SqlAlchemyBridge import get_state_dict,sqlSerialize

class SqlAlchemyObj:
    def __init__(self,session,engine,mConnStr):
        self._sess = session
        self._engine = engine
        self._dbStr = mConnStr
        self._conn = engine.connect()
    def setCls(self,mClasses):
        self._mCls = mClasses
    # return the connection, class, and session
    def connClassSess(self):
        conn = self._conn
        mCls = self._mCls
        sess = self._sess
        return conn,mCls,sess

def MakeSqlSessionAndEngine(DatabaseStr):
    engine = create_engine(DatabaseStr)
    session = Session(engine)
    return SqlAlchemyObj(session,engine,DatabaseStr)

# function to generate sql classes from a database
def GenerateSqlClasses(mSqlObj):
    # Connection string:
    # http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html
    # automap: http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/automap.html
    # reflect the tables (magic!)
    engine = mSqlObj._engine
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    # this actually works, in that it appears to get the correct classes.
    mCls = Base.classes
    return mCls

# returns the parameters for a file object, given the classes and session
def GetTraceModelId(mSqlObj,fileObj):
    mCls = mSqlObj._mCls
    mSess = mSqlObj._sess
    trMod = mCls.TraceModel
    traceMod = mCls.TraceModel
    mSel = mSess.query(traceMod).\
           filter(traceMod.idTraceMeta == fileObj.idTraceMeta).all()
    return mSel[0].idTraceModel

def GetTraceParams(mSqlObj,fileObj):
    """
    Gets the parameter values and parameter meta associated with a given file

    Args:
        mSqlObj: see GetMeta
        fileObject: see GetMeta
    Returns:
        tuple of parameter values, parameter meta
    """
    conn,mCls,sess = mSqlObj.connClassSess()
    modelId = GetTraceModelId(mSqlObj,fileObj)
    mParams = sess.query(mCls.LinkTraceParam).\
              filter(mCls.LinkTraceParam.idTraceModel == modelId).all()
    mParamIds = [p.idParameterValue for p in mParams]
    ParameterValue = mCls.ParameterValue
    mParamVals = sess.query(ParameterValue)\
                 .filter(ParameterValue.idParameterValue.in_(mParamIds))\
                 .order_by(ParameterValue.idParamMeta).all()
    mMetaIds = [p.idParamMeta for p in mParamVals]
    mParamMeta = sess.query(mCls.ParamMeta)\
                     .filter(mCls.ParamMeta.idParamMeta.in_(mMetaIds))\
                     .order_by(mCls.ParamMeta.idParamMeta).all()
    return mParamVals,mParamMeta

def GetMeta(mSqlObj,fileObj):
    """
    Gets the TraceMeta assoiated with an object with an idTraceMeta field

    Args:
        mSqlObj: sqlobject to use to connect to the database
        fileObject: probably subclass of TraceData, at least has idTraceMeta
        field
    """
    conn,mCls,sess = mSqlObj.connClassSess()
    mTrace = sess.query(mCls.TraceMeta)\
                 .filter(mCls.TraceMeta.idTraceMeta ==
                         fileObj.idTraceMeta).\
                 order_by(mCls.TraceMeta.idTraceMeta).all()
    # XXX assume that there is at least one. Check this?
    return get_state_dict(mTrace[0])
    
# function to get the source name of *every* file to read.
# Is model is not none, only gets files associated with that model
def GetSrcFiles(mSqlObj,ModelName=None):
    # get every file
    session = mSqlObj._sess
    mCls = mSqlObj._mCls
    if (ModelName is not None):
        # get the model we care about
        Models = session.query(mCls.Model)\
                 .filter(mCls.Model.Name == ModelName)\
                 .all()
        # XXX assert this model exists
        myIdModel = Models[0].idModel
        # get all the trace model objects
        mTraceModel = session.query(mCls.TraceModel)\
                             .filter(mCls.TraceModel.idModel == myIdModel).all()
        traceId = [obj.idTraceMeta for obj in mTraceModel]
        mTraceData = session.query(mCls.TraceData)\
                            .filter(mCls.TraceData.idTraceMeta.in_(traceId))\
                            .all()        
    else:
        # get all the tracedata objects with these ids
        mTraceData = session.query(mCls.TraceData).all()
    return mTraceData

def InitSqlGetSessionAndClasses(databaseStr=CONNECT_STR):
    """
    Initializes asql object to the database pointed to by connectStr

    Args:
        databaseStr : string to connect to database
    """
    SqlObj = MakeSqlSessionAndEngine(databaseStr)
    mClasses = GenerateSqlClasses(SqlObj)
    SqlObj.setCls(mClasses)
    return SqlObj

def getModelDataFilesInfo(models,serialize=False,mSqlObj=None):
    '''
    Gets the "TraceData" for each model in models.

    Args:
        models: a single or iterable list of models to get the files for
        serialize : if true, essentially turns the sql object into a dict.
        this is useful for writing to a 'stale' .pkl file 
    '''
    if (mSqlObj is None):
        mSqlObj = InitSqlGetSessionAndClasses()
    toRet = []
    try:
        # loop through each model, get all the files associated
        if (not isinstance(models, basestring)):
            # go to just the single model.
            for m in models:
                mFiles = GetSrcFiles(mSqlObj,ModelName=m)
                if (serialize):
                    mFiles = sqlSerialize(mFiles)
                toRet.append(mFiles)
            return toRet
    except ValueError:
        # passed just a singe value; go to singular
        pass
    toRet = GetSrcFiles(mSqlObj,ModelName=models)
    if (serialize):
        toRet = sqlSerialize(toRet)
    return toRet

# default runner
def run():
    mSqlObj = InitSqlGetSessionAndClasses()
    mFiles = GetSrcFiles(mSqlObj)
    GetTraceParams(mSqlObj,mFiles[0])

if __name__ == '__main__':
    run()
