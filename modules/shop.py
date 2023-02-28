import sqlite3 # Импорт модуля для работы с базой данных SQLite.

db = sqlite3.connect('shop.db') # Эта переменная осуществляет подключение к базе данных shop.db. Если база данных с таким названием отсутствует, то создаётся новая.
cursor = db.cursor() # Курсор нужен для осуществления запросов к базе данных.

cursor.execute(f"""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER,
    money FLOAT NOT NULL DEFAULT (0),
    userName TEXT,
    UNIQUE(user_id)
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS shop(
    prodName TEXT,
    prodDesc TEXT,
    prodPrice INTEGER,
    catID INTEGER,
    prodID INTEGER PRIMARY KEY
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS sendData(
    prodName TEXT,
    product TEXT,
    status TEXT,
    dataID INTEGER PRIMARY KEY
)""")

cursor.execute(f'''CREATE TABLE IF NOT EXISTS categories(
    catPhoto TEXT,
    catName TEXT,
    catDesc TEXT,
    catID INTEGER PRIMARY KEY
)''')



db.commit() # Вносит изменения в базу данных.
cursor.close()
db.close()
