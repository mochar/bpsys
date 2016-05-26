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
     

class SignificanceWidget(QtGui.QWidget):
    def __init__(self, analysis, parent):
        super(SignificanceWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        # Scatterplot
        self.scatter_widget = pg.PlotWidget(self)
        self.scatter_widget.setLabel('left', 'Intensity')
        self.scatter_widget.setLabel('bottom', 'Ratio')
        self.scatter_widget.setLogMode(x=True, y=True)
               
        # Tables
        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.setTabPosition(QtGui.QTabWidget.TabPosition.West)
        self.tab_widget.currentChanged.connect(self.on_tab_change)
        for sample in self.analysis.samples:
            columns = ['id', 'protein_ids'] 
            columns += [c for c in self.analysis.protein_groups if c.endswith('_{}'.format(sample))]
            table_view = QtGui.QTableView(self)
            table_view.setModel(PandasModel(self.analysis.protein_groups[columns]))
            self.tab_widget.addTab(table_view, sample)
        layout.addWidget(self.tab_widget)
        
        # Significance
        form_layout = QtGui.QHBoxLayout()
        values_layout = QtGui.QFormLayout()
        label = QtGui.QLabel('<font><p><strong>Significance-B</strong></p></font>')
        self.bin_size_edit = QtGui.QLineEdit('300')
        self.p_value_edit = QtGui.QLineEdit('0.05')
        filter_button = QtGui.QPushButton('Filter')
        # filter_button.clicked.connect(self.filter)
        values_layout.addWidget(label)
        values_layout.addRow('Bin size', self.bin_size_edit)
        values_layout.addRow('P-value cutoff', self.p_value_edit)
        form_layout.addLayout(values_layout)
        form_layout.addWidget(filter_button)
        
        # Plot and significane-B in the same vertical box
        right_layout = QtGui.QVBoxLayout()
        right_layout.addWidget(self.scatter_widget, 3)
        # right_layout.addLayout(form_layout, 1)
        layout.addLayout(right_layout)
        
    def on_tab_change(self, tab_index):
        sample = self.analysis.samples[tab_index]
        self.plot_data(sample)
        
    def plot_data(self, sample):
        self.scatter_widget.clear()
        colors = ('b', 'r', 'y', 'g')
        pgs = self.analysis.protein_groups
        p_column = pgs['p_{}'.format(sample)]
        data = (pgs[p_column > 0.05], pgs[p_column.between(0.01, 0.05)],
                pgs[p_column.between(0.001, 0.01)], pgs[p_column < 0.001])
        for color, points in zip(colors, data):
            self.scatter_widget.plot(
                x=points['ratio_{}'.format(sample)],
                y=points['intensity_{}'.format(sample)],
                pen=None, symbolPen=None, symbolSize=7,
                symbolBrush=color, antialias=False)
        