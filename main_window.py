import math
import re

from PySide import QtCore, QtGui
import pyqtgraph

from central_widget import CentralWidget


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
        
        # ID regex
        self.regex_box = QtGui.QGroupBox('ID regex')
        self.regex_box.setLayout(QtGui.QVBoxLayout())
        self.regex_box.hide()
        regex_layout = QtGui.QHBoxLayout()
        self.regex_box.layout().addLayout(regex_layout)
        self.regex_edit = QtGui.QLineEdit('\|(.+)\|')
        self.regex_edit.setPlaceholderText('Laat leeg als eiwit ID\'s kloppen.')
        update_regex = QtGui.QPushButton('Update')
        update_regex.clicked.connect(self.super_mega_update)
        regex_layout.addWidget(self.regex_edit)
        regex_layout.addWidget(update_regex)
        lists_layout = QtGui.QHBoxLayout()
        self.regex_box.layout().addLayout(lists_layout)
        self.pg_ids = QtGui.QListWidget(self)
        self.pg_ids.currentTextChanged.connect(self.update_regex_list)
        self.protein_ids = QtGui.QListWidget(self)
        lists_layout.addWidget(self.pg_ids, 3)
        lists_layout.addWidget(self.protein_ids, 1)
        self.layout.addWidget(self.regex_box)
        
        # Dialog buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)
        
    def show_protein_ids(self):
        for protein_group in self.analysis.protein_groups.head()['protein_ids'].iteritems():
            QtGui.QListWidgetItem(protein_group[1], self.pg_ids)
            
    def super_mega_update(self):
        protein_ids = ''.join([str(i.text()) for i in self.pg_ids.selectedItems()])
        self.update_regex_list(protein_ids)

    def update_regex_list(self, protein_ids):
        self.protein_ids.clear()
        regex = self.regex_edit.text() or self.analysis.id_regex
        regex = re.compile(regex)
        for protein_id in protein_ids.split(';'):
            putative_id = regex.findall(protein_id)[0]
            QtGui.QListWidgetItem(putative_id, self.protein_ids)
        
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
            self.regex_box.hide()
            self.error_message.setText('Invalid')
            self.error_message.show()
            return
        self.error_message.hide()
        self.samples_box.setEnabled(True)
        self.regex_box.show()
        self.show_samples()
        self.show_protein_ids()
        
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
        analysis.id_regex = dialog.regex_edit.text()
        if dialog.swap_check.isEnabled():
            analysis.swap_replicas()
        return result == QtGui.QDialog.Accepted


class MainWindow(QtGui.QMainWindow):
    def __init__(self, analysis):
        super(MainWindow, self).__init__()
        self.analysis = analysis
        self.set_up()
        
        self.resize(850, 450)
        self.setWindowTitle('Proteomics')
        self.show()
        
        self.start()
        
    def set_up(self):
        self.init_menu()
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
            central_widget = CentralWidget(self.analysis, self)
            self.setCentralWidget(central_widget)
