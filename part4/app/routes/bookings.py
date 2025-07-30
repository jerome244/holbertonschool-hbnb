from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.booking import Booking
from app.models.user import User
from app.models.place import Place
from app.database import db
from app.services.facade import facade
from datetime import datetime

bookings = Blueprint("bookings", __name__)

# --- Host Booking Management ---

@bookings.route("/bookings/<int:booking_id>/accept", methods=["POST"])
@login_required
def accept_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Check if the current user is the host of the booking
    if booking.place.host_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    # Check if the booking is already accepted or cancelled
    if booking.status != "pending":
        return jsonify({"error": "Booking cannot be accepted in its current state."}), 400

    try:
        booking.status = "accepted"
        db.session.add(booking)
        facade.notify_guest_booking_status(booking, "accepted")  # Notify guest
        db.session.commit()

        return jsonify(
            {"status": "accepted", "message": "Booking accepted and user notified."}
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bookings.route("/host/bookings")
@login_required
def host_bookings():
    user = current_user  # current_user is provided by Flask-Login

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("auth.login"))

    bookings = (
        Booking.query.join(Place)
        .filter(Place.host_id == user.id, Booking.status == "pending")
        .all()
    )

    last_requests = (
        Booking.query.join(Place)
        .filter(Place.host_id == user.id, Booking.status == "requested")
        .order_by(Booking.created_at.desc())  # Sort by creation date
        .limit(5)  # Limit the number of requests to show
        .all()
    )

    return render_template(
        "host_bookings.html", 
        bookings=bookings, 
        last_requests=last_requests
    )


@bookings.route("/booking/<booking_id>")
@login_required
def view_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template("view_booking.html", booking=booking)


@bookings.route("/host/bookings/<booking_id>/approve", methods=["POST"])
@login_required
def approve_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure that the current user is the host of the place
    if booking.place.host_id != current_user.id:
        flash(f"You are not authorized to approve the booking for {booking.place.title}.", "error")
        return redirect(url_for("places.host_bookings"))
    
    # Change the booking status to confirmed
    if booking.status != "pending":
        flash("Booking cannot be approved because it is not in 'pending' state.", "error")
        return redirect(url_for("bookings.host_bookings"))

    booking.status = "confirmed"
    
    try:
        db.session.commit()

        # Notify the guest (you may need to handle both success/failure of notification)
        facade.notify_guest_booking_status(booking, "accepted")

        flash(f"Booking for {booking.place.title} confirmed and guest notified.", "success")
        return redirect(url_for("bookings.host_bookings"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}. Please try again.", "error")
        return redirect(url_for("bookings.host_bookings"))

@bookings.route("/host/bookings/<booking_id>/decline", methods=["POST"])
@login_required
def decline_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.place.host_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("bookings.host_bookings"))

    try:
        booking.status = "declined"
        db.session.add(booking)

        facade.notify_guest_booking_status(booking, "declined")

        db.session.commit()
        flash(f"Booking for {booking.place.title} has been declined and guest notified.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}. Please try again.", "danger")

    return redirect(url_for("bookings.host_bookings"))

@bookings.route("/user/bookings/<booking_id>/cancel", methods=["POST"], endpoint="cancel_booking")
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    user_email = session.get("user")
    user = User.query.filter_by(email=user_email).first()

    if not user or booking.user_id != user.id:
        flash("Unauthorized cancellation.", "danger")
        return redirect(url_for("bookings.user_bookings"))

    if booking.status == "cancelled":
        flash("Booking is already cancelled.", "info")
        return redirect(url_for("bookings.user_bookings"))
    
    if booking.status == "accepted":
        flash("Cannot cancel an accepted booking.", "danger")
        return redirect(url_for("bookings.user_bookings"))

    try:
        booking.status = "cancelled"
        db.session.add(booking)

        place = booking.place
        host = User.query.get(place.host_id)
        message = f"{user.first_name} {user.last_name} has cancelled their booking for '{place.title}'."
        facade.notify_host_booking_cancelled(booking)

        db.session.commit()
        flash("Booking cancelled and host notified.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Error cancelling booking: {str(e)}", "danger")

    return redirect(url_for("bookings.user_bookings"))


# --- User Bookings ---

@bookings.route("/user/bookings")
@login_required
def user_bookings():
    user_email = session.get("user")
    user = User.query.filter_by(email=user_email).first()
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("auth.login"))
    bookings = Booking.query.filter_by(user_id=user.id).all()
    return render_template("user_bookings.html", bookings=bookings)

