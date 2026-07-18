from flask import Flask, session
from flask_socketio import SocketIO, join_room, emit
from db import DataBase
from auth import AuthRoute
from index import IndexRoute, MainRoute
from admin import AdminRoute
from profile import ProfileRoute

app = Flask(__name__)
app.secret_key = "token"
app.config['SECRET_KEY'] = "token"

main_ip = "192.168.1.212"
conn_type = "http"

socket = SocketIO(app)

tables = [
    """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT,
            password TEXT,
            ip TEXT,
            creation_time DATETIME DEFAULT CURRENT_TIMESTAMP
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

auth_routes = AuthRoute(app, db, main_ip, conn_type)
index_route = IndexRoute(app, db, socket, main_ip, conn_type)
main_route = MainRoute(app)
admin_route = AdminRoute(app, db, main_ip, conn_type)
profile_route = ProfileRoute(app, db, main_ip, conn_type)

@socket.on("join_room")
def handle_join_room(data):
    room = "general"
    join_room(room)

@socket.on("message")
def handle_message(data):
    text = data['text']
    sender = session.get("login")

    message_index = db.insert_message(sender, text, "messages")

    emit("message", {"sender": sender, "text": text, "index": message_index}, room="general")

@socket.on("answer")
def handle_message_answer(data):
    text = data['text']
    login = session.get("login")
    question_sender = data['question_sender']
    question_text = data['question_text']

    message_index = db.insert_message(login, text, "messages", question_sender, question_text)
    emit("answer", {"question": f"[{question_sender}]: {question_text}", "message": f"[{login}]: {text}", "index": message_index})

if __name__ == "__main__":
    socket.run(app, host=main_ip, port=80, debug=True)