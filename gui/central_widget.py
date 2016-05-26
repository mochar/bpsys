from PySide import QtCore, QtGui

from .significance_widget import SignificanceWidget
     

class CentralWidget(QtGui.QWidget):
    def __init__(self, analysis, parent):
        super(CentralWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        tab_widget = QtGui.QTabWidget(self)
        tab_widget.addTab(SignificanceWidget(self.analysis, self), 'Significantie')
        tab_widget.addTab(QtGui.QWidget(self), 'GO Enrichment')
        tab_widget.addTab(QtGui.QWidget(self), 'Cluster')
        layout.addWidget(tab_widget)