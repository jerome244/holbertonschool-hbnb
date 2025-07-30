from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user import User
from app.models.host import Host
from app.models.message import Message
from app.models.booking import Booking
from app.models.amenity import Amenity
from app.models.place import Place
from app.database import db
from flask_login import login_required
from datetime import datetime

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
@login_required
def dashboard_view():
    user_email = session.get("user")
    user = User.query.filter_by(email=user_email).first()

    if not user:
        flash("User not found.")
        return redirect(url_for("auth.login"))

    # Fetch confirmed bookings for the user
    confirmed_bookings = Booking.query.filter_by(
        user_id=user.id, status="confirmed"
    ).all()

    # Statistics for widgets
    total_bookings = Booking.query.filter_by(user_id=user.id).count()
    unread_messages = Message.query.filter_by(
        receiver_id=user.id, is_read=False
    ).count()  # Updated to receiver_id instead of recipient_id
    upcoming_reservations = Booking.query.filter(
        Booking.user_id == user.id,
        Booking.start_date >= datetime.utcnow(),
        Booking.status == "confirmed",
    ).count()

    # Calculate total views for all places owned by the user
    total_views = sum(place.views for place in user.places)

    return render_template(
        "dashboard.html",
        total_bookings=total_bookings,
        unread_messages=unread_messages,
        upcoming_reservations=upcoming_reservations,
        confirmed_bookings=confirmed_bookings,
        places=user.places,
        total_views=total_views,  # Pass the total views to the template
    )

@dashboard.route("/become_host", methods=["GET", "POST"])
def become_host():
    user_email = session.get("user")
    user = User.query.filter_by(email=user_email).first()
    
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("auth.login"))

    # Check if user is already a host
    if getattr(user, "type", None) == "host":
        flash("You are already a host!", "info")
        return redirect(url_for("dashboard.dashboard_view"))
    
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        
        if not first_name or not last_name:
            flash("Please provide both first and last name.", "error")
            return render_template("become_host.html", user=user)
        
        # Update the user's information
        user.first_name = first_name
        user.last_name = last_name
        user.type = "host"
        
        # Commit changes to the database
        db.session.add(user)
        db.session.commit()

        # Update the session to reflect the new type
        session["user"] = user.email  # Refresh the session to reflect the updated user

        # Notify the user and redirect to the dashboard
        flash("You are now a host!", "success")
        return redirect(url_for("dashboard.dashboard_view"))

    return render_template("become_host.html", user=user)


# --- Amenity Management (Admin only) ---


@dashboard.route("/amenities", methods=["GET", "POST"])
def manage_amenities():
    user_email = session.get("user")
    user = User.query.filter_by(email=user_email).first()
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("auth.login"))
    if not getattr(user, "is_admin", False):
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("auth.index"))
    amenities = Amenity.query.all()
    return render_template("admin_manage_amenities.html", amenities=amenities)


@dashboard.route("/amenities/add", methods=["GET", "POST"])
def add_amenity():
    user_email = session.get("user")
    user = User.query.filter_by(email=user_email).first()
    if not user or not getattr(user, "is_admin", False):
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("auth.index"))
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Amenity name is required.", "error")
            return redirect(url_for("dashboard.add_amenity"))
        amenity = Amenity(name=name)
        db.session.add(amenity)
        db.session.commit()

        return redirect(url_for("dashboard.manage_amenities"))
    return render_template("admin_add_amenity.html")


@dashboard.route("/admin/amenities/edit/<int:id>", methods=["GET", "POST"])
def edit_amenity(id):
    user_email = session.get("user")
    user = User.query.filter_by(email=user_email).first()
    if not user or not getattr(user, "is_admin", False):
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("auth.index"))
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

        return redirect(url_for("dashboard.manage_amenities"))
    return render_template("admin_edit_amenity.html", amenity=amenity)


@dashboard.route("/amenities/delete/<int:id>", methods=["POST"])
def delete_amenity(id):
    user_email = session.get("user")
    user = User.query.filter_by(email=user_email).first()
    if not user or not getattr(user, "is_admin", False):
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("auth.index"))
    amenity = Amenity.query.get(id)
    if not amenity:
        flash("Amenity not found.", "error")
    else:
        db.session.delete(amenity)
        db.session.commit()

    return redirect(url_for("dashboard.manage_amenities"))
