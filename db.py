import sqlite3
from typing import Type

class DataBase:
    def __init__(self, db_path: str, tables_sql: list[str]):
        """
            :tables_sql: List[str]= Это список с кодом для каждой таблицы;
                Код - SQL, 1 элемент = 1 таблица
        """

        self.db_path = db_path
        self.tables_sql = tables_sql

        self.init_db(False)

    def init_db(self, return_cursor: bool=True) -> sqlite3.Cursor:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for sql in self.tables_sql:
                cursor.execute(sql)
                conn.commit()

            return cursor if return_cursor else None
    
    def check_user_exists(self, login: str, user_table: str, password: str=None) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if not password:
                cursor.execute(f"SELECT id FROM {user_table} WHERE login = ?", (login,))
            else:
                cursor.execute(f"SELECT id FROM {user_table} WHERE login = ? AND password = ?", (login, password))
        
        return True if cursor.fetchone() else False
        
    def insert_user(self, login: str, password: str, user_table: str, user_ip: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(f"INSERT INTO {user_table} (login, password, ip) VALUES (?, ?, ?)", (login, password, user_ip))
            conn.commit()

    def insert_message(self, login: str, message: str, msg_table: str, question_sender: str = "", question_text: str = "") -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"INSERT INTO {msg_table} (login, message, question_sender, question_text) VALUES (?, ?, ?, ?)", 
                (login, message, question_sender, question_text)
            )
                
            conn.commit()

            cursor.execute(
                f"SELECT id FROM {msg_table} WHERE login = ? AND message = ? AND question_sender = ? AND question_text = ?", 
                (login, message, question_sender, question_text)
            )
            message_id = cursor.fetchone()[0]

            return message_id
    
    def get_messages(self, msg_table: str) -> list[dict[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT id, login, message, question_sender, question_text FROM {msg_table}")
            rows = cursor.fetchall()

            messages = [{"index": row[0], "sender": row[1], "text": row[2], "question_sender": row[3], "question_text": row[4], "type": "1" if row[3] else "2"} for row in rows]

        return messages
    
    def get_users(self, user_table: str) -> list[dict[str, str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM {user_table}")
            rows = cursor.fetchall()

            users = [{"id": row[0], "login": row[1], "password": row[2], "ip": row[3]} for row in rows]
            return users
        
    def get_user_accounts(self, user_ip: str, user_table: str, to_return: Type = int) -> list[str] | int:
        """:to_return: list | int"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT login FROM {user_table} WHERE ip = ?", (user_ip,))
            rows = cursor.fetchall()

            if to_return is list:
                user_accounts = [r[0] for r in rows]
                return user_accounts
            
            elif to_return is int:
                user_accounts = len(rows)
                return user_accounts
            else:
                raise ValueError("Неверный тип данных в get_user_accounts")
            
    def get_user_creation_time(self, username: str) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT creation_time FROM users WHERE login = ?", (username,))
            creation_time = cursor.fetchone()[0]

            return creation_time
        
    def get_user_chats(self, username: str) -> dict[str, list[str]]:
        """
            :return:
                {
                    "channels": ['ch_name1', 'ch_name2'...],
                    "friends": ['fr_name1', 'fr_name2'...]
                }
        """

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT channels_id, friend_users_id FROM users WHERE login = ?", (username,))

            # channels_id, friend_users_id = "x;x;x;"
            
            channels_id_str, friends_id_str = cursor.fetchone()
            channels_id = channels_id_str.split(";") if channels_id_str else []
            friends_id = friends_id_str.split(";") if friends_id_str else []

            channels_id = [ch for ch in channels_id if ch]
            friends_id = [fr for fr in friends_id if fr]

            return {"channels": channels_id, "friends": friends_id}

    def add_friend(self, username: str, friend_username: str, users_table: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT friend_users_id FROM {users_table} WHERE login = ?", (username,))
            row = cursor.fetchone()
            line_friends = row[0] if row and row[0] is not None else ""
            line_friends += friend_username + ";"

            cursor.execute(f"UPDATE {users_table} SET friend_users_id = ? WHERE login = ?", (line_friends, username))
            conn.commit()

