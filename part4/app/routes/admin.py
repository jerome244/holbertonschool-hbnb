from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import Review, Amenity, Place, User, Booking
from app import db
from functools import wraps
from uuid import UUID
from app.utils.decorators import admin_required
from app.models.message import Message

# Define the Blueprint for admin routes
admin = Blueprint("admin", __name__, url_prefix="/admin")


# Admin access decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


# Route to view reported reviews
@admin.route("/reported_reviews")
@login_required
@admin_required
def reported_reviews():
    reviews = Review.query.filter_by(reported=True).all()
    return render_template("admin/reported_reviews.html", reviews=reviews)


# Route to delete a review
@admin.route("/delete_review/<int:review_id>", methods=["POST"])
@login_required
@admin_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash("Review deleted.", "success")
    return redirect(url_for("admin.reported_reviews"))


# Route to dismiss a report on a review
@admin.route("/dismiss_report/<int:review_id>", methods=["POST"])
@login_required
@admin_required
def dismiss_report(review_id):
    review = Review.query.get_or_404(review_id)
    review.reported = False
    db.session.commit()
    flash("Report dismissed.", "success")
    return redirect(url_for("admin.reported_reviews"))


# Route to list all amenities
@admin.route("/amenities")
@login_required
@admin_required
def amenities_list():
    amenities = Amenity.query.all()
    return render_template("admin_manage_amenities.html", amenities=amenities)


# Route to add a new amenity
@admin.route("/amenities/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_amenity():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Amenity name is required.", "danger")
            return render_template("admin_add_amenity.html")

        amenity = Amenity(name=name)
        db.session.add(amenity)
        db.session.commit()
        flash("Amenity added successfully.", "success")
        return redirect(url_for("admin.amenities_list"))

    return render_template("admin_add_amenity.html")


# Route to edit an amenity
@admin.route("/amenities/<amenity_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_amenity(amenity_id):
    amenity = Amenity.query.get_or_404(amenity_id)
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Amenity name is required.", "danger")
            return render_template("admin_edit_amenity.html", amenity=amenity)
        amenity.name = name
        db.session.commit()
        flash("Amenity updated successfully.", "success")
        return redirect(url_for("admin.amenities_list"))
    return render_template("admin_edit_amenity.html", amenity=amenity)


# Route to delete an amenity
@admin.route("/amenities/<amenity_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_amenity(amenity_id):
    amenity = Amenity.query.get_or_404(amenity_id)
    db.session.delete(amenity)
    db.session.commit()
    flash("Amenity deleted successfully.", "success")
    return redirect(url_for("admin.amenities_list"))


# Route to list all places
@admin.route("/places")
@login_required
@admin_required
def places_list():
    places = Place.query.all()
    return render_template("admin/places_list.html", places=places)


@admin.route('/delete_user/<uuid:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(str(user_id))  # Fetch the user by UUID

    # Set the default user ID for messages
    default_user_id = 'default-user-id'  # Replace with the ID of a valid user (e.g., admin)

    # Ensure all messages where the user is the sender or receiver are updated to a default user
    Message.query.filter_by(sender_id=user.id).update({Message.sender_id: default_user_id})
    Message.query.filter_by(receiver_id=user.id).update({Message.receiver_id: default_user_id})

    # Delete the user
    db.session.delete(user)
    db.session.commit()

    flash(f"User {user.pseudo} deleted successfully.", "success")
    return redirect(url_for('admin.view_users'))


# Route to delete a place
@admin.route("/delete_place/<int:place_id>", methods=["POST"])
@login_required
@admin_required
def delete_place(place_id):
    try:
        place = Place.query.get(place_id)
        if not place:
            return jsonify({"error": "Place not found"}), 404

       
        db.session.delete(place)
        db.session.commit()
        return jsonify({"message": "Place deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin.route('/users')
@login_required
@admin_required
def view_users():
    users = User.query.all()  # Get all users
    return render_template('view_users.html', users=users)

@admin.route('/edit_user/<uuid:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    try:
        # Try fetching the user by UUID
        user = User.query.get_or_404(str(user_id))
        
        if request.method == 'POST':
            # Update the user's attributes from the form
            user.pseudo = request.form['username']
            user.email = request.form['email']
            is_admin = request.form.get('is_admin') == 'True'
            user.is_admin = is_admin

            # Commit changes to the database
            db.session.commit()

            # Flash success message after committing
            flash(f'{user.pseudo} updated successfully!', 'success')
            return redirect(url_for('admin.view_users'))
        
        return render_template('edit_user.html', user=user)

    except ObjectDeletedError:
        # Handle the error gracefully by showing a neutral message and redirecting
        flash('The user has been deleted or is no longer available.', 'danger')
        return redirect(url_for('admin.view_users'))


@admin.route('/grant_admin/<user_id>', methods=['POST'])
@login_required
@admin_required
def grant_admin(user_id):
    user = User.query.get_or_404(user_id)  # Ensure the user is fetched again
    if user:  # Make sure the user exists
        user.is_admin = True
        db.session.commit()
        flash(f'{user.pseudo} is now an admin.', 'success')
    else:
        flash('User not found or already deleted.', 'danger')  # Handle deletion
    return redirect(url_for('admin.view_users'))

