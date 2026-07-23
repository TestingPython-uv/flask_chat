from flask import Flask, session, redirect, url_for, request, render_template
from auth import AuthRoute
from db import DataBase

class ProfileRoute:
    def __init__(self, app: Flask, db: DataBase, main_ip: str, conn_type: str):
        """Класс обработки страницы профиля пользователя. /profile/..."""

        self.db = db

        self.profile_html = "profile.html" # Путь к html файлу профиля

        self.main_ip = main_ip # Айпи с которого запускаеться сервер
        self.conn_type = conn_type # Тип соединения: http | https

        self.main_args = {
            "template_name_or_list": self.profile_html, 
            "main_ip": self.main_ip,
            "conn_type": self.conn_type
        }

        app.add_url_rule("/profile", view_func=self.profile, methods=["GET", 'POST'])

    @AuthRoute.check_session
    def profile(self):
        if request.method == 'GET':
            username = request.args.get("user")

            exists = self.db.check_user_exists(username, "users")
            if exists:
                creation_time = self.db.get_user_creation_time(username)

                return render_template(
                    **self.main_args,
                    username=username,
                    creation_time=creation_time,
                    login=session.get("login")
                )
            else:
                return render_template(
                    **self.main_args,
                    error="Пользователь не существует",
                    login=session.get("login")
                )
            
        else:
            if request.form.get("create_chat"):
                main_user = session.get("login")
                other_user = request.form.get("profile_user")

                self.db.add_friend(main_user, other_user, "users")

                return redirect(url_for("index"))