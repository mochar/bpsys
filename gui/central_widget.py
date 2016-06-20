import time

from PySide import QtCore, QtGui

from .significance_widget import SignificanceWidget
from .clusters_widget import ClustersWidget
from .go_widget import GOWidget
from .parameters import Ui_Form
from .search_dialog import SearchDialog


class ParametersWidget(QtGui.QWidget, Ui_Form):
    show_load = QtCore.Signal(bool)
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
        self.show_load.emit(True)
        self.cluster_run.setEnabled(True)
        self.go_run.setEnabled(False)
        self.a.p_value = float(self.p_sig_a.text())
        if self.sig_b.isChecked():
            self.a.p_value = float(self.p_sig_b.text())
        self.a.bin_size = int(self.bin_size_edit.text())
        self.a.find_significant()
        self.add_tab.emit(1)
        self.show_load.emit(False)
        
    def run_cluster(self):
        self.show_load.emit(True)
        self.go_run.setEnabled(True)
        self.a.num_clusters = int(self.num_clusters_edit.text())
        self.a.linkage = self.linkage_combo.currentText()
        self.a.cluster()
        self.add_tab.emit(2)
        self.show_load.emit(False)
        
    def run_go(self):
        self.show_load.emit(True)
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
        for _ in self.a.iterate_go_terms():
            QtGui.qApp.processEvents()
        self.add_tab.emit(3)
        self.show_load.emit(False)


class CentralWidget(QtGui.QWidget):
    search_pg = QtCore.Signal(int)

    def __init__(self, analysis, parent):
        super(CentralWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        self.set_up_load()
        
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
        self.load_widget = QtGui.QWidget(self)
        self.load_widget.setLayout(QtGui.QHBoxLayout())
        self.load_widget.hide()
        self.load_widget.layout().addWidget(self.load_gif_screen)
        self.layout().addWidget(self.load_widget)
    
    def set_up(self):
        # Init parameter widget
        parameters_widget = ParametersWidget(self, self.analysis)
        parameters_widget.add_tab.connect(self.set_tabs)
        parameters_widget.show_load.connect(self.show_load)
        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.addTab(parameters_widget, 'Parameters')
        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().addWidget(self.tab_widget)
        
        # Corner search widget
        self.corner_widget = QtGui.QPushButton('Vind eiwit')
        self.corner_widget.clicked.connect(self.search_protein)
        self.tab_widget.setCornerWidget(self.corner_widget)
        
    def show_load(self, show):
        self.tab_widget.setVisible(not show)
        self.load_widget.setVisible(show)
        
    def tab_changed(self, index):
        if index in (0, 2):
            self.corner_widget.hide()
        else:
            self.corner_widget.show()
        
    def search_protein(self):
        pg_id, ok = SearchDialog.get_search_pg_id(self, self.analysis)
        if ok:
            self.search_pg.emit(pg_id)
        
    def set_tabs(self, i):
        if i == 1:
            self.delete_tab(3)
            self.delete_tab(2)
            self.delete_tab(1)
            significance_widget = SignificanceWidget(self, self.analysis)
            self.search_pg.connect(significance_widget.select_pg)
            self.tab_widget.addTab(significance_widget, 'Significantie')
        elif i == 2:
            self.delete_tab(3)
            self.delete_tab(2)
            self.tab_widget.addTab(ClustersWidget(self, self.analysis), 'Clusters')
        elif i == 3:
            self.delete_tab(3)
            self.tab_widget.addTab(GOWidget(self, self.analysis), 'GO Enrichment')
        
    def delete_tab(self, i):
        widget = self.tab_widget.widget(i)
        if widget is not None:
            widget.deleteLater()
        self.tab_widget.removeTab(i)
            