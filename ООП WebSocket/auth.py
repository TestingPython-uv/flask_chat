from flask import session, render_template, redirect, url_for, request, Flask
from functools import wraps
import sqlite3
from db import DataBase

class AuthRoute:
    def __init__(self, app: Flask, db: DataBase):
        """ Класс обработки веток /auth, /create_account """

        self.auth_html = "auth.html" # Путь к файлу
        self.create_account_html = "create_account.html" # Путь к файлу

        self.flag_login = "log_into" # Флаг, получаемый от формы html, значит что user входит в систему
        self.main_page = "index" # Название ветки главной страницы
        self.user_table = "users" # Название таблицы в БД для пользователей

        self.db = db

        app.add_url_rule("/auth", view_func=self.auth, methods=['GET', 'POST'])
        app.add_url_rule("/create_account", view_func=self.create_account, methods=['GET', 'POST'])

    def auth(self):
        if request.method == 'GET':
            return render_template(self.auth_html)
        else:
            if request.form.get(self.flag_login):
                login = request.form.get("login")
                password = request.form.get("password")

                exists = self.db.check_user_exists(login, self.user_table, password)
                if exists:
                    session['login'] = login
                    return redirect(url_for(self.main_page))
                else:
                    return render_template(self.auth_html, error="Неверный логин или пароль")
            else:
                return redirect(url_for("create_account"))

    def create_account(self):
        if request.method == 'GET':
            return render_template("create_account.html")
        else:
            login = request.form.get("login")
            password = request.form.get("password")

            is_user_exists = self.db.check_user_exists(login, self.user_table)
            is_too_many_accounts = self.check_account_limit(10)

            if not is_user_exists:
                if not is_too_many_accounts:
                    if len(login) <= 20 and len(password) <= 100:
                        user_ip = request.remote_addr
                        self.db.insert_user(login, password, self.user_table, user_ip)
                        session['login'] = login

                        return redirect(url_for(self.main_page))
                    else:
                        return render_template(self.create_account_html, error="Слишком большой логин или пароль")
                else:
                    return render_template(self.create_account_html, error="Слишком много аккаунтов")
            else:
                return render_template(self.create_account_html, error="Такой пользователь уже существует")
    
    @staticmethod
    def check_session(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get("login"):
                return func(*args, **kwargs)
            else:
                return redirect(url_for("auth"))
        return wrapper
    
    @staticmethod
    def check_admin_session(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get("login") == "admin":
                return func(*args, **kwargs)
            else:
                return "Нет доступа к админ-панели"
        return wrapper
    
    def check_account_limit(self, account_limit: int):
        user_accounts = self.db.get_user_accounts(request.remote_addr, "users", int)
        return user_accounts >= account_limit
