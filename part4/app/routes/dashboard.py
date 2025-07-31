from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.models.user import User
from app.models.message import Message
from app.models.booking import Booking
from app.models.amenity import Amenity
from app.database import db
from functools import wraps

dashboard = Blueprint("dashboard", __name__)


# Admin-only route protection
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("You must be logged in.", "warning")
            return redirect(url_for("auth.login"))
        if not getattr(current_user, "is_admin", False):
            flash("Admin access required.", "danger")
            return redirect(url_for("views.index"))
        return f(*args, **kwargs)
    return decorated_function


# ------------------ Dashboard ------------------ #

@dashboard.route("/dashboard")
@login_required
def dashboard_view():
    user = current_user

    # Fetch confirmed bookings for the user
    confirmed_bookings = Booking.query.filter_by(user_id=user.id, status="confirmed").all()

    # Statistics for widgets
    total_bookings = Booking.query.filter_by(user_id=user.id).count()
    unread_messages = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    upcoming_reservations = Booking.query.filter(
        Booking.user_id == user.id,
        Booking.start_date >= datetime.utcnow(),
        Booking.status == "confirmed"
    ).count()

    # Total views for user's places
    total_views = sum(place.views for place in user.places)

    return render_template(
        "dashboard.html",
        total_bookings=total_bookings,
        unread_messages=unread_messages,
        upcoming_reservations=upcoming_reservations,
        confirmed_bookings=confirmed_bookings,
        places=user.places,
        total_views=total_views
    )


# ------------------ Become Host ------------------ #

@dashboard.route("/become_host", methods=["GET", "POST"])
@login_required
def become_host():
    user = current_user

    if getattr(user, "type", None) == "host":
        flash("You are already a host!", "info")
        return redirect(url_for("dashboard.dashboard_view"))

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")

        if not first_name or not last_name:
            flash("Please provide both first and last name.", "error")
            return render_template("become_host.html", user=user)

        user.first_name = first_name
        user.last_name = last_name
        user.type = "host"

        db.session.commit()

        flash("You are now a host!", "success")
        return redirect(url_for("dashboard.dashboard_view"))

    return render_template("become_host.html", user=user)


# ------------------ Amenity Management (Admin Only) ------------------ #

@dashboard.route("/admin/amenities", methods=["GET"])
@login_required
@admin_required
def manage_amenities():
    amenities = Amenity.query.all()
    return render_template("admin_manage_amenities.html", amenities=amenities)


@dashboard.route("/admin/amenities/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_amenity():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Amenity name is required.", "error")
            return redirect(url_for("dashboard.add_amenity"))

        amenity = Amenity(name=name)
        db.session.add(amenity)
        db.session.commit()

        flash("Amenity added.", "success")
        return redirect(url_for("dashboard.manage_amenities"))

    return render_template("admin_add_amenity.html")


@dashboard.route("/admin/amenities/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_amenity(id):
    amenity = Amenity.query.get(id)
    if not amenity:
        flash("Amenity not found.", "error")
        return redirect(url_for("dashboard.manage_amenities"))

    if request.method == "POST":
        amenity.name = request.form.get("name")
        if not amenity.name:
            flash("Amenity name is required.", "error")
            return redirect(url_for("dashboard.edit_amenity", id=id))

        db.session.commit()
        flash("Amenity updated.", "success")
        return redirect(url_for("dashboard.manage_amenities"))

    return render_template("admin_edit_amenity.html", amenity=amenity)


@dashboard.route("/admin/amenities/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_amenity(id):
    amenity = Amenity.query.get(id)
    if not amenity:
        flash("Amenity not found.", "error")
    else:
        db.session.delete(amenity)
        db.session.commit()
        flash("Amenity deleted.", "success")

    return redirect(url_for("dashboard.manage_amenities"))
