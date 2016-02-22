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
import IgorUtil
import CheckpointUtilities as pCheckUtil
import PyUtil.SqlUtil as SqlUtil
import PyUtil.HDF5Util as HDF5Util
import copy
import argparse as ap
import TraceMetaConverter
import IgorAdapter.BinaryHDF5Io as BinaryHDF5Io
from sqlalchemy import MetaData,and_
import copy

class TraceObj:
    def __init__(self,MetaIds,WaveObj,ParamVals,ParamIds):
        """
        Args:
        MetaIds: a dict with <table>/<ids> pairs for the The ids for all of the 
        tables associated with the User Meta (e.g User, TipType, etc), 
        as well as the experiment and model
        
        WaveObject: Contains the raw data to save (as DataY) as well as the 
        meta information (ie: wave note). See ProcessSingleWave

        Returns: A newly constructed traceObj
        """

        self.MetaIds = MetaIds
        self.WaveObj = WaveObj
        self.ParamVals = ParamVals
        self.ParamIds = ParamIds
        self.SaveName = BinaryHDF5Io.GetFileSaveName(WaveObj)
        self.idDot = ap.Namespace(**copy.deepcopy(self.MetaIds))

def GetClassesAndSess(mSqlObj):
    """
    Given a (possibly None) sql object from PyUtil.SqlUtil, returns the class
    and session object
    
    Args:
        ModelName: a 
    Returns:
        The associated table dictionary for the Model
    """
    if (mSqlObj is None):
        mSqlObj = SqlUtil.InitSqlGetSessionAndClasses()
    _,mCls,sess = mSqlObj.connClassSess()
    # POST: have a valid session. Get the first valid object (or none, if none)
    return mCls,sess

def InsertOrGetModelId(ModelName,SqlObj,ModelDecscription=""):
    """
    Given a (unique) model name, gets the ID or inserts if it doesn't exist
    
    Args:
        ModelName: the name of the model to insert
        ModelDecscription: The decription of the model
        SqlObj: The sql Object, decribed in PyUtil.SqlUtil
    Returns:
        The associated table dictionary for the Model
    """
    mCls,sess = GetClassesAndSess(SqlObj)
    mTab = mCls.Model
    CondFunc = lambda Model: Model.Name==ModelName
    return InsertToTableBySession(mTab,sess,CondFunc=CondFunc,Name=ModelName,
                                  Description=ModelDecscription)


def InsertOrGetSourceFile(SourceFile,SqlObj,Name=None,Description=""):
    """
    Given a (unique) source file name, gets the ID, inserts if it doesn't exist
    
    Args:
        Source File: the source file
        Description: the description of the source file
        SqlObj: The sql Object, decribed in PyUtil.SqlUtil
    Returns:
        The associated table dictionary for the Source File
    """
    if (Name is None):
        Name = SourceFile
    mCls,sess = GetClassesAndSess(SqlObj)
    mTab = mCls.ExpMeta
    CondFunc = lambda Table: Table.SourceFile==SourceFile
    return InsertToTableBySession(mTab,sess,CondFunc=CondFunc,Name=Name,
                                  Description=Description,SourceFile=SourceFile)
    
def InsertToTableBySession(Table,Session,CondFunc,**kwargs):
    """
    Wrapper for GenInsertReturnRow. 
    
    Args:
        Table : see GenInsertReturnRow
        Session : see GenInsertReturnRow
        CondFunc : see GenInsertReturnRow
        kwargs : what keywords are used to create a new table object
    Returns:
        The associated table dictionary for the Model
    """
    NewRow = lambda Table: Table(**kwargs)
    return GenInsertReturnRow(Table,Session,CondFunc=CondFunc,NewFunc=NewRow) 

def GetParamIdsForModel(idModel,SqlObj):
    """
    Given a model dictionary (with id, name, etc), gets the stored parameters
    associated with it in the database.
    
    Args:
        idModel: id associated with the model we want

        SqlObj: the 'SqlUtil'-style object used for connecting to the database

    Returns:
        The (possibly empty) set of parameter associated with this model. 
    """
    # POST: have the Ids.
    mCls,sess = GetClassesAndSess(SqlObj)
    mParamObj = sess.query(mCls.LinkModelParams).\
                filter(mCls.LinkModelParams.idModel==idModel).all()
    return [o.idParamMeta for o in mParamObj]

