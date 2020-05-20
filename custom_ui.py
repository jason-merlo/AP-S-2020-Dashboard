# -*- coding: utf-8 -*-
"""
Custom UI class.

Currently only implements horizontal line element.

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
"""
from pyqtgraph.Qt import QtGui


# From Michael Leonard on StackOverflow
class QHLine(QtGui.QFrame):
    """Qt horizontal line/divider object."""

    def __init__(self):
        """Create horizontal line."""
        super(QHLine, self).__init__()
        self.setFrameShape(QtGui.QFrame.HLine)
        self.setFrameShadow(QtGui.QFrame.Sunken)
