from flask import Flask, session
from flask_socketio import SocketIO, join_room, emit
from db import DataBase
from auth import AuthRoute
from index import IndexRoute, MainRoute
from admin import AdminRoute

app = Flask(__name__)
app.secret_key = "token"
app.config['SECRET_KEY'] = "token"

socket = SocketIO(app)

tables = [
    """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT,
            password TEXT,
            ip TEXT
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT,
            message TEXT,
            question_sender TEXT,
            question_text TEXT
        ) 
    """
]
db = DataBase("chat.db", tables)
db.init_db(False)

auth_routes = AuthRoute(app, db)
index_route = IndexRoute(app, db, socket)
main_route = MainRoute(app)
admin_route = AdminRoute(app, db)

@socket.on("join_room")
def handle_join_room(data):
    room = "general"
    join_room(room)

@socket.on("message")
def handle_message(data):
    text = data['text']
    sender = session.get("login")

    db.insert_message(sender, text, "messages")

    emit("message", {"message": f"[{sender}]: {text}"}, room="general")

@socket.on("answer")
def handle_message_answer(data):
    text = data['text']
    login = session.get("login")
    question_sender = data['question_sender']
    question_text = data['question_text']

    # ТУТ ИЗМЕНИТЬ: надо сделать функцию или возвращать индекс сообщения после его вставки (id AUTOINCREMENT) и передавать в emit
    db.insert_message(login, text, "messages", question_sender, question_text)
    emit("answer", {"question": f"[{question_sender}]: {question_text}", "message": f"[{login}]: {text}", "index": ...})

if __name__ == "__main__":
    socket.run(app, host="192.168.1.212", port=80, debug=True)