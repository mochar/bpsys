
from PySide import QtCore, QtGui


class GOWidget(QtGui.QWidget):
    def __init__(self, analysis, parent):
        super(GOWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
 
        for go_id in self.analysis.go_ids:
            layout.addWidget(QtGui.QLabel(go_id))