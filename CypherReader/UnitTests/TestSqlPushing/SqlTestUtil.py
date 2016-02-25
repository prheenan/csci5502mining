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
import IgorUtil
from ReaderSqlInterface import MetaParamOpt
import copy
from pyqtgraph.Qt import QtCore, QtGui
from ReaderModel.SqlDataModel import SqlDataModel
from ReaderModel.SqlDataModel import TraceMetaConverter
from UnitTests.TestingUtil.UnitTestUtil import ArrClose
from ReaderController.ControllerEventHandler import EventWindow
from ReaderModel.Generic import Model
from IgorAdapter import BinaryHDF5Io 

def PushAndCheck(ModelName,AssociatedWaveData,MetaIds,ParamMeta,ParamVals,
                 SqlObj):
    """
    Pushes the parameter values and meta information, and checks things are
    consistent

    Args:

        ModelName : The name of the model to use 
        AssociatedWaveData :  associated Model.WaveDataGroup we want to push
        MetaIds : ids associated with all the meta parameters 
        ParamMeta : Meta value for the parameters 
        ParamVals : Expected parameter values (to push). List of ParameterData
        SqlObj : Sql object to use for this session.

    Returns:
        Namespace of Ids used
    """
    idNameSpace = SqlDataModel.PushToDatabase(ModelName,AssociatedWaveData,
                                              MetaIds,ParamMeta,ParamVals,
                                              SqlObj=SqlObj)
    ## POST: data and database should be consistent. 
    ## ensure that the new data is all consistent
    AssertCorrectlyPushed(idNameSpace,AssociatedWaveData,ParamVals,ParamMeta,
                          SqlObj)
    return idNameSpace

def AssertCorrectlyPushed(idNameSpace,AssociatedWaveData,ParamVals,ParamMeta,
                          SqlObj):
    """
    After a push with the given information, queries the database to ensure
    everything is consistent. Assertion error on failure. 

    Args:
        idNameSpace : a namespace with the ids we think we pushed
        AssociatedWaveData : wavedatagroup for the actual data we want
        ParamVals : List of Parameter.ParameterData objects, actual indices etc
        ParamMeta : Parameter.Parameter object, descriptions and the such
        SqlObj : the session object we are using 
    
    Returns:
        None. 
    """
    # Read back in binary data, ensure that it matches the expected data
    try:
        AssertDataSavedCorrectly(AssociatedWaveData)
    except AssertionError as e:
        print(e)
        print("XXX Cannot save data off campus. Must be connected to network." )
    # Linker tables match
    AssertLinkersCorrect(idNameSpace,SqlObj)
    # Check meta information (TraceMeta table) passes what we expect.
    AssertMetaCorrect(idNameSpace,AssociatedWaveData,SqlObj)
    # Parameters match
    AssertParamsCorrect(idNameSpace,ParamVals,ParamMeta,SqlObj)
    
def AssertMetaCorrect(ids,AssociatedWaveData,mSqlObj):
    """
    Tests the TraceMeta table is consistent with what we wanted. 

    Args:
        ids: Namespace (ie argpase.Namespace(**idDict) desired ids for table, 
      
        AssociatedWaveData: The associated waves we want to push

        mSqlObj: the sql object, having the session etc.

    Returns:
        None
    """
    mCls,sess = SqlDataModel.GetClassesAndSess(mSqlObj)
    # get the trace meta table
    metaRow = sess.query(mCls.TraceMeta).filter(mCls.TraceMeta.idTraceMeta ==
                                                ids.idTraceMeta).all()
    assert (len(metaRow) == 1) , "TraceMeta not pushed"
    # POST: exactly only row
    thisRow = metaRow[0]
    # Pick the first note for our meta
    # XXX change to more general?
    MetaNote = AssociatedWaveData.values()[0].Note
    mCols = [str(c).split(".")[1] for c in mCls.TraceMeta.__table__.columns]
    expected = TraceMetaConverter.ConvertToTableObj(mCls,MetaNote,ids.__dict__)
    expectObj = mCls.TraceMeta(**expected)
    for c in mCols:
        SqlVal = getattr(thisRow, c)
        Expect = getattr(expectObj,c)
        if (Expect is None):
            Expect = getattr(ids,c)
        # POST: have the property. try comparing as a numeric first
        try:
            Sql = float(SqlVal)
            Expect = float(Expect)
            # XXX TODO: lower (relative) tolerance, since Invols truncates? 
            assert ArrClose(Sql,Expect) , \
                "Property {:s} doesn't match, {:.7g} vs {:.7g}".\
                format(c,Expect,Sql)
        except (TypeError,ValueError) as e:
            # string or datetime
            assert SqlVal == Expect ,\
                "Property {:s} doesn't match, {:s} vs {:s}".format(c,
                                                                   str(SqlVal),
                                                                   str(Expect))
    
