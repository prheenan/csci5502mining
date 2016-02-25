# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys

from TestGuiLoading import CypherReaderGUITest
from TestParameterSetting import CypherReaderParamTest
from TestSqlPushing import MainSqlUnitTest
from TestPythonReader import MainUnitTest as MainConverterReaderTest
from TestingUtil import MainUnitUtil

from multiprocessing import Process

def run():
    """
    Runs every unit tests associated with the code. Tests:
    
    (0) General utility function for unit testing (self-consistency)

    (1) Loadng, Saving, and Converting of data 
    (between FEC types, e.g. Sep to Zsnsr and back)

    (2) Gui Loading and setting of view parameters

    (3) Pushing data to the Sql Database (from model down, independent of view)

    Args:
        None

    Returns:
        None
    """
    # make a list of the module unit testers.
    modules = [MainUnitUtil,CypherReaderGUITest,CypherReaderParamTest,
               MainConverterReaderTest,MainSqlUnitTest]
    # create processes for each sub-test
    mProcs = []
    for mod in modules:
        p = Process(target=mod.run)
        mProcs.append(p)
    # start and join them all
    for p in mProcs:
        p.start()
    for p in mProcs:
        p.join()
    # POST: if no errors, unit testing passed.

if __name__ == "__main__":
    run()
