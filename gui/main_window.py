from PySide import QtCore, QtGui
import pyqtgraph

from .central_widget import CentralWidget


class OpenFileDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(OpenFileDialog, self).__init__(parent=parent)
        self.set_up()
        self.show()
        
    def set_up(self):
        # Open proteinGroups.txt layout
        open_layout = QtGui.QHBoxLayout()
        self.file_path = QtGui.QLineEdit('/home/mochar/Documenten/school/bpsys/data/xyz_proteinGroups.txt')
        browse_button = QtGui.QPushButton('Browse...')
        browse_button.clicked.connect(self.show_filebrowser)
        open_layout.addWidget(QtGui.QLabel('proteinGroups.txt'))
        open_layout.addWidget(self.file_path)
        open_layout.addWidget(browse_button)
        
        # Dialog buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # Main layout
        layout = QtGui.QVBoxLayout()
        layout.addLayout(open_layout)
        layout.addWidget(buttons)
        self.setLayout(layout)
        
    def show_filebrowser(self):
        file_path, _ = QtGui.QFileDialog().getOpenFileName(self)
        self.file_path.setText(file_path)
    
    @staticmethod
    def get_file_data(parent):
        dialog = OpenFileDialog(parent)
        result = dialog.exec_()
        file_path = dialog.file_path.text()
        return (file_path, result == QtGui.QDialog.Accepted)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, analysis):
        super(MainWindow, self).__init__()
        self.analysis = analysis
        self.set_up()
        
        self.setGeometry(300, 300, 800, 450)
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
        file_path, ok = OpenFileDialog.get_file_data(self)
        if ok:
            self.statusBar().showMessage(file_path)
            self.analysis.load_data(file_path)
            central_widget = CentralWidget(self.analysis, self)
            self.setCentralWidget(central_widget)