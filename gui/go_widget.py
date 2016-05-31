
from PySide import QtCore, QtGui


class GOWidget(QtGui.QWidget):
    def __init__(self, analysis, parent):
        super(GOWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
 
        layout.addWidget(QtGui.QLabel('Go terms'))