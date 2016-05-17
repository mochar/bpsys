from PySide import QtCore, QtGui
import pyqtgraph as pg


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None
     

class CentralWidget(QtGui.QWidget):
    def __init__(self, analysis, parent):
        super(CentralWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        self.plot_data()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        # Table
        self.table_view = QtGui.QTableView(self)
        self.load_table()
        layout.addWidget(self.table_view)
        layout.addWidget(QtGui.QWidget())
        
        # Graph
        self.plot_widget = pg.PlotWidget(self, left='Ratio')
        
        # Significance
        form_layout = QtGui.QHBoxLayout()
        values_layout = QtGui.QFormLayout()
        self.bin_size_edit = QtGui.QLineEdit('300')
        self.p_value_edit = QtGui.QLineEdit('0.05')
        filter_button = QtGui.QPushButton('Filter')
        filter_button.clicked.connect(self.filter)
        values_layout.addRow('Bin size', self.bin_size_edit)
        values_layout.addRow('P-value cutoff', self.p_value_edit)
        form_layout.addLayout(values_layout)
        form_layout.addWidget(filter_button)
        
        # Graph and significane-B in the same vertical box
        right_layout = QtGui.QVBoxLayout()
        right_layout.addWidget(self.plot_widget)
        right_layout.addLayout(form_layout)
        layout.addLayout(right_layout)
        
    def load_table(self):
        self.table_view.setModel(PandasModel(self.analysis.protein_groups))
    
    def plot_data(self):
        ratios = self.analysis.protein_groups[[c for c in self.analysis.protein_groups if c.startswith('log')]]
        colors = ['b', 'r', 'g']
        for column, color in zip(ratios, colors):
            data = self.analysis.protein_groups[column].sort_values()
            plot_item = self.plot_widget.plot(data.values, pen=pg.mkPen(color, width=2))

    def filter(self):
        bin_size = int(self.bin_size_edit.text())
        p_value = float(self.p_value_edit.text())
        self.analysis.find_significant(p_value, bin_size)
        self.load_table()