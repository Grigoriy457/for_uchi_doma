import sqlite3
# import os

class Database:
	def __init__(self, db_file):
		# if not os.path.exists(db_file):
		# 	with open(db_file, "w", encoding="utf-8"):
		# 		pass
		self.connection = sqlite3.connect(db_file, check_same_thread=False)
		self.cursor = self.connection.cursor()

	def get_all_tables_name(self):
		with self.connection:
			return list(filter(lambda t: t != "sqlite_sequence", map(lambda t: t[0], self.cursor.execute("""SELECT "name" FROM "sqlite_schema" WHERE "type" = 'table' ORDER BY "name";""").fetchall())))

	def get_all_cols_by_table_name(self, table_name):
		with self.connection:
			return list(map(lambda t: t[1], self.cursor.execute("""PRAGMA table_info('{}');""".format(table_name)).fetchall()))

	def get_table_data_by_table_name(self, table_name):
		with self.connection:
			return self.cursor.execute("""SELECT * FROM "{}";""".format(table_name)).fetchall()

	def change_item_by_table_name_col_name_id(self, table_name, col_name, _id, value):
		with self.connection:
			self.cursor.execute("""UPDATE "{}" SET "{}" = ? WHERE "id" = ?;""".format(table_name, col_name), (value, _id,))


if __name__ == '__main__':
	db = Database("./db.db")
	for table_name in db.get_all_tables_name():
		print(table_name, db.get_all_cols_by_table_name(table_name), db.get_table_data_by_table_name(table_name))