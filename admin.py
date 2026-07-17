from flask import Flask, render_template, request
from db import DataBase
from auth import AuthRoute

class AdminRoute:
    def __init__(self, app: Flask, db: DataBase, main_ip: str, conn_type: str):
        self.db = db

        self.main_ip = main_ip # Айпи с которого запускаеться сервер
        self.conn_type = conn_type # Тип соединения: http | https

        app.add_url_rule("/admin", view_func=self.admin, methods=['GET', 'POST'])

    @AuthRoute.check_admin_session
    def admin(self):
        if request.method == 'GET':
            users = self.db.get_users("users")
            messages = self.db.get_messages("messages")

            return render_template(
                "admin.html", 
                users=users,
                messages=messages, 
                main_ip=self.main_ip, 
                conn_type=self.conn_type
            )