import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required

from extensions import db, login_manager
from models import User
from forms import RegisterForm, LoginForm

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)

        user = User(
            username=form.username.data,
            password_hash=hashed_pw
        )

        # Profile picture upload
        if form.profile_image.data:
            file = form.profile_image.data
            filename = secure_filename(file.filename)

            upload_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                "pfps",
                filename
            )

            file.save(upload_path)
            user.profile_image = f"uploads/pfps/{filename}"

        db.session.add(user)
        db.session.commit()

        flash("Account created. You can now log in.")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for("index"))

        flash("Invalid username or password")

    return render_template("login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))