from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
)
from flask_login import login_required, login_user, logout_user, current_user
from app.models.user import User
from app.database import db
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        session["user"] = user.email
        flash("Logged in successfully!", "success")
        return redirect(url_for("views.index"))

    return render_template("login.html")


@auth.route("/logout")
def logout():
    logout_user()
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("auth.login"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        pseudo = request.form.get("pseudo")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please login or use a different email.", "error")
            return render_template("register.html")

        if pseudo:
            existing_pseudo = User.query.filter_by(pseudo=pseudo).first()
            if existing_pseudo:
                flash("This nickname is already taken, please choose another.", "error")
                return render_template("register.html")

        # Create new user
        user = User(email=email, first_name=first_name, last_name=last_name, pseudo=pseudo)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Log the user in by setting session
        session["user"] = user.email
        flash("Registration successful! You are now logged in.", "success")

        # Check if user is a host, if not, redirect to become_host page
        if user.type != "host":
            flash("Please become a host to create places.", "info")
            return redirect(url_for("dashboard.become_host"))

        # If the user is a host, redirect to dashboard
        return redirect(url_for("dashboard.dashboard_view"))

    return render_template("register.html")


@auth.route("/profile", methods=["GET", "POST"])
def profile():
    user_email = session.get("user")
    user = User.query.filter_by(email=user_email).first()
    if not user:
        flash("You must be logged in to view your profile.", "error")
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        pseudo = request.form.get("pseudo")
        if pseudo:
            existing_pseudo = User.query.filter_by(pseudo=pseudo).first()
            if existing_pseudo and existing_pseudo.id != user.id:
                flash("This nickname is already taken, please choose another.", "error")
                return render_template("profile.html", user=user)

        user.pseudo = pseudo
        user.bio = request.form.get("bio")
        file = request.files.get("profile_pic")
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.root_path, "static/uploads")
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, filename))
            user.profile_pic = filename
        db.session.commit()
        flash("Profile updated!")
        return redirect(url_for("auth.profile"))
    return render_template("profile.html", user=user)

@auth.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user = current_user
    # Perform account deletion logic
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("auth.logout"))

