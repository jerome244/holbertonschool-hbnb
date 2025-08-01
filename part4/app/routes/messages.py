from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.database import db
from app.models.message import Message
from app.models.user import User
from app.models.notification import Notification

from datetime import datetime
import logging

messages_bp = Blueprint("messages_bp", __name__)

# View: List conversations (all users you chatted with)
@messages_bp.route("/messages")
@login_required
def messages_list():
    user_id = current_user.id

    sent_users = db.session.query(Message.receiver_id).filter(
        Message.sender_id == user_id
    )
    received_users = db.session.query(Message.sender_id).filter(
        Message.receiver_id == user_id
    )
    user_ids = set(u[0] for u in sent_users.union(received_users))
    users = User.query.filter(User.id.in_(user_ids)).all()

    return render_template("messages_list.html", users=users)


@messages_bp.route("/chat/<other_user_id>")
@login_required
def chat(other_user_id):
    # Fetch the conversation messages between current_user and the other user
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    # Fetch the user's pseudo (name) to display in the chat
    other_user = User.query.get(other_user_id)

    return render_template(
        "chat.html", 
        your_user_id=current_user.id, 
        other_user_id=other_user_id,
        other_user_pseudo=other_user.pseudo,  # Add pseudo to the template
        messages=messages  # Pass messages to the template
    )


# API route to send a message
@messages_bp.route("/api/messages", methods=["POST"])
@login_required
def send_message():
    if not request.is_json:
        logging.warning("Non-JSON request received at /api/messages")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    receiver_id = data.get("receiver_id")
    content = data.get("content")
    place_id = data.get("place_id")

    if not receiver_id or not content:
        logging.warning("Missing receiver_id or content in message")
        return jsonify({"error": "receiver_id and content required"}), 400

    receiver = User.query.get(receiver_id)
    if not receiver:
        logging.warning(f"Receiver with id {receiver_id} not found")
        return jsonify({"error": "Receiver not found"}), 404

    try:
        # ✅ Capture sender's name before commit to avoid detached instance error
        sender_pseudo = current_user.pseudo

        # Create and save the message
        msg = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            place_id=place_id,
            content=content,
            timestamp=datetime.utcnow(),
            is_read=False,
        )
        db.session.add(msg)
        db.session.commit()

        # ✅ Create a notification for the receiver
        from app.models.notification import Notification
        notif = Notification(
            recipient_id=receiver_id,
            recipient_type="user",  # or "host" if applicable
            message=f"New message from {sender_pseudo}"
        )
        db.session.add(notif)
        db.session.commit()

        return jsonify({"message": "Message sent", "id": msg.id}), 201

    except Exception as e:
        logging.error("Failed to send message", exc_info=True)
        db.session.rollback()
        return jsonify({"error": "Failed to send message", "details": str(e)}), 500

# API route to get conversation messages
@messages_bp.route("/api/messages/conversation", methods=["GET"])
@login_required
def get_conversation():
    other_user_id = request.args.get("user_id")
    if not other_user_id:
        return jsonify({"error": "user_id required"}), 400
    
    messages = (
        Message.query.filter(
            (
                (Message.sender_id == current_user.id) & (Message.receiver_id == other_user_id)
            )
            | (
                (Message.sender_id == other_user_id) & (Message.receiver_id == current_user.id)
            )
        )
        .order_by(Message.timestamp.asc())
        .all()
    )
    
    return jsonify(
        [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "receiver_id": m.receiver_id,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
                "is_read": m.is_read,
            }
            for m in messages
        ]
    )
