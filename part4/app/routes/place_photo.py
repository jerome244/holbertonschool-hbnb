import os
from flask import Blueprint, request, flash, redirect, url_for, current_app, jsonify
from werkzeug.utils import secure_filename
from app import db
from app.models.place import Place
from app.models.place_photo import PlacePhoto
from flask_login import login_required, current_user

# Define allowed file extensions for photo uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Blueprint for photo-related actions
place_photo_bp = Blueprint("place_photo_bp", __name__, url_prefix="/place")

# Helper function to check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload photo for a place
@place_photo_bp.route("/<place_id>/upload_photo", methods=["POST"])
@login_required
def upload_photo(place_id):
    place = Place.query.get_or_404(place_id)

    # Ensure the user is the host of the place
    if place.host_id != current_user.id:
        flash("You are not authorized to upload photos for this place.", "error")
        return redirect(url_for("places.place", place_id=place.id))

    # Ensure file is part of the request
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)

    file = request.files['file']

    # If no file is selected
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)

    # If the file is allowed
    if file and allowed_file(file.filename):
        # Use current_app to access the app's config
        upload_folder = os.path.join(current_app.root_path, 'static/uploads')
        
        # Ensure the upload folder exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)  # Save relative path
        file.save(os.path.join(upload_folder, filename))

        # Create and save the photo record in the database with the relative path
        photo = PlacePhoto(url=filepath, place_id=place.id)
        db.session.add(photo)
        db.session.commit()

        flash("Photo uploaded successfully.", "success")
        return redirect(url_for("places.place", place_id=place.id))

    flash('Invalid file type. Only images are allowed.', 'error')
    return redirect(request.url)

@place_photo_bp.route("/<place_id>/photos/<photo_id>/delete", methods=["POST"])
@login_required
def delete_photo(place_id, photo_id):
    place = Place.query.get_or_404(place_id)
    photo = PlacePhoto.query.get_or_404(photo_id)

    # Ensure the photo belongs to the place
    if photo.place_id != place.id:
        return jsonify({"error": "Photo does not belong to this place."}), 400

    # Ensure the user is the host of the place
    if place.host_id != current_user.id:
        return jsonify({"error": "Unauthorized action."}), 403

    # Construct the full path to the photo file
    photo_path = os.path.join(current_app.root_path, "static", "uploads", photo.url)

    # Check if the file exists
    if os.path.exists(photo_path):
        os.remove(photo_path)
    else:
        return jsonify({"error": "Photo file not found."}), 404

    # Remove the photo record from the database
    db.session.delete(photo)
    db.session.commit()

    return jsonify({"message": "Photo deleted successfully."}), 200
