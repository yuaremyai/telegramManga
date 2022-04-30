import sqlite3
import os

if not os.path.isfile("user.db"):
    create_table = '''CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        title TEXT DEFAULT 'TITLE_NAME',
        volume INTEGER DEFAULT 0,
        chapter INTEGER DEFAULT 0,
        page INTEGER DEFAULT 0,
        max_volume INTEGER DEFAULT 0,
        max_chapter INTEGER DEFAULT 0,
        max_page INTEGER DEFAULT 0)'''
    try:
        conn = sqlite3.connect("user.db")
        cur = conn.cursor()
        cur.execute(create_table)
        cur.close()
    except sqlite3.Error as error:
        print("Data Base connection error:", error)
    else:
        conn.close()


class DataBase:

    def connect_to_db(self):
        try:
            connect = sqlite3.connect("user.db")
        except sqlite3.Error as err:
            print("Data Base connection error:", err)
        else:
            return connect

    def init_user(self, chat_id):
        connect = self.connect_to_db()
        cursor = connect.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO user(id) VALUES({chat_id})")
        connect.commit()
        cursor.close()
        connect.close()

    def update_column(self, chat_id, column, value):
        connect = self.connect_to_db()
        cursor = connect.cursor()
        sql = f'''UPDATE user SET {column} = ? WHERE id = {chat_id}'''
        cursor.execute(sql, (value,))
        connect.commit()
        cursor.close()
        connect.close()

    def update_multi_column(self, chat_id, columns, values):
        connect = self.connect_to_db()
        cursor = connect.cursor()
        set_sql = ""
        for column in columns:
            set_sql += f"{column} = ?, "
        sql = f'''UPDATE user SET {set_sql[:-2]} WHERE id = {chat_id}'''
        cursor.execute(sql, values)
        connect.commit()
        cursor.close()
        connect.close()

    def get_column(self, chat_id, column):
        connect = self.connect_to_db()
        cursor = connect.cursor()
        sql = f'''SELECT {column} FROM user WHERE id = {chat_id}'''
        cursor.execute(sql)
        value = cursor.fetchall()[0]
        connect.commit()
        cursor.close()
        connect.close()
        return value[0]

    def get_multi_column(self, chat_id, columns):
        connect = self.connect_to_db()
        cursor = connect.cursor()
        sql = f'''SELECT {",".join(columns)} FROM user WHERE id = {chat_id}'''
        cursor.execute(sql)
        value = cursor.fetchall()[0]
        connect.commit()
        cursor.close()
        connect.close()
        return value
