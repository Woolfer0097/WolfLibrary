import sqlite3


connection = sqlite3.connect("../db/books.db")
cursor = connection.cursor()
query = cursor.execute("SELECT user_id FROM books").fetchall()
count = 0
for i in query:
    for j in i:
        count += 1
        cursor.execute(f"UPDATE books set user_id = 1 WHERE id = {count}")
connection.commit()
