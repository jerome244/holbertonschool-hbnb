from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.message import Message
from app.models.user import User
from app.database import db
from datetime import datetime

ns = Namespace("messages", description="Messaging operations")

message_model = ns.model(
    "Message",
    {
        "id": fields.Integer(readonly=True),
        "sender_id": fields.String(readonly=True),  # UUID as string
        "receiver_id": fields.String(required=True),  # UUID as string
        "place_id": fields.Integer,
        "content": fields.String(required=True),
        "timestamp": fields.DateTime(readonly=True),
        "is_read": fields.Boolean(readonly=True),
    },
)


@ns.route("")
class MessageList(Resource):
    @jwt_required()
    @ns.expect(message_model, validate=True)
    def post(self):
        """Send a new message"""
        data = request.json
        sender_id = get_jwt_identity()
        receiver_id = data.get("receiver_id")
        place_id = data.get("place_id")
        content = data.get("content")

        if not receiver_id or not content:
            return {"message": "receiver_id and content are required"}, 400

        receiver = User.query.get(receiver_id)
        if not receiver:
            return {"message": "Receiver not found"}, 404

        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            place_id=place_id,
            content=content,
            timestamp=datetime.utcnow(),
            is_read=False,
        )
        db.session.add(message)
        db.session.commit()

        return {"message": "Message sent", "id": message.id}, 201


@ns.route("/conversation")
class Conversation(Resource):
    @jwt_required()
    @ns.param("user_id", "Other user ID to fetch conversation with", required=True)
    @ns.param("place_id", "Place ID to filter messages", required=False)
    def get(self):
        """Get conversation messages with another user, optionally filtered by place"""
        current_user_id = get_jwt_identity()
        other_user_id = request.args.get("user_id")
        place_id = request.args.get("place_id", type=int)

        if not other_user_id:
            return {"message": "user_id query parameter is required"}, 400

        query = Message.query.filter(
            (
                (Message.sender_id == current_user_id)
                & (Message.receiver_id == other_user_id)
            )
            | (
                (Message.sender_id == other_user_id)
                & (Message.receiver_id == current_user_id)
            )
        )
        if place_id:
            query = query.filter(Message.place_id == place_id)

        messages = query.order_by(Message.timestamp.asc()).all()

        result = [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "receiver_id": m.receiver_id,
                "place_id": m.place_id,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
                "is_read": m.is_read,
            }
            for m in messages
        ]

        return result
