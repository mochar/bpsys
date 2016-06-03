from PySide import QtCore, QtGui


class ClustersWidget(QtGui.QWidget):
    def __init__(self, parent, analysis=None):
        super(ClustersWidget, self).__init__(parent=parent)
        self.analysis = analysis
        if analysis is not None:
            self.set_up()
        
    def set_up(self):
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)