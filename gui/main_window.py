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
        
        self.set_up_files()
        self.set_up_significance()
        self.set_up_go()
        
        # Dialog buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)
        
    def set_up_files(self):
        group_box = QtGui.QGroupBox('Bestanden')
        self.layout.addWidget(group_box)
        layout = QtGui.QVBoxLayout()
        group_box.setLayout(layout)
        
        # proteinGroups.txt
        pg_layout = QtGui.QHBoxLayout()
        self.pg_path = QtGui.QLineEdit('/home/mochar/Documenten/school/bpsys/data/xyz_proteinGroups.txt')
        browse_button = QtGui.QPushButton('Browse...')
        browse_button.clicked.connect(lambda: self.pg_path.setText(QtGui.QFileDialog().getOpenFileName()))
        pg_layout.addWidget(QtGui.QLabel('proteinGroups.txt'))
        pg_layout.addWidget(self.pg_path)
        pg_layout.addWidget(browse_button)
        layout.addLayout(pg_layout)
        
        # Association table uniprot
        ass_layout = QtGui.QHBoxLayout()
        self.ass_path = QtGui.QLineEdit('/home/mochar/Documenten/school/bpsys/data/go/gene_association.goa_human')
        browse_button = QtGui.QPushButton('Browse...')
        browse_button.clicked.connect(lambda: self.ass_path.setText(QtGui.QFileDialog().getOpenFileName()))
        ass_layout.addWidget(QtGui.QLabel('Associations'))
        ass_layout.addWidget(self.ass_path)
        ass_layout.addWidget(browse_button)
        layout.addLayout(ass_layout)
        
    def set_up_significance(self):
        group_box = QtGui.QGroupBox('Significantie')
        self.layout.addWidget(group_box)
        layout = QtGui.QHBoxLayout()
        tab_widget = QtGui.QTabWidget()
        layout.addWidget(tab_widget)
        group_box.setLayout(layout)
        
        # Significance A
        sig_a_widget = QtGui.QWidget()
        sig_a_layout = QtGui.QFormLayout()
        sig_a_widget.setLayout(sig_a_layout)
        
        self.p_value_edit = QtGui.QLineEdit('0.05')
        sig_a_layout.addRow('P-value cutoff', self.p_value_edit)
        
        tab_widget.addTab(sig_a_widget, 'Significance-A')
        
        # Significance B
        sig_b_widget = QtGui.QWidget()
        sig_b_layout = QtGui.QFormLayout()
        sig_b_widget.setLayout(sig_b_layout)
        
        self.bin_size_edit = QtGui.QLineEdit('300')
        sig_b_layout.addRow('Bin size', self.bin_size_edit)
        sig_b_layout.addRow('P-value cutoff', self.p_value_edit)
        
        tab_widget.addTab(sig_b_widget, 'Significance-B')
        
        # Cut-off
        cut_off_widget = QtGui.QWidget()
        tab_widget.addTab(cut_off_widget, 'Cut-off')
    
    def set_up_go(self):
        group_box = QtGui.QGroupBox('GO Enrichment')
        self.layout.addWidget(group_box)
        layout = QtGui.QVBoxLayout()
        group_box.setLayout(layout)
    
    @staticmethod
    def get_parameters(parent):
        dialog = StartAnalysisDialog(parent)
        result = dialog.exec_()
        parameters = {
            'pg_path': dialog.pg_path.text(),
            'ass_path': dialog.ass_path.text(),
            'bin_size': dialog.bin_size_edit.text(),
            'p_value': dialog.p_value_edit.text()
        }
        return (parameters, result == QtGui.QDialog.Accepted)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, analysis):
        super(MainWindow, self).__init__()
        self.analysis = analysis
        self.set_up()
        
        self.setGeometry(300, 300, 850, 450)
        self.setWindowTitle('Proteomics')
        self.show()
        
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
        open_action.triggered.connect(self.load_file)
        
        file_menu = menubar.addMenu('File')
        file_menu.addAction(open_action)

    def load_file(self):
        parameters, ok = StartAnalysisDialog.get_parameters(self)
        if ok:
            self.statusBar().showMessage(parameters['pg_path'])
            self.analysis.load_data(parameters['pg_path'])
            self.analysis.find_significant()
            # self.analysis.load_associations(parameters['ass_path'])
            central_widget = CentralWidget(self.analysis, self)
            self.setCentralWidget(central_widget)