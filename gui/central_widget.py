from PySide import QtCore, QtGui

from .significance_widget import SignificanceWidget
from .go_widget import GOWidget


class AnalysisThread(QtCore.QThread):
    significance_done = QtCore.Signal()
    go_done = QtCore.Signal()
        
    def __init__(self, analysis):
        super(AnalysisThread, self).__init__()
        self.analysis = analysis

    def __del__(self):
        self.wait()

    def run(self):
        self.analysis.find_significant()
        self.significance_done.emit()
        self.go_done.emit()


class CentralWidget(QtGui.QWidget):
    def __init__(self, analysis, parent):
        super(CentralWidget, self).__init__(parent=parent)
        self.set_up()
        
        self.analysis_thread = AnalysisThread(analysis)
        self.analysis_thread.significance_done.connect(
            self.set_significance_tab)
        self.analysis_thread.go_done.connect(
            self.set_go_tab)
        self.analysis_thread.finished.connect(self.done)
        self.analysis_thread.start()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.addTab(QtGui.QWidget(self), QtGui.QIcon('loading.gif'), 'Significantie')
        self.tab_widget.addTab(QtGui.QWidget(self), QtGui.QIcon('loading.gif'), 'GO Enrichment')
        self.tab_widget.addTab(QtGui.QWidget(self), QtGui.QIcon('loading.gif'), 'Cluster')
        layout.addWidget(self.tab_widget)
        
    def set_significance_tab(self):
        analysis = self.analysis_thread.analysis
        current_tab = self.tab_widget.tabPosition()
        self.tab_widget.removeTab(0)
        self.tab_widget.insertTab(0, SignificanceWidget(analysis, self), 'Significantie')
            
    def set_go_tab(self):
        analysis = self.analysis_thread.analysis
        self.tab_widget.removeTab(1)
        self.tab_widget.insertTab(1, GOWidget(analysis, self), 'GO Enrichment')
        
    def done(self):
        QtGui.QMessageBox.information(self, 'Klaar!', 'KLAAR!!')