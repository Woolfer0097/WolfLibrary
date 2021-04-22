import sqlite3


connection = sqlite3.connect("../db/books.db")
cursor = connection.cursor()
query = cursor.execute("SELECT image_link FROM books").fetchall()
count = 0
for i in query:
    for j in i:
        count += 1
        image_link = f"'static/images/skins/{j.split('/')[-1]}'"
        cursor.execute(f"UPDATE books set image_link = {image_link} WHERE id = {count}")
connection.commit()
