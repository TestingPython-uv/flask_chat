from flask import Flask, render_template, redirect, url_for, session, request
from flask_socketio import emit, SocketIO
from auth import AuthRoute
from db import DataBase

class IndexRoute:
    def __init__(self, app: Flask, db: DataBase, socket: SocketIO, main_ip: str, conn_type: str):
        self.db = db
        self.socket = socket

        self.main_ip = main_ip # Айпи сервера
        self.conn_type = conn_type # Тип подключения: http | https

        app.add_url_rule("/index", view_func=self.index, methods=['GET', 'POST'])

    @AuthRoute.check_session
    def index(self):
        if request.method == 'GET':
            messages = self.db.get_messages("messages")
            return render_template(
                "index.html", 
                login=session.get("login"), 
                messages=messages, 
                main_ip=self.main_ip, 
                conn_type=self.conn_type
            )
        else:
            if request.form.get("clear_session"):
                session.pop("login", None)
                return redirect(url_for("auth"))
            
            elif request.form.get("admin"):
                return redirect(url_for("admin"))
            
            elif request.form.get("check_message"):
                self.socket.emit("show_msg_funcs", {})
                return redirect(url_for("index"))
            
            elif request.form.get("get_user_chats"):
                login = session.get("login")
                chats_data = self.db.get_user_chats(login)
                return chats_data
            
            else:
                return redirect(url_for("index"))
            
            
class MainRoute:
    def __init__(self, app: Flask):
        app.add_url_rule("/", view_func=self.main, methods=['GET'])
    
    @AuthRoute.check_session
    def main(self):
        return redirect(url_for("index"))