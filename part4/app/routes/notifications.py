# Import necessary modules
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.database import db
from app.models.notification import Notification  # Assuming the Notification model is in app/models/notification.py
from datetime import datetime

# Create a Blueprint for notifications
notifications_bp = Blueprint('notifications', __name__, url_prefix='/user/notifications')

# Route to display notifications page
@notifications_bp.route('/')
@login_required
def view_notifications():
    user = current_user  # Get the logged-in user

    # Fetch notifications for the logged-in user
    notifications = Notification.query.filter_by(recipient_id=user.id).order_by(Notification.timestamp.desc()).all()

    return render_template('notifications.html', notifications=notifications)

# Route to mark a specific notification as read
@notifications_bp.route('/<int:notification_id>/mark_as_read', methods=["POST"])
@login_required
def mark_notification_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)

    # Ensure the notification belongs to the current user
    if notification.recipient_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for('notifications.view_notifications'))

    notification.status = 'read'  # Change the notification status to 'read'
    db.session.commit()  # Save the changes to the database

    flash("Notification marked as read.", "success")
    return redirect(url_for('notifications.view_notifications'))

# Route to mark all unread notifications as read
@notifications_bp.route('/mark_all_as_read', methods=['POST'])
@login_required
def mark_all_notifications_as_read():
    user = current_user  # Get the logged-in user

    # Mark all unread notifications as read
    notifications = Notification.query.filter_by(recipient_id=user.id, status='unread').all()
    for notification in notifications:
        notification.status = 'read'

    db.session.commit()  # Save the changes to the database
    return jsonify({"message": "All notifications marked as read."})

# Route to get the count of unread notifications
@notifications_bp.route('/unread_count')
@login_required
def get_unread_notifications_count():
    unread_count = Notification.query.filter_by(recipient_id=current_user.id, status='unread').count()
    return jsonify({"unread_count": unread_count})

# Route to get the notifications as JSON
@notifications_bp.route('/json')
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(recipient_id=current_user.id).order_by(Notification.timestamp.desc()).all()

    notifications_data = [{
        "message": notification.message,
        "status": notification.status,
        "timestamp": notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for notification in notifications]

    return jsonify({"notifications": notifications_data})
