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
        self.analysis.find_go_terms()
        self.go_done.emit()


class CentralWidget(QtGui.QWidget):
    def __init__(self, analysis, parent):
        super(CentralWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.run_thread()
        self.set_up()
        self.parent().statusBar().showMessage('Significantie uitvoeren...')
        
    def run_thread(self):
        self.analysis_thread = AnalysisThread(self.analysis)
        self.analysis_thread.significance_done.connect(
            self.update_significance_tab)
        self.analysis_thread.go_done.connect(
            self.update_go_tab)
        self.analysis_thread.finished.connect(self.done)
        self.analysis_thread.start()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        self.tab_widget = QtGui.QTabWidget(self)
        self.sig_widget = SignificanceWidget(self)
        self.tab_widget.addTab(self.sig_widget, 'Significantie')
        self.go_widget = GOWidget(self)
        self.tab_widget.addTab(self.go_widget, 'GO Enrichment')
        self.cluster_widget = QtGui.QWidget(self)
        self.tab_widget.addTab(self.cluster_widget, 'Clusters')
        layout.addWidget(self.tab_widget)
        
    @QtCore.Slot()
    def update_significance_tab(self):
        print('significance setup')
        self.sig_widget.analysis = self.analysis
        self.sig_widget.set_up()
        self.parent().statusBar().showMessage('GO Enrichment Analyse uitvoeren...')
        print('significance done')
        
    @QtCore.Slot()
    def update_go_tab(self):
        print('go setup')
        self.go_widget.analysis = self.analysis
        self.go_widget.set_up()
        self.parent().statusBar().showMessage('Clusters vinden...')
        print('go done')
        
    @QtCore.Slot()
    def done(self):
        self.parent().statusBar().showMessage('KLAAR!!!')