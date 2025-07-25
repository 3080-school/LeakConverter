import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# ОЧИСТИТЬ ТАБЛИЦУ users
cursor.execute("DELETE FROM answers")
conn.commit()

# Если надо добавить пользователя после очистки:
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("0004", "arbuz4"))
conn.commit()
# Если надо добавить пользователя после очистки:
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("0005", "arbuz5"))
conn.commit()
# Если надо добавить пользователя после очистки:
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("0006", "arbuz6"))
conn.commit()
# Если надо добавить пользователя после очистки:
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("0007", "arbuz7"))
conn.commit()
# Если надо добавить пользователя после очистки:
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("0008", "arbuz8"))
conn.commit()
# Если надо добавить пользователя после очистки:
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("0009", "arbuz9"))
conn.commit()
# Если надо добавить пользователя после очистки:
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("0010", "arbuz10"))
conn.commit()
# Если надо добавить пользователя после очистки:
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("0011", "arbuz11"))
conn.commit()


conn.close()
print("success.")
