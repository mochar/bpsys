from PySide import QtCore, QtGui


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        super(PandasModel, self).__init__(parent=parent)
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