def Insert(Session,ToAdd):
    """
    Insert and commit an object to a given session (pushes to the database)
    
    Args:
        Session: The session to use for the insert

        ToAdd: The object to add

    Returns:
        a *frozen* copy of what we added. Includes the id of the inserted object
    """
    # go ahead and add/flush, so we update the id we just inserted
    Session.add(ToAdd)
    Session.flush()
    # POST: id is up to date
    frozenTable= copy.deepcopy(ToAdd)
    Session.commit()
    return frozenTable

def GetSqlParamsOrderedByNumber(SqlObj,idTraceModel,idMeta):
    """
    Returns the sqlAlchemy row objects associated with the given parameters
    
    Args:
        SqlObj: The SqlObjec to use for getting the classes and session

        idTraceModel: The Sql ID of the TraceModel table we want

        idMeta : The meta parameter ids associated with what we care about
    Returns:
        The list of SqlAlchemy ParamVal objects, ordered by paramNumber
    """
    # get the model
    mCls,sess = GetClassesAndSess(SqlObj)
    traceModRow = sess.query(mCls.TraceModel).\
                  filter(mCls.TraceModel.idTraceModel ==idTraceModel).first()
    assert traceModRow is not None , "Couldn't find TraceModel in ParamByNum"
    # POST: row exists. get the model
    idModel = traceModRow.idModel
    #order them by their parameter number, corresponding to the model
    metaTab = mCls.ParamMeta
    assert len(idMeta) > 0 ,  "Zero-length ids"
    mMeta = sess.query(metaTab).filter(metaTab.idParamMeta.in_(idMeta)).\
            order_by(metaTab.ParameterNumber).all()
    # get the inserted parameter values
    idMetaOrdered = [m.idParamMeta for m in mMeta]
    pValTab = mCls.ParameterValue
    linkParams = sess.query(mCls.LinkTraceParam).\
            filter(mCls.LinkTraceParam.idTraceModel ==idTraceModel).all()
    # POST: some number of parameters. Get their ids
    idParamVals = [v.idParameterValue for v in linkParams]
    if len(idParamVals) == 0:
        return []
    paramVals = sess.query(pValTab).\
                filter(pValTab.idParameterValue.in_(idParamVals)).all()
    expectedDict = dict((idMetaTmp,val)
                        for idMetaTmp,val in zip(idMeta,paramVals))
    sqlOrderedByNumber = [expectedDict[pSql.idParamMeta] for pSql in paramVals]
    return sqlOrderedByNumber

def GenInsertReturnRow(Table,Session,CondFunc,NewFunc):
    """
    Inserts a single row into a table
    
    Args:
        Table: table (e.g. mCls.Model, See PyUtil.SqlUtil) to insert into
        session: Session to use for connection
        CondFunc: function of the form f(table), used in .filter() in sqlalchemy
        NewFunc: Function of the form f(table), returns something to insert
    Returns:
        The associated table dictionary for the Model
    """
    ev = Session.query(Table).filter(CondFunc(Table)).first()
    # figure out what the frozen table (eg: "canned" data/id) is.  
    if not ev:
        # add the new object
        ToAdd = NewFunc(Table)
        frozenTable = Insert(Session,ToAdd)
    else:
        frozenTable = copy.deepcopy(ev)
    # return a simpler dictionary, removing the sqlalchmny state objects...    
    toRet = frozenTable
    # push the new object (do this at the end to avoid deallocation of 'toAdd')
    return toRet

