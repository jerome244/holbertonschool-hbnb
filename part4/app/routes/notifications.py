from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.database import db
from app.models.notification import Notification

notifications_bp = Blueprint("notifications_bp", __name__, url_prefix="/api/v1/notifications")

@notifications_bp.route("/", methods=["GET"])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(recipient_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    data = [{
        "id": n.id,
        "message": n.message,
        "status": n.status,
        "timestamp": n.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for n in notifications]
    return jsonify({"notifications": data})

@notifications_bp.route("/unread_count", methods=["GET"])
@login_required
def unread_count():
    count = Notification.query.filter_by(recipient_id=current_user.id, status="unread").count()
    return jsonify({"unread_count": count})

@notifications_bp.route("/<int:notification_id>/mark_as_read", methods=["POST"])
@login_required
def mark_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.recipient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    notification.status = "read"
    db.session.commit()
    return jsonify({"message": "Notification marked as read."})

@notifications_bp.route("/mark_all_as_read", methods=["POST"])
@login_required
def mark_all_as_read():
    notifications = Notification.query.filter_by(recipient_id=current_user.id, status="unread").all()
    for n in notifications:
        n.status = "read"
    db.session.commit()
    return jsonify({"message": "All notifications marked as read."})
