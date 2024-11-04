import sqlite3
import uuid
class DatabaseConnection:
	def __init__(self):
		self.db = sqlite3.connect('KundalikMobile.db')
		self.c = self.db.cursor()
		self.create_tables()

		self.device_id = self.get_data("device_id")
		if self.device_id is None:
			self.device_id = str(uuid.uuid4())
			self.set_data("device_id", self.device_id)
		self.db.commit()

	def create_tables(self):
		try:
			self.c.execute('''CREATE TABLE datas (
				key TEXT NOT NULL,
				data TEXT NOT NULL
			)''')
		except:
			print(f"Error creating datas table")

		try:
			self.c.execute('''CREATE TABLE logins (
				id INTEGER PRIMARY KEY,
				name TEXT NOT NULL,
				login TEXT NOT NULL UNIQUE,
				password TEXT NOT NULL,
				holat BOOLEAN NOT NULL
			)''')
		except:
			print(f"Error creating logins table")
		self.db.commit()
	def logins_len(self):
		return len(self.c.execute('SELECT * FROM logins').fetchall())
	def get_data(self, key):
		try:
			self.c.execute('''SELECT * FROM datas WHERE key = ?''', (key,))
			result = self.c.fetchone()
			if result is not None:
				return result[1]
			return None
		except sqlite3.Error as e:
			print(f"Database error: {e}")
			return None

	def set_datas(self, datas):
		for key in datas.keys():
			self.set_data(key, datas[key])
	def set_data(self, key, data):
		self.c.execute('''SELECT * FROM datas WHERE key = ?''', (key,))
		fetched_data = self.c.fetchone()
		
		if fetched_data:
			self.c.execute('''UPDATE datas SET data = ? WHERE key = ?''', (data, key))
		else:
			self.c.execute('''INSERT INTO datas (key, data) VALUES (?, ?)''', (key, data))
		
		self.db.commit()
	
	def logout(self):
		try:
			self.c.execute('''DELETE FROM datas WHERE key = ?''', ("token",))
			self.db.commit()
		except:
			pass
	
	# Login ma'lumotlarini olish
	def get_login(self, _id):
		_, name, login, password, holat = self.c.execute("SELECT * FROM logins WHERE id = ?", (_id,)).fetchone()
		return {
			"name": name,
			"login": login,
			"password": password,
			"holat": holat
		}
	
	def get_logins(self) -> tuple[dict[str, dict], dict[str, dict]]:
		login_datas = self.c.execute("SELECT * FROM logins").fetchall()
		result = dict()
		result_err = dict()
		for login_data in login_datas:
			_id, name, login, password, holat = login_data
			if holat:
				result[login] = {
					"id": _id,
					"name": name,
					"login": login,
					"password": password,
					"holat": holat
				}
			else:
				result[login] = {
					"id": _id,
					"name": name,
					"login": login,
					"password": password,
					"holat": holat
				}
				result_err[login] = {
					"id": _id,
					"name": name,
					"login": login,
					"password": password,
					"holat": holat
				}
		return result, result_err
	# Login ma'lumotlarini yaratish
	def add_login(self, name, login, password):
		self.c.execute("INSERT INTO logins (name, login, password, holat) VALUES (?, ?, ?, ?)", (name, login, password, 1))
		self.db.commit()

	# Login ma'lumotlarini o'chirish
	def delete_login(self, _id):
		self.c.execute("DELETE FROM logins WHERE id = ?", (_id,))
		self.db.commit()

	# Login ma'lumotlarini taxrirlash
	def set_login(self, _id, name=None, login=None, password=None, holat=None):
		# Construct the SQL update statement dynamically based on the fields provided
		updates = []
		params = []
		
		if name is not None:
			updates.append("name = ?")
			params.append(name)
		if login is not None:
			updates.append("login = ?")
			params.append(login)
		if password is not None:
			updates.append("password = ?")
			params.append(password)
		if holat is not None:
			updates.append("holat = ?")
			params.append(holat)
		
		params.append(_id)
		sql_query = f"UPDATE logins SET {', '.join(updates)} WHERE id = ?"
		self.c.execute(sql_query, tuple(params))
		self.db.commit()

	# Database ni yopish dasturdan chiqilganda
	def close(self):
		self.db.close()

# Database yaratish
# database = DatabaseConnection()

# Barcha loginlarni olish
# print(database.get_logins())

# Login qo'shish
# print(database.add_login(name, login, parol, 1))

# Login ma'lumotini o'chirish
# print(database.del_login(1))

# Login ma'lumotini o'chirish
# print(database.set_login(1, parametslar...))
