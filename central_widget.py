import time

from PySide import QtCore, QtGui

from significance_widget import SignificanceWidget
from clusters_widget import ClustersWidget
from go_widget import GOWidget
from parameters import Ui_Form
from search_dialog import SearchDialog


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
        self.go_browse.clicked.connect(self.load_go)
        self.ass_browse.clicked.connect(self.load_ass)
        
        self.sig_run.clicked.connect(self.run_sig)
        self.cluster_run.clicked.connect(self.run_cluster)
        self.clust_run_all.clicked.connect(self.clust_run_all_clicked)
        self.go_run.clicked.connect(self.run_go)
        self.go_run_all.clicked.connect(self.go_run_all_clicked)
        
    def load_go(self):
        path, _ = QtGui.QFileDialog().getOpenFileName()
        self.a.database_path = path
        self.go_db_path.setText(path)
        self.db_loaded = False
        
    def load_ass(self):
        path, _ = QtGui.QFileDialog().getOpenFileName()
        self.a.ass_path = path
        self.ass_path.setText(path)
        self.ass_loaded = False
        
    def clust_run_all_clicked(self):
        self.show_load.emit(True)
        self.run_sig(False)
        self.run_cluster(False)
        self.show_load.emit(False)

    def go_run_all_clicked(self):
        self.show_load.emit(True)
        self.run_sig(False)
        self.run_cluster(False)
        self.run_go(False)
        self.show_load.emit(False)

    def run_sig(self, emit=True):
        if emit: self.show_load.emit(True)
        self.cluster_run.setEnabled(True)
        self.go_run.setEnabled(False)
        self.a.p_value = float(self.p_sig_a.text())
        if self.sig_b.isChecked():
            self.a.p_value = float(self.p_sig_b.text())
        self.a.bin_size = int(self.bin_size_edit.text())
        self.a.find_significant()
        self.add_tab.emit(1)
        if emit: self.show_load.emit(False)
        
    def run_cluster(self, emit=True):
        if emit: self.show_load.emit(True)
        self.go_run.setEnabled(True)
        self.a.distance_treshold = float(self.distance_edit.text())
        self.a.linkage = self.linkage_combo.currentText()
        self.a.cluster()
        self.add_tab.emit(2)
        if emit: self.show_load.emit(False)
        
    def run_go(self, emit=True):
        if emit: self.show_load.emit(True)
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
        if emit: self.show_load.emit(False)


class CentralWidget(QtGui.QWidget):
    search_pg = QtCore.Signal(int)

    def __init__(self, analysis, parent):
        super(CentralWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        self.set_up_menu()
        
    def set_up_menu(self):
        menubar = self.parent().menuBar()
        save_menu = menubar.addMenu('Save')
        
        # Save cluster
        self.save_clus_menu = save_menu.addMenu('Cluster')
        self.save_clus_menu.setEnabled(False)
        clus_png_action = QtGui.QAction('Als png', self)
        clus_png_action.triggered.connect(lambda: self.save_figure('png'))
        self.save_clus_menu.addAction(clus_png_action)
        clus_svg_action = QtGui.QAction('Als svg', self)
        clus_svg_action.triggered.connect(lambda: self.save_figure('svg'))
        self.save_clus_menu.addAction(clus_svg_action)

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
        self.corner_widget.hide()
        self.tab_widget.setCornerWidget(self.corner_widget)
        
    def show_load(self, show):
        self.setDisabled(show)
        QtGui.qApp.processEvents()
        
    def tab_changed(self, index):
        self.corner_widget.hide()
        if index == 1:
            self.corner_widget.show()
        
    def search_protein(self):
        pg_id, ok = SearchDialog.get_search_pg_id(self, self.analysis)
        if ok:
            self.search_pg.emit(pg_id)
            
    def save_figure(self, extension):
        file_name, _ = QtGui.QFileDialog.getSaveFileName(self)
        if not file_name.endswith('.{}'.format(extension)):
            file_name = '{}.{}'.format(file_name, extension)
        self.tab_widget.widget(2).fig.savefig(file_name)
        
    def set_tabs(self, i):
        if i == 1:
            self.delete_tab(3)
            self.delete_tab(2)
            self.delete_tab(1)
            self.save_clus_menu.setEnabled(False)
            significance_widget = SignificanceWidget(self, self.analysis)
            self.search_pg.connect(significance_widget.select_pg)
            self.tab_widget.addTab(significance_widget, 'Significantie')
        elif i == 2:
            self.delete_tab(3)
            self.delete_tab(2)
            self.save_clus_menu.setEnabled(True)
            self.tab_widget.addTab(ClustersWidget(self, self.analysis), 'Clusters')
        elif i == 3:
            self.delete_tab(3)
            self.tab_widget.addTab(GOWidget(self, self.analysis), 'GO Enrichment')
        
    def delete_tab(self, i):
        widget = self.tab_widget.widget(i)
        if widget is not None:
            widget.deleteLater()
        self.tab_widget.removeTab(i)
            