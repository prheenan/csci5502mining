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

from sqlalchemy.orm.attributes import manager_of_class
from sqlalchemy.orm.properties import ColumnProperty
import argparse as ap

from decimal import Decimal

# sanitizes input from a database
# XXX add datetime to seconds?
def sanitize(attribute):
    if (type(attribute) is Decimal):
        return float(attribute)
    else:
        return attribute

# from: 
#http://stackoverflow.com/questions/7239873/recreate-some-sqlalchemy-object
# essentialy, we want to serialize some class, turn it into a simple dictionary 
def get_state_dict(instance,name="Generic"):
    cls = type(instance)
    mgr = manager_of_class(cls)
    myDict = dict((key, sanitize(getattr(instance, key)))
                  for key, attr in mgr.iteritems()
                  if isinstance(attr.property, ColumnProperty))
    # next, we convert the dictionary to a 'namespace',
    # which allows us to use dot notation
    # XXX used named tuple instead?
    nameSpace = ap.Namespace(**myDict)
    return nameSpace

def sqlSerialize(instances):
    toRet = []
    try:
        for i in instances:
            toRet.append(get_state_dict(i))
    except TypeError:
        # we were passed a single element
        toRet = get_state_dict(instancs)
    return toRet

