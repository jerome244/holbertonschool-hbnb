from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.notification import Notification
from app.database import db

ns = Namespace("notifications", description="User notifications")

notification_model = ns.model("Notification", {
    "id": fields.Integer(),
    "message": fields.String(),
    "status": fields.String(),
    "timestamp": fields.String()
})

@ns.route("/")
class NotificationList(Resource):
    @ns.doc("list_notifications")
    @ns.marshal_list_with(notification_model)
    @jwt_required()
    def get(self):
        """List all notifications for the logged-in user"""
        user_id = get_jwt_identity()
        notifications = Notification.query.filter_by(recipient_id=user_id).order_by(Notification.timestamp.desc()).all()
        return [{
            "id": n.id,
            "message": n.message,
            "status": n.status,
            "timestamp": n.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for n in notifications]

@ns.route("/unread_count")
class UnreadCount(Resource):
    @ns.doc("get_unread_count")
    @jwt_required()
    def get(self):
        """Get count of unread notifications"""
        user_id = get_jwt_identity()
        count = Notification.query.filter_by(recipient_id=user_id, status="unread").count()
        return {"unread_count": count}

@ns.route("/<int:notification_id>/mark_as_read")
class MarkAsRead(Resource):
    @ns.doc("mark_notification_as_read")
    @jwt_required()
    def post(self, notification_id):
        """Mark a notification as read"""
        user_id = get_jwt_identity()
        notification = Notification.query.get_or_404(notification_id)
        if notification.recipient_id != user_id:
            return {"error": "Unauthorized"}, 403
        notification.status = "read"
        db.session.commit()
        return {"message": "Notification marked as read."}

@ns.route("/mark_all_as_read")
class MarkAllAsRead(Resource):
    @ns.doc("mark_all_as_read")
    @jwt_required()
    def post(self):
        """Mark all notifications as read"""
        user_id = get_jwt_identity()
        notifications = Notification.query.filter_by(recipient_id=user_id, status="unread").all()
        for n in notifications:
            n.status = "read"
        db.session.commit()
        return {"message": "All notifications marked as read."}


notifications_ns = ns