def UpdateTrace(TraceObj,SqlObj,TraceDataRow):
    """
    In a single operation, updates an exising trace in the database. Does *not*
    save out the binary file 
    
    Args:
        TraceObj: see SyncTraceWithDatabase
        SqlObj: ibid
        TraceDataRow: the row for the TraceData table for this trace. 

    Returns:
        tuple of <idTraceMeta,idTraceModel>  
    """     
    mCls,sess = GetClassesAndSess(SqlObj)
    idTraceMeta = TraceDataRow.idTraceMeta
    idDot = TraceObj.idDot
    idModel = idDot.idModel
    traceTab = mCls.TraceModel
    row = sess.query(traceTab).\
          filter(and_(traceTab.idModel == idModel,
                      traceTab.idTraceMeta == idTraceMeta)).all()
    assert len(row) == 1 , \
        "Should be exactly one TraceModel associated with curve"
    # POST: exactly one. update?
    row = row[0]
    idTraceModel = row.idTraceModel
    if row.idModel != idModel:
        row.idModel = idModel
        sess.commit()
    # POST: model updated
    # update the trace meta informaton, if needed
    mDict = TraceMetaConverter.ConvertToTableObj(mCls,
                                                 TraceObj.WaveObj.Note,
                                                 TraceObj.MetaIds)
    # get the old travemeta object.
    traceMeta = sess.query(mCls.TraceMeta).\
                filter(mCls.TraceMeta.idTraceMeta == idTraceMeta).first()
    assert traceMeta is not None , "Trace Meta object (Precondition) not found."
    # update the TraceMeta object with all the new values.
    for key,val in mDict.items():
        setattr(traceMeta,key,val)
    sess.commit()
    # POST: everything updated in meta...
    # Go ahead and update the linkers
    mFilter = lambda x: x.idTraceMeta == idTraceMeta
    # go through, update all the tales we need to 
    linkerArgs = [
        (mCls.LinkMoleTrace,'idMolType'),
        (mCls.LinkTipTrace,'idTipType'),
        (mCls.TraceExpLink,'idExpMeta')]
    for table,prop in linkerArgs:
        mRow = sess.query(table).filter(mFilter(table)).first()
        assert mRow is not None , "Linker not found; Precondition failed."
        # POST: row exists
        expectedId = getattr(idDot,prop)
        if (getattr(mRow,prop) != expectedId):
            setattr(mRow,prop,expectedId)
            # commit the linker we just assigned
            sess.commit()
    # POST: all linkers match. fix parameter values
    ParamVals = TraceObj.ParamVals
    ParamIds = TraceObj.ParamIds
    # order the parametrs by their parameter number
    sqlParamVals = GetSqlParamsOrderedByNumber(SqlObj,idTraceModel,ParamIds)
    nSqlParams = len(sqlParamVals)
    nNewParams = len(ParamVals)
    maxLen = min(nSqlParams,nNewParams)
    # update the older parameters
    for SqlVal,NewVal in zip(sqlParamVals[:maxLen],ParamVals[:maxLen]):
        # detrermine if we need to update.
        #XXX TODO: assume we don't care about anything except index and data
        # XXX TODO: assume data value is x.
        if (SqlVal.DataIndex != NewVal.index or
            SqlVal.DataValues != NewVal.x):
            # XXX add in repeats etc.
            SqlVal.DataIndex =  NewVal.index
            SqlVal.DataValues = NewVal.x
            # push the updated values.
            sess.commit()
    # POST: old parameters updated.
    # now: do we need to add new parameters, or remove bad ones?
    if (nSqlParams < nNewParams):
        # then all the new ones (after nSqlParams)
        extraParamVals = ParamVals[nSqlParams:]
        extraParamIds = ParamIds[nSqlParams:]
        PushParameters(SqlObj,extraParamIds,extraParamVals,idTraceModel)
    elif (nNewParams < nSqlParams):
        # then we need to delete the older ones...
        # XXX TODO: assume order still OK...
        [sess.delete(toDel) for toDel in sqlParamVals[nNewParams:]]
    return idTraceMeta,idTraceModel

def PushSourceIfNeeded(ToSave,force=False):
    """
    Pushes a single wave object as a binary file if it doesn't already exist
    (and if force is False). Saves the full note, as well as 'DataY'. 
    
    Args:

         ToSave: Wave object (See ProcessSingleWave) to save out. Most likely,
         this will be a concatenation; columns of (e.g.) time, distance, force

         force: if true, force creates the file

    Returns:
        None  
    """
    # check if the file already exists
    FileName = BinaryHDF5Io.GetFileSaveName(ToSave)
    # get the pull path (to the actual database...)
    FullPath = IgorUtil.getDatabaseFile(FileName)
    if (pGenUtil.isfile(FullPath) and not force):
        # don't do anything
        return
    else:
        # save the file out, using a blank string for the file name
        # (ie: just the folder)
        DatabasePath = IgorUtil.getDatabaseFolder()
        # XXX TODO: check that path exists to file?
        print("XXX File saving disabled while off campus")
        #BinaryHDF5Io.SaveObjectAsHDF5(FolderPath=DatabasePath,WaveObject=ToSave)

