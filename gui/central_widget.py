import time

from PySide import QtCore, QtGui

from .significance_widget import SignificanceWidget
from .clusters_widget import ClustersWidget
from .go_widget import GOWidget
from .parameters import Ui_Form


class ParametersWidget(QtGui.QWidget, Ui_Form):
    add_tab = QtCore.Signal(int)

    def __init__(self, parent, analysis):
        super(ParametersWidget, self).__init__(parent)
        self.setupUi(self)
        self.a = analysis
        self.db_loaded = False
        self.ass_loaded = False
        self.set_up()
        
    def set_up(self):
        self.go_db_path.setText('/home/mochar/Documenten/school/bpsys/data/go/go-basic.obo')
        self.a.database_path = self.go_db_path.text()
        self.ass_path.setText('/home/mochar/Documenten/school/bpsys/data/go/gene_association.goa_human')
        self.a.ass_path = self.ass_path.text()
        
        self.go_browse.clicked.connect(self.load_go)
        self.ass_browse.clicked.connect(self.load_ass)
        self.sig_run.clicked.connect(self.run_sig)
        self.cluster_run.clicked.connect(self.run_cluster)
        self.go_run.clicked.connect(self.run_go)
        
    def load_go(self):
        path, _ = QtGui.QFileDialog().getOpenFileName()
        self.a.database_path = path
        self.db_loaded = False
        
    def load_ass(self):
        path, _ = QtGui.QFileDialog().getOpenFileName()
        self.a.ass_path = path
        self.ass_loaded = False

    def run_sig(self):
        self.stack.setCurrentIndex(1)
        self.a.p_value = float(self.p_sig_a.text())
        if self.sig_b.isChecked():
            self.a.p_value = float(self.p_sig_b.text())
        self.a.bin_size = int(self.bin_size_edit.text())
        self.a.find_significant()
        self.add_tab.emit(1)
        
    def run_cluster(self):
        self.stack.setCurrentIndex(1)
        self.a.num_clusters = int(self.num_clusters_edit.text())
        self.a.linkage = self.linkage_combo.currentText()
        self.a.cluster()
        self.add_tab.emit(2)
        
    def run_go(self):
        self.stack.setCurrentIndex(1)
        QtGui.qApp.processEvents()
        self.a.p_value_go = float(self.p_value_go_edit.text())
        self.a.ontology = self.go_combo.currentText() 
        if not self.db_loaded:
            self.a.load_go_database()
            QtGui.qApp.processEvents()
            self.db_loaded = True
        if not self.ass_loaded:
            self.a.load_associations()
            QtGui.qApp.processEvents()
            self.ass_loaded = True
        for i, _ in enumerate(self.a.iterate_go_terms()):
            if i % 1000 == 0:
                QtGui.qApp.processEvents()
                time.sleep(.01)
        self.add_tab.emit(3)
                
    def done(self):
        self.stack.setCurrentIndex(0)


class CentralWidget(QtGui.QWidget):
    tabs_done = QtCore.Signal()

    def __init__(self, analysis, parent):
        super(CentralWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        
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
        parameters_widget = ParametersWidget(self, self.analysis)
        parameters_widget.add_tab.connect(self.set_tabs)
        self.tabs_done.connect(parameters_widget.done)
        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.addTab(parameters_widget, 'Parameters')
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().addWidget(self.tab_widget)
        
    def set_tabs(self, i):
        if i == 1:
            self.delete_tab(3)
            self.delete_tab(2)
            self.delete_tab(1)
            self.tab_widget.addTab(SignificanceWidget(self, self.analysis), 'Significantie')
        elif i == 2:
            self.delete_tab(3)
            self.delete_tab(2)
            self.tab_widget.addTab(ClustersWidget(self, self.analysis), 'Clusters')
        elif i == 3:
            self.delete_tab(3)
            self.tab_widget.addTab(GOWidget(self, self.analysis), 'GO Enrichment')
        self.tabs_done.emit()
        
    def delete_tab(self, i):
        widget = self.tab_widget.widget(i)
        if widget is not None:
            widget.deleteLater()
        self.tab_widget.removeTab(i)
            