import sys
import traceback

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

		self.applyChangesButton.setEnabled(False)
		self.cancelCangesButton.setEnabled(False)

		self.tabWidget.clear()
		tables_name = db.get_all_tables_name()
		if len(tables_name) == 0:
			QtWidgets.QMessageBox.information(self, "Предупреждение", "В данной бд нет никаких созданных таблиц!")

		for i, table_name in enumerate(tables_name):
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

		self.cancelCangesButton.clicked.connect(self.cancelCanges)
		self.applyChangesButton.clicked.connect(self.applyChanges)

	def cellChanged(self, row, column):
		tableWidget = self.sender()
		table_name = tableWidget.objectName().split("__")[1]
		table_item = tableWidget.item(row, column).text()
		if table_item == "None":
			table_item = None

		changes = list()
		_id = tableWidget.item(row, 0).text()
		for i in self.changes:
			if i[0] != table_name or i[2] != _id or i[1] != db.get_all_cols_by_table_name(table_name)[column]:
				changes.append(i)
		self.changes = changes

		col_name = db.get_all_cols_by_table_name(table_name)[column]
		if db.get_value_by_table_name_col_name_id(table_name, col_name, _id) != table_item:
			self.changes.append([table_name, col_name, _id, table_item, (row, column)])
			self.applyChangesButton.setEnabled(True)
			self.cancelCangesButton.setEnabled(True)
			print(f"New changes in {table_name}: {table_item}")

		self.color_table(tableWidget)

	def color_table(self, tableWidget, is_changed=True, cords=None):
		if is_changed:
			for i in self.changes:
				if i[0] in tableWidget.objectName():
					tableWidget.item(*i[4]).setBackground(QtGui.QColor(255, 255, 0))
		else:
			tableWidget.item(*cords).setBackground(QtGui.QColor(0, 0, 0, 0))

	def cancelCanges(self):
		for i in self.changes:
			widget = self.findChild(QtWidgets.QTableWidget, f"tableWidget__{i[0]}")
			widget.item(*i[4]).setText(db.get_value_by_table_name_col_name_id(i[0], i[1], i[2]))
			self.color_table(widget, is_changed=False, cords=i[4])
		self.changes = list()
		self.applyChangesButton.setEnabled(False)
		self.cancelCangesButton.setEnabled(False)

	def applyChanges(self):
		print("Applying changes...")
		is_ok = True

		for i in self.changes:
			try:
				db.change_item_by_table_name_col_name_id(*i[:4])
				widget = self.findChild(QtWidgets.QTableWidget, f"tableWidget__{i[0]}")
				self.color_table(widget, is_changed=False, cords=i[4])
			except Exception as e:
				self.tabWidget.setCurrentIndex(db.get_all_tables_name().index(i[0]))
				QtWidgets.QMessageBox.critical(self, "Ошибка при записи в бд", f"Ошибка в таблице '{i[0]}', в строчке {i[2]}, в столбце '{i[2]}'\n\n{traceback.format_exc()}")
				break
		else:
			self.applyChangesButton.setEnabled(False)
			self.cancelCangesButton.setEnabled(False)
			QtWidgets.QMessageBox.information(self, "Инфо", "Все изменения были сохранены!")


def except_hook(cls, exception, traceback):
	sys.__excepthook__(cls, exception, traceback)



if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyle("Fusion")
	ex = Ui()
	sys.excepthook = except_hook
	sys.exit(app.exec_())