def AddTrace(TraceObj,SqlObj):
    """
    In a single operation, adds an exising trace in the database. Does *not*
    save out the binary file
    
    Args:
        TraceObj: see SyncTraceWithDatabase
        SqlObj: ibid

    Returns:
        tuple of <idTraceMeta,idTraceModel,idTraceData>  
    """    
    # add the meta file...
    mCls,sess = GetClassesAndSess(SqlObj)
    mDict = TraceMetaConverter.ConvertToTableObj(mCls,
                                                 TraceObj.WaveObj.Note,
                                                 TraceObj.MetaIds)
    # get a 'namespace' version of the id object.
    idDot = ap.Namespace(**TraceObj.MetaIds)
    # add the trace meta dictionary
    traceMeta = Insert(sess,mCls.TraceMeta(**mDict))
    # add in the associated hooks.
    idTraceMeta = traceMeta.idTraceMeta
    #LinkMoleTrace
    Insert(sess,mCls.LinkMoleTrace(idMolType=idDot.idMolType,
                                   idTraceMeta=idTraceMeta))
    #TraceExpLink
    Insert(sess,mCls.TraceExpLink(idExpMeta=idDot.idExpMeta,
                                  idTraceMeta=idTraceMeta))
    #TraceModel
    TraceModelRow = Insert(sess,mCls.TraceModel(idModel=idDot.idModel,
                                                idTraceMeta=idTraceMeta))
    idDot.idTraceModel=TraceModelRow.idTraceModel
    #Link TipTrace
    Insert(sess,mCls.LinkTipTrace(idTipType=idDot.idTipType,
                                  idTraceMeta=idTraceMeta))
    #Trace Data
    toAdd = mCls.TraceData(FileTimSepFor=TraceObj.SaveName,
                           idExpMeta=idDot.idExpMeta,idTraceMeta=idTraceMeta)
    idTraceData = Insert(sess,toAdd).idTraceData
    #
    # POST: all non-param linkers made
    # Add in parameters
    #
    idTraceModel =idDot.idTraceModel
    PushParameters(SqlObj,TraceObj.ParamIds,TraceObj.ParamVals,idTraceModel)
    # return the ID associated with this.
    return idTraceMeta,idTraceModel,idTraceData


def PushParameters(SqlObj,ParamIds,ParamVals,idTraceModel):
    """
    Gets all of the SqlAlchemy tables associated with the given session

    Args:
        SqlObj: The Sql Object to use for this session. See (eg) 
        GetParamIdsForModel
        
        ParamIds: The numerical (integer) meta ids for the parameters

        ParamVals : The values to insert, as ParameterData objects

        idTraceModel : The id for the trace-model these parameters belong to

    Returns:
        None
    """
    mCls,sess = GetClassesAndSess(SqlObj)
    for paramMetaId,param in zip(ParamIds,ParamVals):
        #Parameter Value
        # XXX TODO: add in other options as needed (ie: strings, etc)
        # we need to cast everything, because sqlAlchemy can't figure it out
        # for us
        mObj = mCls.ParameterValue(DataIndex=param.index,
                                   idParamMeta=paramMetaId,
                                   StrValues=str(param.index),
                                   DataValues=param.x,
                                   RepeatNumber=0)
        frozenTable =Insert(sess,mObj)
        #Link Trace Param
        idParamVal = frozenTable.idParameterValue
        Insert(sess,mCls.LinkTraceParam(idTraceModel=idTraceModel,
                                        idParameterValue=idParamVal))

def GetAllTables(mSqlObj):
    """
    Gets all of the SqlAlchemy tables associated with the given session

    Args:
        SqlObj: The Sql Object to use for this session. See (eg) 
        GetParamIdsForModel
        
    Returns:
        a list of sorted Sql tables
    """
    meta = MetaData()
    # get all the tables
    engine = mSqlObj._engine
    meta.reflect(engine)
    # nuke everything... (remove all data information)
    tables = meta.sorted_tables
    return tables
    
def SyncTraceWithDatabase(TraceObj,SqlObj):
    """
    In a single operation, adds (or updates) a trace to the database. 
    If necessary (ie: if trace never added before), saves out the binary file

    Args:
        TraceObj: Encapsulated data and references for this trace. 
        See TraceObj Description. Note the WaveData should be completely 
        concatenated in the desired order (time, sep, force)

        SqlObj: The Sql Object to use for this session. See (eg) 
        GetParamIdsForModel
        
    Returns:
        None
    """
    # first, determine if this has already been saved.
    mCls,sess = GetClassesAndSess(SqlObj)
    ev = sess.query(mCls.TraceData).\
         filter(mCls.TraceData.FileTimSepFor==TraceObj.SaveName).first()
    # push the raw (binary) data, if it hasn't already been pushed
    PushSourceIfNeeded(ToSave=TraceObj.WaveObj)
    #LinkExpModel
    idDot = TraceObj.idDot 
    idModel= idDot.idModel
    idExpMeta = idDot.idExpMeta
    CondFunc = lambda tab: ( (tab.idModel == idModel) and
                             (tab.idExpMeta == idExpMeta))
    # add in the link between the model and the experiment, if it
    # doesnt already exist.
    InsertToTableBySession(mCls.LinkExpModel,sess,CondFunc,
                           idModel=idModel,idExpMeta=idExpMeta)
    if ev:
        # hooray! this file already exists.
        # XXX TODO: update all the parameters
        idTraceMeta,idTraceModel = UpdateTrace(TraceObj,SqlObj,ev)
        idDot.idTraceData = ev.idTraceData
    else:
        # doesn't already exist. push everything.
        idTraceMeta,idTraceModel,idTraceData = AddTrace(TraceObj,SqlObj)
        idDot.idTraceData = idTraceData
    idDot.idTraceMeta = idTraceMeta
    idDot.idTraceModel = idTraceModel
    return idDot

