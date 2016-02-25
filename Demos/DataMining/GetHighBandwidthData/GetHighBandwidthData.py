# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("../../../")

from HighBandwidthUtil import GetLabelledObject


def run():
    """
    Reads in an experiment with hi and low res data, associated meta data,
    and labels. Note that everything revoles around the "LabelledObject"
    
    See:

    DataMining/_1_ReadInDta/DataObject for more information on this
    """
    outPath = "./XNUG2TestData_3512133158_Image1334Concat.hdf"
    data = GetLabelledObject(outPath)
    # print off the meta data (holy spam!)
    print(data.MetaData.__dict__)
    rawDataObj = data.RawData
    lowRes = rawDataObj.LowResData
    hiRes = rawDataObj.HiResData
    # get the labels (locations of start and end for events)
    EventLabels = data.Labels
    #decimate the high resolution data so it isnt impossible to plot
    # itll go from about 13 million points to 100K or so
    deciStep = 130
    hiForce = hiRes.force[::deciStep]
    lowForce = lowRes.force
    # now plot the low and high res data
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(hiRes.time[::deciStep],hiForce,'r,',label="Hi Res")
    plt.plot(lowRes.time,lowForce,'b,',label="Lo Res")
    PlotEvents(hiRes.time,EventLabels)
    plt.legend()
    plt.xlabel("Time (Seconds)")
    plt.ylabel("Force (Newtons)")
    plt.subplot(2,1,2)
    # plot the force versus separation, and 
    plt.plot(hiRes.sep[::deciStep],hiForce,'r,',label="Hi Res")
    plt.plot(lowRes.sep,lowForce,'b,',label="Lo Res")
    PlotEvents(hiRes.sep,EventLabels)
    plt.xlabel("Separation (meters)")
    plt.ylabel("Force (Newtons)")
    plt.legend()
    plt.show()


def PlotEvents(x,LabelIdx):
    """
    Given an x and a list of [start,end] pairs, plots vertical lines

    Args:
        x: the x values to index into
        LabelIdx: list of (start,end) pairs
    """
    for i,(startV,endV) in enumerate(LabelIdx):
        # only label the last event (makes the plot prettier)
        label = "event" if i == (len(LabelIdx)-1) else None
        # just plot the start of the evet
        plt.axvline(x[startV],linestyle='--',label=label)

    
if __name__ == "__main__":
    run()
