from PySide import QtCore, QtGui
import pyqtgraph

from .central_widget import CentralWidget


class StartAnalysisDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(StartAnalysisDialog, self).__init__(parent=parent)
        self.set_up()
        
    def set_up(self):
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        self.set_up_protein_groups()
        self.set_up_significance()
        self.set_up_cluster()
        self.set_up_go()
        
        # Dialog buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)
        
    def set_up_protein_groups(self):
        group_box = QtGui.QGroupBox('Protein groups')
        self.layout.addWidget(group_box)
        layout = QtGui.QVBoxLayout()
        group_box.setLayout(layout)
        
        # proteinGroups.txt
        pg_layout = QtGui.QHBoxLayout()
        self.pg_path = QtGui.QLineEdit('/home/mochar/Documenten/school/bpsys/data/kum_proteinGroups.txt')
        self.pg_path.setPlaceholderText('proteinGroups.txt')
        browse_button = QtGui.QPushButton('Browse...')
        browse_button.clicked.connect(lambda: self.pg_path.setText(QtGui.QFileDialog.getOpenFileName()[0]))
        pg_layout.addWidget(QtGui.QLabel('proteinGroups.txt'))
        pg_layout.addWidget(self.pg_path)
        pg_layout.addWidget(browse_button)
        layout.addLayout(pg_layout)
        
        # ID regex
        re_layout = QtGui.QHBoxLayout()
        self.id_regex = QtGui.QLineEdit('\|(.+)\|')
        self.id_regex.setPlaceholderText('.*')
        re_layout.addWidget(QtGui.QLabel('ID regex'))
        re_layout.addWidget(self.id_regex)
        layout.addLayout(re_layout)
        
    def set_up_significance(self):
        group_box = QtGui.QGroupBox('Significantie')
        self.layout.addWidget(group_box)
        layout = QtGui.QVBoxLayout()
        group_box.setLayout(layout)
        
        # Radio buttons
        radio_layout = QtGui.QHBoxLayout()
        self.sig_a_radio = QtGui.QRadioButton('Significance-A')
        self.sig_a_radio.clicked.connect(lambda: self.bin_size_edit.setDisabled(True))
        self.sig_b_radio = QtGui.QRadioButton('Significance-B')
        self.sig_b_radio.setChecked(True)
        self.sig_b_radio.clicked.connect(lambda: self.bin_size_edit.setDisabled(False))
        radio_layout.addWidget(self.sig_a_radio)
        radio_layout.addWidget(self.sig_b_radio)
        layout.addLayout(radio_layout)
        
        # Widgets
        form_layout = QtGui.QFormLayout()
        self.p_value_edit = QtGui.QLineEdit('0.05')
        form_layout.addRow('P-value', self.p_value_edit)
        self.bin_size_edit = QtGui.QLineEdit('300')
        form_layout.addRow('Bin size', self.bin_size_edit)
        layout.addLayout(form_layout)
    
    def set_up_go(self):
        group_box = QtGui.QGroupBox('GO Enrichment')
        self.layout.addWidget(group_box)
        layout = QtGui.QVBoxLayout()
        group_box.setLayout(layout)
        
        # GO DAG database
        go_db_layout = QtGui.QHBoxLayout()
        self.go_db_path = QtGui.QLineEdit('/home/mochar/Documenten/school/bpsys/data/go/go-basic.obo')
        browse_button = QtGui.QPushButton('Browse...')
        browse_button.clicked.connect(lambda: self.go_db_path.setText(QtGui.QFileDialog().getOpenFileName()[0]))
        go_db_layout.addWidget(QtGui.QLabel('Database'))
        go_db_layout.addWidget(self.go_db_path)
        go_db_layout.addWidget(browse_button)
        layout.addLayout(go_db_layout)
        
        # Association table uniprot
        ass_layout = QtGui.QHBoxLayout()
        self.ass_path = QtGui.QLineEdit('/home/mochar/Documenten/school/bpsys/data/go/gene_association.goa_human')
        browse_button = QtGui.QPushButton('Browse...')
        browse_button.clicked.connect(lambda: self.ass_path.setText(QtGui.QFileDialog().getOpenFileName()[0]))
        ass_layout.addWidget(QtGui.QLabel('Associations'))
        ass_layout.addWidget(self.ass_path)
        ass_layout.addWidget(browse_button)
        layout.addLayout(ass_layout)
        
        # P-value
        form_layout = QtGui.QFormLayout()
        self.p_value_go_edit = QtGui.QLineEdit('0.05')
        form_layout.addRow('P-value', self.p_value_go_edit)
        self.go_combo = QtGui.QComboBox()
        self.go_combo.addItem('Molecular function')
        self.go_combo.addItem('Biological process')
        self.go_combo.addItem('Cellular component')
        form_layout.addRow('Ontology', self.go_combo)
        layout.addLayout(form_layout)
    
    def set_up_cluster(self):
        group_box = QtGui.QGroupBox('Clusters')
        self.layout.addWidget(group_box)
        layout = QtGui.QVBoxLayout()
        group_box.setLayout(layout)

        form_layout = QtGui.QFormLayout()
        self.linkage_combo = QtGui.QComboBox()
        self.linkage_combo.addItem('average')
        self.linkage_combo.addItem('single')
        self.linkage_combo.addItem('complete')
        self.linkage_combo.addItem('centroid')
        form_layout.addRow('Linkage', self.linkage_combo)
        self.num_clusters_edit = QtGui.QLineEdit('20')
        form_layout.addRow('Aantal', self.num_clusters_edit)
        layout.addLayout(form_layout)
        
    @staticmethod
    def get_parameters(parent, analysis):
        dialog = StartAnalysisDialog(parent)
        result = dialog.exec_()
        analysis.pg_path = dialog.pg_path.text()
        analysis.ass_path = dialog.ass_path.text()
        analysis.id_regex = dialog.id_regex.text()
        analysis.database_path = dialog.go_db_path.text()
        analysis.bin_size = int(dialog.bin_size_edit.text())
        analysis.p_value = float(dialog.p_value_edit.text())
        analysis.p_value_go = float(dialog.p_value_go_edit.text())
        analysis.ontology = dialog.go_combo.currentText()
        analysis.num_clusters = int(dialog.num_clusters_edit.text())
        analysis.linkage = dialog.linkage_combo.currentText()
        return (analysis, result == QtGui.QDialog.Accepted)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, analysis):
        super(MainWindow, self).__init__()
        self.analysis = analysis
        self.set_up()
        
        self.setGeometry(300, 500, 850, 450)
        self.setWindowTitle('Proteomics')
        self.show()
        
        self.start()
        
    def set_up(self):
        self.init_menu()
        self.statusBar().showMessage('Ready')
        
        w = QtGui.QWidget()
        self.setCentralWidget(w)
        
        layout = QtGui.QVBoxLayout()
        w.setLayout(layout)
        
    def init_menu(self):
        menubar = self.menuBar()
        
        # File menu actions
        open_action = QtGui.QAction('Open', self)
        open_action.triggered.connect(self.start)
        
        file_menu = menubar.addMenu('File')
        file_menu.addAction(open_action)

    def start(self):
        self.analysis, ok = StartAnalysisDialog.get_parameters(self, self.analysis)
        if ok:
            self.statusBar().showMessage(':^)')
            central_widget = CentralWidget(self.analysis, self)
            self.setCentralWidget(central_widget)