def PushToDatabase(ModelName,AssociatedWaveData,MetaViewParams,
                   ParameterDescriptions,CurrentParams,SqlObj):
    """
    In a single operation, adds (or updates) a trace to the database. 
    If necessary (ie: if trace never added before), saves out the binary file.
    Essentially a Model-friendly wrapper for  SyncTraceWithDatabase

    Args:
        ModelName: String name of the model to use. Inserted if new.

        AssociatedWaveData: See Model, WaveDataGroup. Includes the dictionary 
        of name:waveobj pairs to insert, Converted to Sep:Force on insert.

        MetaViewParams: a dict of <table>:<ids> associated with the (user) meta 
        information tables

        ParameterDescriptions: the meta information associated with the
        parameters
        
        CurrentParams: The current parameters (vals)associated. sorted to match
        ParameterDescriptions. 

        SqlObj: The connection object to use

    Returns:
        updated id namespace object. For all tables (except parameters)
        calling "NamespaceObject.<tablename>" will give the integer id used 
        for this insert.
    """
    # check that we actualy have data to push
    if (len(AssociatedWaveData) == 0):
        raise ValueError("Nothing to push to database.")
    # POST: something to push
    # Get all of the meta data for the wave (e.g. pulling speed, etc)
    # (XXX assume it is the same for all associated waves)
    WaveNames = AssociatedWaveData.keys()
    WaveData = AssociatedWaveData[WaveNames[0]]
    # convert all the view parameters to ids
    toIdStr = lambda x : ("id" + x)
    allIds = dict([(toIdStr(table),MetaViewParams[table][toIdStr(table)])
                   for table in MetaViewParams])
    # if the source already exists for this model,
    # then we want to *update* everything, not insert again
    ModelData = InsertOrGetModelId(ModelName,SqlObj=SqlObj)
    ModelId = ModelData.idModel
    # tableName is a helper function that gets a table name from a
    # SqlAlchemy object (e.g., that which is returned from a query)
    idName = lambda SqlAlch : toIdStr(SqlAlch.__table__.name)
    # add the model ID
    allIds[idName(ModelData)]=ModelId
    # Get the rows in the database associated with each parameter
    # XXX inefficient use of SqlObj (repeated instantiation). Fix later...
    paramIds = ParameterDescriptions.GetSqlParamIds(ModelRow=ModelData,
                                                    SqlObj=SqlObj)
    # get the name of the file to save the data as
    ConcatWaveData = AssociatedWaveData.CreateTimeSepForceWaveObject()
    SourceFile = BinaryHDF5Io.GetFileSaveName(ConcatWaveData)
    # get the ID associated with the experiment
    Experiment = InsertOrGetSourceFile(SourceFile,SqlObj=SqlObj)
    idExpMeta = Experiment.idExpMeta
    allIds[idName(Experiment)] = idExpMeta
    # Go ahead and concatenate all of the associated waves 
    # XXX TODO deal with high resolution waves?
    # We now have everything needed to push this data to the database:
    # (0) the actual data is in WaveData
    # (1) all meta information needed by TraceMeta is in WaveData.Note
    # (2) all Model information is in ModelData
    # (3) all Parameter information is in paramIds (for meta) and just the
    # parameter values we have saved
    # (4) The many 'user meta' data points (e.g. tip type) are in
    # We now pass all of this information to our SqlModel, which takes
    # care of most of the hairy details. (e.g. linking, etc)
    #  XXX TODO: move most of above to the Sql model?
    mObj = TraceObj(allIds,ConcatWaveData,
                    CurrentParams,paramIds)
    idDot = SyncTraceWithDatabase(mObj,SqlObj=SqlObj)
    idDot.idExpMeta = idExpMeta
    idDot.idModel = ModelId
    return idDot

