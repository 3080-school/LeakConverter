import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()


# Добавим тестового пользователя
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("0003", "arbuz3"))

conn.commit()
conn.close()
print("success.")
