# Import necessary modules and packages
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import User, Place  # Assuming your models are imported this way
import logging

# Define Blueprint for handling reports
messages_api = Blueprint('messages_api', __name__)

@messages_api.route("/report_user", methods=["POST"])
@login_required
def report_user():
    if not request.is_json:
        logging.warning("Non-JSON request received at /api/messages/report_user")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    reported_user_id = data.get("reported_user_id")
    report_reason = data.get("reason")

    if not reported_user_id or not report_reason:
        logging.warning("Missing reported_user_id or reason")
        return jsonify({"error": "reported_user_id and reason required"}), 400

    reported_user = User.query.get(reported_user_id)
    if not reported_user:
        logging.warning(f"Reported user with id {reported_user_id} not found")
        return jsonify({"error": "Reported user not found"}), 404

    # Fetch the admin(s) dynamically
    admins = User.query.filter_by(role='admin').all()
    
    return jsonify({"message": "User reported successfully"}), 201


@messages_api.route("/report_place", methods=["POST"])
@login_required
def report_place():
    if not request.is_json:
        logging.warning("Non-JSON request received at /api/messages/report_place")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    reported_place_id = data.get("reported_place_id")
    report_reason = data.get("reason")

    if not reported_place_id or not report_reason:
        logging.warning("Missing reported_place_id or reason")
        return jsonify({"error": "reported_place_id and reason required"}), 400

    reported_place = Place.query.get(reported_place_id)
    if not reported_place:
        logging.warning(f"Reported place with id {reported_place_id} not found")
        return jsonify({"error": "Reported place not found"}), 404

    # Fetch the admin(s) dynamically
    admins = User.query.filter_by(role='admin').all()
    
    return jsonify({"message": "Place reported successfully"}), 201
