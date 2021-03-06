from PySide import QtCore, QtGui


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, protein_groups, sample, max_p=None, parent=None):
        super(PandasModel, self).__init__(parent=parent)

        cols = ['id', 'protein_ids', 'log_ratio_{}'.format(sample),
                'intensity_{}'.format(sample), 'p_{}'.format(sample)]
        data = protein_groups[cols]
        if max_p is not None:
            data = data[data['p_{}'.format(sample)] < max_p]
        data.columns = ['id', 'protein_ids', 'log_ratio', 'intensity', 'p-value']
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.index)

    def columnCount(self, parent=None):
        return 4

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                protein_group = self._data.values[index.row()]
                return str(self._data.values[index.row()][index.column() + 1])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col + 1]
        return None


class GOModel(QtCore.QAbstractTableModel):
    def __init__(self, analysis, parent=None):
        super(GOModel, self).__init__(parent=parent)
        self._data = analysis

    def rowCount(self, parent=None):
        return len(self._data.go_terms)

    def columnCount(self, parent=None):
        return 3

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                terms = list(self._data.go_terms.values())
                term = terms[index.row()]
                col = index.column()
                if col < 2:
                    return str(term[col])
                return str(len(term.proteins))
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return ['GO ID', 'p waarde', 'eiwitten'][col]
        return None


class TreeItem:
    def __init__(self, term):  
        self.term = term


class TreeViewModel(QtCore.QAbstractItemModel):
    def __init__(self, top_term):
        super(TreeViewModel, self).__init__()
        self.root = top_term
        
    def flags(self, index):
        """ Returns the item flags for the given index. """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        
    def data(self, index, role):
        """ Returns the data stored under the given role for the item
        referred to by the index. """
        if not index.isValid():
            return QVariant()
        node = self.nodeFromIndex(index)
        if role == Qt.DisplayRole:
            return QVariant(node.name)
        else:
            return QVariant()
        
    def headerData(self, section, orientation, role):
        """ Returns the data for the given role and section in the header
        with the specified orientation. """
        if (orientation, role) == (Qt.Horizontal, \
            Qt.DisplayRole):
            return QVariant('Sample tree')

        return QVariant()
        
    def columnCount(self, parent):
        """The number of columns for the children of the given index."""
        return 1
        
        
    def rowCount(self, parent):
        """ The number of rows of the given index."""
        if not parent.isValid():
            parent_node = self.root
        else:
            parent_node = parent.internalPointer()
        return len(parent_node)
