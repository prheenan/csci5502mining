# force floating point division. Can still use integer with //
from __future__ import division
import sys
sys.path.append("../")
import ReaderController.Controller
import ReaderModel.HighBandwidthFoldUnfold.HighBandwidthModel as \
    HighBandwidthModel


def run():
    """
    Runs the controller and associated GUI

    Args:
        None
    
    Returns:
        None
    """
    ReaderController.Controller.run(HighBandwidthModel.HighBandwidthModel())

if __name__ == "__main__":
    run()
