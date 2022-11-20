import sys

from PyQt5 import Qt
from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow
from template import Ui_MainWindow

from db import Database



db = Database("./db.db")



class Ui(QMainWindow, Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.changes = []
		self.setupUi(self)
		self.initUi()
		self.show()

	def initUi(self):
		self.setWindowTitle("SQLite tables viewer")

		self.tabWidget.clear()
		for i, table_name in enumerate(db.get_all_tables_name()):
			tab = QtWidgets.QWidget()
			tab.setObjectName(f"tab__{table_name}")
			verticalLayout_2 = QtWidgets.QVBoxLayout(tab)
			verticalLayout_2.setObjectName("verticalLayout_2")

			tableWidget = QtWidgets.QTableWidget(tab)
			table_colums = db.get_all_cols_by_table_name(table_name)
			tableWidget.setColumnCount(len(table_colums))
			tableWidget.setHorizontalHeaderLabels(table_colums)
			for row in db.get_table_data_by_table_name(table_name):
				rows = tableWidget.rowCount()
				tableWidget.setRowCount(rows + 1)
				for j, item in enumerate(row):
					tableWidget.setItem(rows, j, QtWidgets.QTableWidgetItem(str(item)))
					if table_colums[j] == "id":
						tableWidget.item(rows, j).setFlags(tableWidget.item(rows, 0).flags() ^ QtCore.Qt.ItemIsEnabled)
			tableWidget.resizeColumnsToContents()

			tableWidget.setObjectName(f"tableWidget__{table_name}")
			tableWidget.cellChanged.connect(self.cellChanged)
			verticalLayout_2.addWidget(tableWidget)
			self.tabWidget.addTab(tab, table_name)

		self.applyChangesButton.clicked.connect(self.applyChanges)

	def cellChanged(self, row, column):
		tableWidget = self.sender()
		table_name = tableWidget.objectName().split("__")[1]
		table_item = tableWidget.item(row, column).text()
		self.changes.append([table_name, db.get_all_cols_by_table_name(table_name)[column], tableWidget.item(row, 0).text(), table_item])
		print(f"New changes in {table_name}: {table_item}")
		# print(dir(tableWidget))

	def applyChanges(self):
		print("Applying changes...")
		for i in self.changes:
			db.change_item_by_table_name_col_name_id(*i)


def except_hook(cls, exception, traceback):
	sys.__excepthook__(cls, exception, traceback)



if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyle("Fusion")
	ex = Ui()
	sys.excepthook = except_hook
	sys.exit(app.exec_())