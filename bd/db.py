import sqlite3
import os


"""
[+] join
[-] union
[+] where
[+] order by
[+] limit
[+] having
[+] group by
"""


class Database:
	def __init__(self, db_file):
		if not os.path.exists(db_file):
			with open(db_file, "w", encoding="utf-8"):
				pass
		self.connection = sqlite3.connect(db_file, check_same_thread=False)
		self.cursor = self.connection.cursor()
		with self.connection:
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS food (
									    id                INTEGER PRIMARY KEY AUTOINCREMENT,
									    restourant_id     INTEGER NOT NULL,
									    food_categorie_id INTEGER NOT NULL,
									    name              VARCHAR NOT NULL,
									    price             NUMERIC NOT NULL);""")
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS food_categories (
									    id   INTEGER PRIMARY KEY AUTOINCREMENT,
									    name VARCHAR NOT NULL);""")
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS food_group (
									    id       INTEGER PRIMARY KEY AUTOINCREMENT,
									    order_id INTEGER NOT NULL,
									    user_id  INTEGER NOT NULL,
									    food_id  INTEGER NOT NULL,
									    pieces   INTEGER NOT NULL
									                     DEFAULT (1));""")
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS restourants (
									    id        INTEGER PRIMARY KEY AUTOINCREMENT,
									    name      VARCHAR NOT NULL,
									    longitude NUMERIC NOT NULL,
									    latitude  NUMERIC NOT NULL,
									    website   VARCHAR NOT NULL);""")
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS user_basket (
									    id      INTEGER PRIMARY KEY AUTOINCREMENT,
									    user_id INTEGER NOT NULL,
									    food_id INTEGER NOT NULL,
									    pieces  INTEGER NOT NULL
									                    DEFAULT (1));""")
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS user_order (
									    id             INTEGER  PRIMARY KEY AUTOINCREMENT,
									    order_datetime DATETIME NOT NULL,
									    user_id        INTEGER  NOT NULL,
									    restourant_id  INTEGER  NOT NULL,
									    longitude      NUMERIC  NOT NULL,
									    latitude       NUMERIC  NOT NULL);""")
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
									    id         INTEGER PRIMARY KEY AUTOINCREMENT,
									    first_name VARCHAR NOT NULL,
									    last_name  VARCHAR NOT NULL,
									    birthday   DATE,
									    phone      VARCHAR NOT NULL,
									    email      VARCHAR);""")

	def get_all_tables_name(self):
		"""
		Получение названия всех таблиц (из sqlite_schema)
		"""
		with self.connection:
			return list(filter(lambda t: t != "sqlite_sequence", map(lambda t: t[0], self.cursor.execute("""SELECT "name" FROM "sqlite_schema" WHERE "type" = 'table' ORDER BY "name";""").fetchall())))

	def get_all_cols_by_table_name(self, table_name):
		"""
		Получение названия всех столбцов по названию таблицы
		"""
		with self.connection:
			return list(map(lambda t: t[1], self.cursor.execute("""PRAGMA table_info('{}');""".format(table_name)).fetchall()))

	def get_table_data_by_table_name(self, table_name):
		"""
		Вытаскивание всех данных из таблицы
		"""
		with self.connection:
			return self.cursor.execute("""SELECT * FROM "{}";""".format(table_name)).fetchall()

	def change_item_by_table_name_col_name_id(self, table_name, col_name, _id, value):
		"""
		Изменение ячейки по названию таблицы и id
		"""
		with self.connection:
			self.cursor.execute("""UPDATE "{}" SET "{}" = ? WHERE "id" = ?;""".format(table_name, col_name), (value, _id,))

	def get_food_by_restourant_id(self, restourant_id):
		with self.connection:
			return self.cursor.execute("""SELECT food_categories.name, food.name FROM "food_categories"
											JOIN "food" ON food_categories.id = food.food_categorie_id
											WHERE food.restourant_id = ?
											ORDER BY food_categories.name;""", (restourant_id,)).fetchall()

	def get_food_categories_count_by_restourant_id(self, restourant_id):
		"""
		Получение количества еды купленной в каждой категории.
		Эта информация может быть полезна для определения самого популярного типа еды в ресторане
		"""
		with self.connection:
			return self.cursor.execute("""SELECT food.name, COUNT(*) as count FROM "user_order"
											JOIN "food_group" ON user_order.id = food_group.order_id
											JOIN "food" ON food_group.food_id = food.id
											JOIN "food_categories" ON food.food_categorie_id = food_categories.id
											GROUP BY food_categories.name
											HAVING food.restourant_id = ?
											ORDER BY count;""", (restourant_id,)).fetchall()

	def get_food_count_restourant_id(self, restourant_id):
		"""
		Получение количества еды купленной каждым пользователем.
		Эта информация может быть полезна для определения самого популярной еды в ресторане
		"""
		with self.connection:
			return self.cursor.execute("""SELECT food.name, COUNT(*) as count FROM "user_order"
											JOIN "food_group" ON user_order.id = food_group.order_id
											JOIN "food" ON food_group.food_id = food.id
											GROUP BY food.name
											HAVING food.restourant_id = ?
											ORDER BY count;""", (restourant_id,)).fetchall()

	def get_restourants_count(self):
		"""
		Получение количество заказов в каждом ресторане (топ 10).
		Эта информация может быть полезна для определения самого популярного ресторана
		"""
		with self.connection:
			return self.cursor.execute("""SELECT restourants.name, COUNT(*) as count FROM "user_order"
											JOIN "food_group" ON user_order.id = food_group.order_id
											JOIN "food" ON food_group.food_id = food.id
											JOIN "restourants" ON food.restourant_id = restourants.id
											GROUP BY food.restourant_id
											ORDER BY count
											LIMIT 10;""").fetchall()


if __name__ == '__main__':
	db = Database("./db.db")

	# for table_name in db.get_all_tables_name():
	# 	print(table_name, db.get_all_cols_by_table_name(table_name), db.get_table_data_by_table_name(table_name))

	for i in db.get_restourants_count():
		print(i)