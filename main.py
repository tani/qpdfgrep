"""
GUI frontend for Poppler search
"""

import pathlib
import sys
import glob
import os
import gi
from PySide2 import QtWidgets, QtGui

gi.require_version('Poppler', '0.18')


class SearchForm(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pattern = QtWidgets.QLineEdit("pattern")
        self.search = QtWidgets.QPushButton("Search")
        self.search.clicked.connect(self.on_button_clicked)
        self.progress = QtWidgets.QProgressBar()
        self.progress.hide()
        self.result = QtWidgets.QTableWidget()
        self.result.setColumnCount(3)
        self.result.setHorizontalHeaderLabels(["File", "page", "Line"])
        self.result.itemDoubleClicked.connect(self.on_item_clicked)
        hblayout = QtWidgets.QHBoxLayout()
        hblayout.addWidget(self.pattern)
        hblayout.addWidget(self.search)
        vblayout = QtWidgets.QVBoxLayout()
        vblayout.addLayout(hblayout)
        vblayout.addWidget(self.progress)
        vblayout.addWidget(self.result)
        self.setLayout(vblayout)

    def on_button_clicked(self):
        from gi.repository import Poppler
        files = glob.glob("./**/*.pdf")
        self.progress.show()
        self.progress.setMinimum(0)
        self.progress.setMaximum(len(files))
        self.result.setRowCount(0)
        for k, file in enumerate(files):
            self.progress.setValue(k+1)
            uri = pathlib.Path(os.path.abspath(file)).as_uri()
            document = Poppler.Document.new_from_file(uri, "")
            for i in range(document.get_n_pages()):
                page = document.get_page(i)
                height = page.get_size()[1]
                for rect in page.find_text(self.pattern.text()):
                    rect.y1 = height - rect.y1
                    rect.y2 = height - rect.y2
                    style = Poppler.SelectionStyle.LINE
                    line = page.get_selected_text(style, rect)
                    self.result.setRowCount(self.result.rowCount()+1)
                    for j, header in enumerate([file, str(i), line]):
                        item = QtWidgets.QTableWidgetItem(header)
                        self.result.setItem(self.result.rowCount()-1, j, item)
        self.result.resizeColumnsToContents()
        self.result.resizeRowsToContents()
        self.progress.hide()

    def on_item_clicked(self, item):
        if item.column() == 0:
            uri = pathlib.Path(os.path.abspath(item.text())).as_uri()
            QtGui.QDesktopServices.openUrl(uri)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    searchForm = SearchForm()
    searchForm.show()
    sys.exit(app.exec_())
