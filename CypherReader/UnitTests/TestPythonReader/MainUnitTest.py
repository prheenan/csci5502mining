# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("../../../")
sys.path.append("../../")
sys.path.append("../")
import PythonReader,CypherConverter

def run():
    """
    Runs the unit tests for Python Reading PXP files, reading and Writing HDF5.
    Must be connected to the group drive.
    
    Raises:
         Assertion or IO errors

    """
    PythonReader.run()
    print("All Load/Save tests passed.")
    CypherConverter.run()
    print("All Conversion tests passed.")

if __name__ == "__main__":
    run()
