# force floating point division. Can still use integer with //
from __future__ import division
import ReaderController.Controller


def run():
    """
    Runs the controller and associated GUI

    Args:
        None
    
    Returns:
        None
    """
    ReaderController.Controller.run()

if __name__ == "__main__":
    run()