def AssertParamsCorrect(ids,ParamVals,ParamMeta,mSqlObj):
    """
    Tests that the parameter values used are consistent. Specifically

    (0) Are the parameter values and indices correct, in terms of ids and values
    (1) Are the Parameter linkers correct, in terms of ids and values
    (2) Are the correct number of parameters present.

    Args:
        ids: Namespace (ie argpase.Namespace(**idDict) desired ids for table, 
      
        ParamVals: the actual ParamData object, with the x,y, and index 

        ParamMeta: The (ParamVals-Sorted) meta information for each parameter

        mSqlObj: the sql object, having the session etc.

    Returns:
        None
    """
    # determine the ids for the meta parameters, order by parameter number
    mCls,sess = SqlDataModel.GetClassesAndSess(mSqlObj)
    mParams = sess.query(mCls.LinkModelParams).\
              filter(mCls.LinkModelParams.idModel ==ids.idModel).all()
    nParams = len(mParams)
    assert nParams == len(ParamMeta) ,\
        "Wrong number of parameters found [{:d} vs {:d}]".format(nParams,
                                                                 len(ParamVals))
    # POST: correct number of parameters. Are the the correct ID?
    idSql = [p.idParamMeta for p in mParams]
    idMeta = ParamMeta.GetSqlParamIdsModelId(ids.idModel,mSqlObj)
    assert set(idSql) == set(idMeta) ,\
        "Inserted parameters don't match expected"
    # POST: we are all referring to the same parameters.
    # See if we actually inserted anything for this model
    linkParams = sess.query(mCls.LinkTraceParam).\
            filter(mCls.LinkTraceParam.idTraceModel ==ids.idTraceModel).all()
    # exactly the number of parameters we added.
    nParamVals = len(ParamVals)
    nLinks = len(linkParams)
    assert(nLinks == nParamVals) ,\
        "Wrong number of parameters for trace model [{:d} vs {:d}].".\
        format(nParamVals,nLinks)
    # POST: some number of parameters. Get their ids
    idParamVals = [v.idParameterValue for v in linkParams]
    sqlOrderedByNumber = SqlDataModel.\
            GetSqlParamsOrderedByNumber(mSqlObj,ids.idTraceModel,idMeta)
    for pSql,pExpected in zip(sqlOrderedByNumber,ParamVals):
        # check the indices and data value (assumed to be x value!) match
        sqlIdx = float(pSql.DataIndex)
        expIdx = pExpected.index
        # XXX TODO: assert incides are integral?
        assert ArrClose(sqlIdx,int(sqlIdx)), "Index should be integral"
        assert ArrClose(sqlIdx,expIdx), \
            "Sql/Expect indices {:.1f}/{:.1f} don't match".format(sqlIdx,expIdx)
        # POST: indices match. how about x data?
        sqlDataVal = float(pSql.DataValues)
        expDataVal = float(pExpected.x)
        assert ArrClose(pExpected.x,expDataVal) , \
            "Data values don't match ({:.7g},{:.7g})".format(pExpected.x,
                                                             pSql.DataValues)
        # POST: they match. check we have the appropriate linker to the model
        linkTab = mCls.LinkTraceParam
        linkResult = sess.query(linkTab).\
            filter(linkTab.idParameterValue ==pSql.idParameterValue).all()
        assert (len(linkResult) == 1) ,\
            "Expect exactly one link between a parameter and a model"
        # POST: exactly and only one link
        mLink = linkResult[0]
        assert (mLink.idTraceModel == ids.idTraceModel) ,\
            "Wrong trace model associated with linker vable"
        # POST: linker is correct
    
