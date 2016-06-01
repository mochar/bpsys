import time

from PySide import QtCore, QtGui

from .significance_widget import SignificanceWidget
from .go_widget import GOWidget


class AnalysisWorker(QtCore.QObject):
    all_done = QtCore.Signal()
    update_gui = QtCore.Signal()
    update_message = QtCore.Signal(str)
        
    def __init__(self, analysis):
        super(AnalysisWorker, self).__init__()
        self.analysis = analysis

    def run(self):
        self.update_message.emit('Significantie uitvoeren...')
        self.analysis.find_significant()
        self.update_gui.emit()
        self.update_message.emit('GO Enrichment Analyse uitvoeren...')
        start = time.time()
        for i, _ in enumerate(self.analysis.iterate_go_terms()):
            if i % 1000 == 0:
                self.update_gui.emit()
                time.sleep(.01)
        print(time.time() - start)
        self.update_message.emit('KLAAR!!')
        self.all_done.emit()


class CentralWidget(QtGui.QWidget):
    def __init__(self, analysis, parent):
        super(CentralWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.run_thread()
        self.set_up_load()
        
    def run_thread(self):
        self.worker = AnalysisWorker(self.analysis)
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.worker.all_done.connect(self.thread.quit)
        self.worker.update_gui.connect(self.update_gui)
        self.worker.update_message.connect(self.update_statusbar_message)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.done)
        self.thread.start()
        
    def set_up_load(self):
        self.load_gif_screen = QtGui.QLabel()
        self.load_gif_screen.setSizePolicy(QtGui.QSizePolicy.Expanding, 
            QtGui.QSizePolicy.Expanding)        
        self.load_gif_screen.setAlignment(QtCore.Qt.AlignCenter) 
        gif = QtGui.QMovie('gui/loading.gif', QtCore.QByteArray(), self) 
        gif.setCacheMode(QtGui.QMovie.CacheAll) 
        gif.setSpeed(100) 
        self.load_gif_screen.setMovie(gif) 
        gif.start()
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().addWidget(self.load_gif_screen)
    
    def set_up(self):
        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.addTab(SignificanceWidget(self, self.analysis), 'Significantie')
        self.tab_widget.addTab(GOWidget(self, self.analysis), 'GO Enrichment')
        self.tab_widget.addTab(QtGui.QWidget(self), 'Clusters')
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().addWidget(self.tab_widget)
        
    @QtCore.Slot()
    def update_gui(self):
        QtGui.qApp.processEvents()
        
    @QtCore.Slot(str)
    def update_statusbar_message(self, message):
        self.parent().statusBar().showMessage('GO Enrichment Analyse uitvoeren...')
        
    @QtCore.Slot()
    def done(self):
        self.load_gif_screen.deleteLater()
        self.set_up()