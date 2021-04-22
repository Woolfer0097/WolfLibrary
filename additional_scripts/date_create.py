import sqlite3
from datetime import datetime


connection = sqlite3.connect("../db/books.db")
cursor = connection.cursor()
query = cursor.execute("SELECT created_date FROM books").fetchall()
count = 0
for i in query:
    for j in i:
        count += 1
        cursor.execute(f"UPDATE books set created_date = '{datetime.now()}' WHERE id = {count}")
        # cursor.execute(f"UPDATE books set updated_date = '{datetime.now()}' WHERE id = {count}")
connection.commit()
