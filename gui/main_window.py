import math

from PySide import QtCore, QtGui
import pyqtgraph

from .central_widget import CentralWidget


class LoadProteinGroupsDialog(QtGui.QDialog):
    def __init__(self, parent, analysis):
        super(LoadProteinGroupsDialog, self).__init__(parent=parent)
        self.analysis = analysis
        self.resize(400, 100)
        self.set_up()
        
    def set_up(self):
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        # File selection
        pg_box = QtGui.QGroupBox('proteinGroups.txt')
        pg_box.setLayout(QtGui.QHBoxLayout())
        self.pg_path_edit = QtGui.QLineEdit()
        browse_button = QtGui.QPushButton('Browse...')
        browse_button.clicked.connect(self.load_file)
        pg_box.layout().addWidget(self.pg_path_edit)
        pg_box.layout().addWidget(browse_button)
        self.layout.addWidget(pg_box)
        
        # Error message
        self.error_message = QtGui.QLabel('')
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.error_message.setPalette(palette)
        self.error_message.hide()
        self.layout.addWidget(self.error_message)
        
        # Horizontal line
        line = QtGui.QFrame(self)
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)
        self.layout.addWidget(line)
        
        # Sample names
        samples_layout = QtGui.QHBoxLayout()
        self.layout.addLayout(samples_layout)

        self.samples_box = QtGui.QGroupBox('Samples')
        self.samples_box.setLayout(QtGui.QVBoxLayout())
        samples_layout.addWidget(self.samples_box)
        
        self.replicas_box = QtGui.QGroupBox('Replica\'s')
        self.replicas_box.setLayout(QtGui.QVBoxLayout())
        self.replicas_box.setCheckable(True)
        self.replicas_box.setChecked(False)
        samples_layout.addWidget(self.replicas_box)
        
        self.swap_check = QtGui.QCheckBox('Label swap?')
        self.swap_check.setEnabled(False)
        self.replicas_box.toggled.connect(self.swap_check.setEnabled)
        self.replicas_box.toggled.connect(self.show_samples)
        self.layout.addWidget(self.swap_check)
        
        # Dialog buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)
        
    def empty_layout(self, layout):
        for i in reversed(range(layout.count())): 
            item = layout.takeAt(i)
            widget = item.widget()
            if widget is None:
                self.empty_layout(item.layout())
            else:
                widget.deleteLater()
        
    def load_file(self):
        file_name, _ = QtGui.QFileDialog.getOpenFileName()
        self.pg_path_edit.setText(file_name)
        self.analysis.pg_path = file_name
        try:
            self.analysis.load_data()
        except:
            self.samples_box.setEnabled(False)
            self.error_message.setText('Invalid')
            self.error_message.show()
            return
        self.error_message.hide()
        self.samples_box.setEnabled(True)
        self.show_samples()
        
    def empty(self):
        self.empty_layout(self.samples_box.layout())
        self.empty_layout(self.replicas_box.layout())
        self.sample_combos = []
        self.replica_combos = []
        self.checkboxes = []
        
    def show_samples(self):
        self.empty()
        replicas = self.replicas_box.isChecked()
        num = math.floor(len(self.analysis.samples) / 2) if replicas else len(self.analysis.samples)
        for i in range(num):
            layout = QtGui.QHBoxLayout()
            
            # Check box to activate or deactivate sample + replica
            checkbox = QtGui.QCheckBox()
            checkbox.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred))
            checkbox.setChecked(True)
            self.checkboxes.append(checkbox)
            
            #  Sample box
            sample_combobox = QtGui.QComboBox()
            checkbox.toggled.connect(sample_combobox.setEnabled)
            sample_combobox.addItems(self.analysis.samples)
            sample_combobox.setCurrentIndex(i)
            self.sample_combos.append(sample_combobox)
           
            # Replica box
            replica_combobox = QtGui.QComboBox()
            checkbox.toggled.connect(replica_combobox.setEnabled)
            replica_combobox.addItems(self.analysis.samples)
            if replicas:
                self.replica_combos.append(replica_combobox)
                replica_combobox.setCurrentIndex(i + num)
            else:
                self.sample_combos.append(replica_combobox)
                replica_combobox.setCurrentIndex(i)
            
            layout.addWidget(checkbox)
            layout.addWidget(sample_combobox)
            self.samples_box.layout().addLayout(layout)
            self.replicas_box.layout().addWidget(replica_combobox)
        
    @staticmethod
    def get_file_info(parent, analysis):
        dialog = LoadProteinGroupsDialog(parent, analysis)
        result = dialog.exec_()
        samples = [combo.currentText() for combo in dialog.sample_combos]
        replicas = [combo.currentText() for combo in dialog.replica_combos]
        analysis.samples = [sample for check, sample in zip(dialog.checkboxes, samples) if check.isChecked()]
        analysis.replicas = [replica for check, replica in zip(dialog.checkboxes, replicas) if check.isChecked()]
        return result == QtGui.QDialog.Accepted


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
        ok = LoadProteinGroupsDialog.get_file_info(self, self.analysis)
        if ok:
            self.statusBar().showMessage(':^)')
            central_widget = CentralWidget(self.analysis, self)
            self.setCentralWidget(central_widget)
