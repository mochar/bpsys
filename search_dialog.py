from PySide import QtGui, QtCore


class SearchDialog(QtGui.QDialog):
    def __init__(self, parent, analysis):
        super(SearchDialog, self).__init__(parent)
        self.analysis = analysis
        self.pg_id = None # ID of selected protein group
        self.setWindowTitle('Vind eiwit')
        self.set_up()

    def set_up(self):
        self.setLayout(QtGui.QVBoxLayout())

        # Search bar
        search_layout = QtGui.QHBoxLayout()
        self.search_edit = QtGui.QLineEdit()
        self.search_edit.setPlaceholderText('Eiwit')
        self.search_edit.returnPressed.connect(self.search)
        search_layout.addWidget(self.search_edit)
        self.search_button = QtGui.QPushButton('Zoek')
        self.search_button.clicked.connect(self.search)
        search_layout.addWidget(self.search_button)
        self.layout().addLayout(search_layout)

        # Result table
        self.result_table = QtGui.QTableWidget(1, 1, self)
        self.result_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.result_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.result_table.setHorizontalHeaderLabels(['Protein IDs'])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.clicked.connect(self.select_pg)
        self.layout().addWidget(self.result_table)
        
        # Dialog buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout().addWidget(buttons)
        
    def search(self):
        protein_id = self.search_edit.text()
        pgs = self.analysis.protein_groups
        found = pgs[pgs['protein_ids'].str.contains(protein_id)]
        self.found_pg_ids = [item for _, item in found['id'].iteritems()]
        self.pg_id = self.found_pg_ids[0] if self.found_pg_ids else None
        self.result_table.setRowCount(len(found.index))
        for i, item in enumerate(found['protein_ids'].iteritems()):
            self.result_table.setItem(i, 0, QtGui.QTableWidgetItem(item[1]))
            
    def select_pg(self, index):
        self.pg_id = self.found_pg_ids[index.row()]
            
    @staticmethod
    def get_search_pg_id(parent, analysis):
        dialog = SearchDialog(parent, analysis)
        result = dialog.exec_()
        return (dialog.pg_id, result == QtGui.QDialog.Accepted)
