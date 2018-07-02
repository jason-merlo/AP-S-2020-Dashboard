from pyqtgraph.Qt import QtGui, QtCore  

# From Michael Leonard on StackOverflow
class QHLine(QtGui.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtGui.QFrame.HLine)
        self.setFrameShadow(QtGui.QFrame.Sunken)