def AssertLinkersCorrect(ids,mSqlObj):
    """
    Tests the ids are all appropriate for the given meta trace and sql obj
    session

    Args:
        ids: Namespace (ie argpase.Namespace(**idDict) desired ids for table, 
      
        mSqlObj: the sql object, having the session etc.

    Returns:
        None
    """
    # get just the 'normal' (number) ids
    mCls,sess = SqlDataModel.GetClassesAndSess(mSqlObj)
    filterFunc = lambda x: x.idTraceMeta == ids.idTraceMeta
    # set up arguments for checkig the linker tables
    # format is (table, id to check)
    tableTest = [(mCls.LinkTipTrace,lambda x: x.idTipType),
                 (mCls.TraceModel,lambda x: x.idModel),
                 (mCls.LinkMoleTrace,lambda x: x.idMolType),
                 (mCls.TraceExpLink,lambda x: x.idExpMeta),
                 # check the trace meta foreign keys
                 (mCls.TraceMeta,lambda x: x.idTipManifest),
                 (mCls.TraceMeta,lambda x: x.idUser),
                 (mCls.TraceMeta,lambda x: x.idTraceRating),
                 (mCls.TraceMeta,lambda x: x.idSample)]
    for tab in tableTest:
        # pass the session, table, and id to check 
        AssertLinkerTableMatches(sess,tab[0],tab[1],filterFunc,ids)

def AssertLinkerTableMatches(sess,sqlTable,checkIdFunc,filterFunc,idList):
    """
    Tests that a row in a table matching a condition has a correct id.Checks:
    (1) Exactly (only!) one row matches
    (2) checkIdFunc(<row in Sql Table>) == checkIdFunc(idList)

    Args:
        sess : The Sql Session to use

        sqlTable : The table we want to query

        checkIdFunc: a function that takes in the table, determines if it is OK

        filterFunc: lambda function used in .filter method to get the row

        idList: a namespace object that checkIdFunc understands. essentially,
        the id from this list should match the id from the other table 
    Returns:
        None
    """
    actualId = sess.query(sqlTable).filter(filterFunc(sqlTable)).all()
    tableName =sqlTable.__table__.name 
    assert actualId is not None , "Linker for [{:s}] not made".format(tableName)
    # POST: row exists. Is it unique? (should be...)
    assert len(actualId) == 1 ,"More than one matching value in table [{:s}]"
    # POST: only one
    assert checkIdFunc(actualId[0]) == checkIdFunc(idList),\
        "id didn't match".format(tableName)
        
def AssertDataSavedCorrectly(AssociatedWaveData):
    """
    Tests the binary file is saved properly. Doesn't check for notes (assumes
    that is OK), but *does* check for data matching.

    Args:
        AssociatedWaveData: a WaveDataGroup object (see Model)

    Returns:
        None
    """
    # make a copy of the wave, to use as meta data...
    WaveMetaData = copy.deepcopy(AssociatedWaveData.values()[0])
    WaveMetaData.SetAsConcatenated()
    SavedFilePath = BinaryHDF5Io.GetFileSaveName(WaveMetaData)
    DataFilePath = IgorUtil.getDatabaseFile(SavedFilePath)
    assert pGenUtil.isfile(DataFilePath) , "File {:s} wasn't saved.".\
        format(DataFilePath)
    # POST: file exists. Hooray! Is it correct?
    readObj = BinaryHDF5Io.LoadHdfFileIntoWaveObj(DataFilePath)
    correctObj = AssociatedWaveData.CreateTimeSepForceWaveObject()
    # note we overload "==" to check that notes *and* data match
    assert (readObj == correctObj) , "File read back in doesn't match."
    # POST: meta data and 'normal' data mach
    
def GetAllTableRows(sqlObj):
    """
    Returns a dictionary, each key is a table, each value is a list of rows
    in the table

    Args:
        None

    Returns:
        None
    """
    allTables = SqlDataModel.GetAllTables(sqlObj)
    toRet = dict()
    mCls,sess = SqlDataModel.GetClassesAndSess(sqlObj)
    for t in allTables:
        toRet[t] = sess.query(t).all()
    return toRet
        

def GetMetaTableOptions(mCls,sess):
    metaDict = dict()
    for func in MetaParamOpt.GetMetaTableFuncs():
        mTab = func(mCls)
        mRows = sess.query(mTab).all()
        # get all of the valid meta rows
        tableName = mTab.__table__.name
        # dont add model (probably not added yet..)
        # XXX add this to bootstrap?
        metaDict[tableName] = [copy.deepcopy(row.__dict__) for row in mRows]
    return metaDict
        
