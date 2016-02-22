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

# Cypher has stupid naming conventions...
Map = {"TimeStarted":"StartTempSeconds",
       'DwellAway':"DwellTime1",
       'DwellTowards':"DwellTime",
       'TimeEnded':"Seconds"}

def ConvertTimeStamp(MacTime):
    import datetime
    d = datetime.datetime.strptime("01-01-1904", "%m-%d-%Y")
    return (d + datetime.timedelta(seconds=MacTime))

def ConvertToTableObj(mCls,Note,MetaIds):
    """
    Converts a given wave note to a dictionary we can use to push SQL data 
    to a table. Also recquires the other associated ids
    
    Args:
        mCls: The Sql Class object we use to determine the columns we need

        Note: The Igor note as a dict, with <name>:<value pairs> (e.g. 
        "ApproachVelocity":1.2e-6)

        MetaIds: A dictionary of <Table>:<id> pairs
    """    
    mTab = mCls.TraceMeta
    table = mTab.__table__
    tableName = table.name
    colObj = table.columns
    # a function to get just the column names (assumed to match the note)
    # we convert the column to a string, split it into <Table>.<field>, then
    # just take the field.
    getColName = lambda x: str(x).split(".")[1]
    colNames = map(getColName,colObj)
    vals = dict()
    # loop through, find where all the columns are.
    for c in colNames:
        withoutId = c[2:]
        if (withoutId == tableName):
            # then this is our id column; pass
            continue
        elif (c in Note):
            # then this is a note property
            vToAdd = Note[c]
        elif (c in MetaIds):
            # this is a 'user meta' property. Skip the first two characters
            # because they should be 'id' (metaIds is the table name)
            vToAdd = MetaIds[c]
        elif (c in Map):
            vToAdd = Note[Map[c]]
        else:
            raise KeyError("Key {:s} not in Wave Note or ids".format(c))
        if ("time" in c.lower()):
            # then this is a timestamp; convert from Cypher format
            vToAdd = ConvertTimeStamp(vToAdd)
        # POST: vToAdd is A-OK
        vals[c] = vToAdd
    # POST: all columns added
    return vals
