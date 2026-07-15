from flask import Flask, redirect, url_for, render_template, request
from db import DataBase
from auth import AuthRoute

class AdminRoute:
    def __init__(self, app: Flask, db: DataBase):
        self.db = db

        app.add_url_rule("/admin", view_func=self.admin, methods=['GET', 'POST'])

    @AuthRoute.check_admin_session
    def admin(self):
        if request.method == 'GET':
            users = self.db.get_users("users")
            messages = self.db.get_messages("messages")

            return render_template("admin.html", users=users, messages=messages)