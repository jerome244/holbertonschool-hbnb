from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

ns = Namespace(
    "reviews",
    description="Review management",
    security='BearerAuth'
)

# ----------------------- data models ----------------------- #
review_output = ns.model(
    "Review",
    {
        "id": fields.String(readOnly=True, description="Review UUID"),
        "booking_id": fields.String(readOnly=True, description="UUID of the associated booking"),
        "text": fields.String(description="Review text"),
        "rating": fields.Integer(description="Rating between 1 and 5"),
    },
)

review_input = ns.model(
    "ReviewInput",
    {
        "booking_id": fields.String(required=True, description="UUID of the booking to review"),
        "text": fields.String(required=True, description="Review text"),
        "rating": fields.Integer(required=True, description="Rating between 1 and 5"),
    },
)

@ns.route("/")
class ReviewList(Resource):
    @ns.doc(
        "list_reviews",
        description="Retrieve all reviews (Authenticated users)",
        security='BearerAuth'
    )
    @jwt_required()
    @ns.marshal_list_with(review_output)
    def get(self):
        """
        Retrieve a list of all reviews. Only authenticated users may list reviews.
        """
        reviews = facade.list_reviews()
        result = []
        for r in reviews:
            try:
                rating_val = int(r.rating)
            except Exception:
                rating_val = None
            result.append({
                "id": r.id,
                "booking_id": r.booking.id,
                "text": r.text,
                "rating": rating_val,
            })
        return result, 200

    @ns.doc(
        "create_review",
        description="Create a new review (Booking owner only; one review per booking)",
        security='BearerAuth'
    )
    @ns.expect(review_input, validate=True)
    @jwt_required()
    @ns.marshal_with(review_output, code=201)
    def post(self):
        """
        Submit a new review for a booking. Only the user who made the booking may review it.
        """
        payload = request.json.copy()

        # Validate booking existence
        booking = facade.get_booking(payload.get("booking_id"))
        if not booking:
            ns.abort(400, "Booking not found")

        # Ensure only booking owner can submit review
        current_user = get_jwt_identity()
        if booking.user.id != current_user:
            ns.abort(403, "Unauthorized action")

        # Prevent reviewing own place (if booking owner is also host)
        if booking.place.host.id == current_user:
            ns.abort(400, "You cannot review your own place.")

        # Validate text
        text = payload.get("text", "").strip()
        if not text:
            ns.abort(400, "Review text cannot be empty")
        payload["text"] = text

        # Validate rating
        try:
            rating = int(payload.get("rating"))
        except (TypeError, ValueError):
            ns.abort(400, "Rating must be an integer between 1 and 5")
        if not (1 <= rating <= 5):
            ns.abort(400, "Rating must be between 1 and 5")
        payload["rating"] = rating

        # Create review, handle duplicate
        try:
            review = facade.create_review(payload)
        except Exception as e:
            if "already has a review" in str(e):
                ns.abort(400, "You have already reviewed this booking.")
            ns.abort(500, "Could not create review")

        setattr(review, "booking_id", review.booking.id)
        
        return review, 201

@ns.route("/<string:review_id>")
@ns.response(404, "Review not found")
class ReviewDetail(Resource):
    @ns.doc(
        "get_review",
        description="Fetch a review by its ID (Authenticated users)",
        security='BearerAuth'
    )
    @jwt_required()
    @ns.marshal_with(review_output)
    def get(self, review_id):
        """
        Retrieve a specific review by UUID. Only authenticated users may fetch reviews.
        """
        r = facade.get_review(review_id)
        if not r:
            ns.abort(404, f"Review {review_id} not found")
        try:
            rating_val = int(r.rating)
        except Exception:
            rating_val = None
        return {
            "id": r.id,
            "booking_id": r.booking.id,
            "text": r.text,
            "rating": rating_val,
        }, 200

    @ns.doc(
        "replace_review",
        description="Replace an existing review (Author or Admin only)",
        security='BearerAuth'
    )
    @ns.expect(review_input, validate=True)
    @jwt_required()
    @ns.marshal_with(review_output)
    def put(self, review_id):
        """
        Update an existing review. Only the review author or an admin may replace a review.
        """
        review = facade.get_review(review_id)
        if not review:
            ns.abort(404, f"Review {review_id} not found")

        current_user = get_jwt_identity()
        claims = get_jwt()
        if review.booking.user.id != current_user and not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")

        # Validate booking
        booking = facade.get_booking(request.json.get("booking_id"))
        if not booking:
            ns.abort(400, "Booking not found")

        # Validate text
        text = request.json.get("text", "").strip()
        if not text:
            ns.abort(400, "Review text cannot be empty")

        # Validate rating
        try:
            rating = int(request.json.get("rating"))
        except (TypeError, ValueError):
            ns.abort(400, "Rating must be an integer between 1 and 5")
        if not (1 <= rating <= 5):
            ns.abort(400, "Rating must be between 1 and 5")

        payload = {
            "booking_id": booking.id,
            "text": text,
            "rating": rating
        }

        updated = facade.update_review(review_id, payload)
        if not updated:
            ns.abort(404, f"Review {review_id} not found")
        return updated, 200

    @ns.doc(
        "delete_review",
        description="Delete a review by its ID (Author or Admin only)",
        security='BearerAuth'
    )
    @jwt_required()
    @ns.response(204, "Review deleted")
    def delete(self, review_id):
        """
        Remove a review. Only the review author or an admin may delete a review.
        """
        review = facade.get_review(review_id)
        if not review:
            ns.abort(404, f"Review {review_id} not found")

        current_user = get_jwt_identity()
        claims = get_jwt()
        if review.booking.user.id != current_user and not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")

        facade.delete_review(review_id)
        return "", 204
