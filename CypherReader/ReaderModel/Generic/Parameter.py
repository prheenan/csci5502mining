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
from collections import OrderedDict
import CypherReader.ReaderModel.SqlDataModel.SqlDataModel as SqlDataModel
from CypherReader.UnitTests.TestingUtil.UnitTestUtil import AssertIntegral

class ParameterData:
    def __init__(self,index,x,y):
        AssertIntegral(index)
        # POST: passed an integral index
        self.index = int(index)
        self.x = float(x)
        self.y = float(y)
    def __iter__(self):
        keys = ["x","y","index"]
        for k in keys:
            yield (k,getattr(self,k))
class ParameterMeta:
    def __init__(self):
        pass
        self.mParams = []
        self.ids = []
        self.ParamCount = 0
    def _addParam(self,**kwargs):
        self.mParams.append(dict(**kwargs))
    def AddParamMeta(self,Name,Description="",UnitName="",UnitAbbr="",
                     LeadStr="",Prefix="",
                     IsRepeatable=False,IsPreProcess=False):
        """
        Adds a parameter with the relevant fields
        
        Args:
            See ParamMeta table in SqlAlchemy
        Returns:
            count of the parameter
        """
        self._addParam(
            Name=Name,
            Description=Description,
            UnitName=UnitName,
            UnitAbbr=UnitAbbr,
            LeadStr=LeadStr,
            Prefix=Prefix,
            IsRepeatable=IsRepeatable,
            IsPreProccess=IsPreProcess,
            ParameterNumber=self.ParamCount)
        # increment how many parameters we have
        self.ParamCount += 1
        return self.ParamCount
    def __getitem__(self, k):
        """
        Gets the parameter at index k
        
        Args:
            k :index, less than len(self)
        Returns:
            ParameterData object
        """
        return self.mParams[k]
    def __len__(self):
        """
        Gets the number of parameters
        
        Args:
            None
        Returns:
            integer number of parameters
        """
        return len(self.mParams)
    def GetSqlParamIds(self,ModelRow,SqlObj):
        """
        see: GetSqlParamIdsModelId
        
        Args:
            ModelRow: the SqlAlchemy Model object associated with the model
            SqlObj: The connection object to use
        Returns:
            see GetSqlParamIdsModelId
        """
        idModel = ModelRow.idModel
        return self.GetSqlParamIdsModelId(idModel,SqlObj)
    def GetSqlParamIdsModelId(self,idModel,SqlObj):
        """
        Given a model, returns the ids associated with the parameters.
        If no such parameters exist, creates them. If some but not all, throws
        an error (for now)
        
        Args:
            ModelId: the SqlAlchemy Model id associated with the model
            SqlObj: The connection object to use
        Returns:
            a list of the ids associated with the model. Also selfs 'self.ids'
            to the same list (returned list is a *copy*, not a reference).
        """
        if len(self.ids) == self.ParamCount:
            # no need to do all the query b.s.
            # return a copy of our ids
            return self.ids[:]
        mCls,sess = SqlDataModel.GetClassesAndSess(SqlObj)
        # first, check if there are any models associated with this parameter
        # we may need to over-write this, if the model hasn't been pushed yet.
        self.ids = SqlDataModel.GetParamIdsForModel(idModel,
                                                    SqlObj=SqlObj)
        nParams = self.ParamCount
        nParamsStored = len(self.ids)
        if (nParamsStored == 0):
            # insert everything, get and save their IDs
            self.ids = []
            for p in self.mParams:
                # get just the id from the (full returned) object
                idParamMeta = SqlDataModel.Insert(sess,mCls.ParamMeta(**p)).\
                              idParamMeta
                # add a linker
                link = mCls.LinkModelParams(idModel=idModel,
                                            idParamMeta=idParamMeta)
                SqlDataModel.Insert(sess,link)
                # record the meta parameter id
                self.ids.append(idParamMeta)
            # POST: all ids added
        elif (nParamsStored != nParams):
            # XXX TODO: add the parameters we dont have? nuke and re-insert?
            # essentially parameters have been removed or added..
            # for now, throw up our hands in disgust
            raise ValueError(("Parameter number mismatch; "
                              "{:d} stored, {:d} expected. "+
                              "Model Editing unsupported").format(nParamsStored,
                                                                  nParams))
        else:
            # everything matches; just return the ids. Move along...
            pass
        # POST: 'ids' is set to the ids of the parameters associated with this
        # model, in their proper order
        # return a copy of the list
        return self.ids[:]
