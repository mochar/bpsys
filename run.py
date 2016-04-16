import sys

from PySide import QtGui

from gui.main_window import MainWindow


if __name__ == '__main__':
    app = QtGui.QApplication([])
    gui = MainWindow()
    sys.exit(app.exec_())