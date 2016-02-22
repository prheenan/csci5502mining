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
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")

# import the patrick-specific utilities
import GenUtilities  as pGenUtil
import PlotUtilities as pPlotUtil
import CheckpointUtilities as pCheckUtil
import IgorUtil
from ReaderModel.SqlDataModel import SqlBootstrap
from ReaderModel.SqlDataModel import SqlDataModel
from IgorAdapter import BinaryHDF5Io
from PyUtil import SqlUtil
from IgorAdapter import PxpLoader
# Parameter setting (meta and data)
from ReaderModel.Generic import Parameter
# for getting primary keys easily
from sqlalchemy.inspection import inspect
# for getting the high-bandwidth model
from ReaderModel.HighBandwidthFoldUnfold import HighBandwidthModel
from ReaderModel.Generic import Model
# for making an assocWaves object
import argparse
import numpy.random as rand
# import the utilities..
from SqlTestUtil import GetMetaTableOptions,PushAndCheck,GetAllTableRows

def run():
    """
    Function that tests the hookup to the database is working 100%. Nukes the 
    test (ie: debug) schema, tries everything from scratch. Note that this 
    depends on the Cypher converter and reader/writer being Tested 
    (See Demos:PythonReader)

    Tests:
    
    (1) Is binary data saved properly?
    (2) Is the 'user' meta data (e.g. tip type) saved properly?
    (3a) Are the parametrs saved correctly?
    (3b) Are the parameters updated properly, after saving?
    (4a) Is the meta information saved properly?
    (4b) Is the meta information updated properly, after saving?

    Args:
        None

    Returns:
        None
    """
    # # First, we refresh / reload the dataabase, model, and Sql Session
    # nuke and rebuild the debugging database
    debugDataBase = "DebugCypher"
    PathToBootstrap = SqlUtil.SQL_BASE_LOCAL
    databaseStr = PathToBootstrap + debugDataBase
    SqlBootstrap.run()
    # read in data to ship off
    FileToLoad = "./LocalData/ParseWaveTest.pxp"
    data = PxpLoader.LoadPxp(FileToLoad)
    # Create a high bandwidth model 
    TestModel = HighBandwidthModel.HighBandwidthModel()
    # Create all the Sql Meta Parameters
    ParamMeta,_= TestModel.GetParameterMetaInfo()
    # Get the Valid ids for each table
    mSqlObj = SqlUtil.InitSqlGetSessionAndClasses(databaseStr=databaseStr)
    mCls,sess = SqlDataModel.GetClassesAndSess(mSqlObj)
    # get all of the meta IDs, using  sqlalchemy.inspection.inspect
    # in our database, the primary key is just one field.
    getId = lambda x: inspect(x).identity[0]
    # make a dictionary for each tables, for the valid ids...
    metaDict = GetMetaTableOptions(mCls,sess)
    # # next, we create functions to randomize the input.
    # function to shuffle a list and take the first element (effectively
    # random pick).
    shuffleIds = lambda listOfIds : np.random.choice(listOfIds)
    # loop through data, adding parameters and checking they match.
    nToCheck = len(data.keys())
    constr = Parameter.ParameterData
    # function to make an (index,x,y) pair for each parameter (randomized)
    getRandomParam = lambda n : [constr(rand.randint(low=0,high=n),
                                      rand.randn(),rand.rand())
                                 for i in range(n) ]
    getRandomIds = lambda : dict([(key,shuffleIds(val))
                                  for key,val in metaDict.items()])
    maxParams = len(ParamMeta)
    # get a random number of parameters (for testing updating)
    nRandParams = lambda : rand.randint(low=1,high=maxParams)
    # number of updates to try for each datapoint
    nUpdates = 10
    for i,(waveId,assocWaves) in enumerate(data.items()):
        print("Sql Testing {:d}/{:d}".format(i+1,nToCheck))
        mRows = GetAllTableRows(mSqlObj)
        # get the parameteter values, maximum index given here...
        n = 100
        ParamVals = getRandomParam(maxParams)
        # get a random assortment of valid ids to use in pushing
        MetaIds = getRandomIds()
        AssociatedWaveData = Model.WaveDataGroup(assocWaves)
        # push everything
        ModelName = TestModel.ModelName()
        idNameSpaceFirst = PushAndCheck(ModelName,AssociatedWaveData,MetaIds,
                                        ParamMeta,ParamVals,mSqlObj)
        # POST: initial push worked. try re-pushing. First, count how many
        # things are in each table (note: none of these numbers should change)
        # get another random assortment of parameters and meta information to
        # push (but with the same source and model; an *update*)
        for i in range(nUpdates):
            nParams = nRandParams()
            ParamVals = getRandomParam(nParams)
            # get a random assortment of valid ids to use in pushing
            MetaIds = getRandomIds()
            idNameSpaceSecond = PushAndCheck(ModelName,AssociatedWaveData,
                                             MetaIds,ParamMeta,
                                             ParamVals,mSqlObj)
            idsToCheck = [lambda x : x.idTraceMeta,
                          lambda x : x.idTraceData,
                          lambda x : x.idTraceModel]
            for idFunc in idsToCheck:
                orig = idFunc(idNameSpaceFirst)
                new = idFunc(idNameSpaceSecond)
                assert orig == new , "Update incorrectly changed a field."
        ParamVals = getRandomParam(maxParams)
        PushAndCheck(ModelName,AssociatedWaveData,MetaIds,ParamMeta,ParamVals,
                     mSqlObj)
    print("Passed (1) Data Save")
    print("Passed (2) Sql Linker Tables")
    print("Passed (3) Parameter Passing")
    print("Passed (4) Trace Meta ")

if __name__ == "__main__":
    run()

    
