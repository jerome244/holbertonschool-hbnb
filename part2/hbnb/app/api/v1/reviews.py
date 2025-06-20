"""
reviews.py: Flask-RESTX API endpoints for Review resources.

This module defines a namespace and models for reviews, including:
- Listing all reviews and creating a new review
- Retrieving, replacing, and deleting a review by ID

Swagger UI will display these descriptions alongside each endpoint.
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace("reviews", description="Review management")

# ----------------------- data models ----------------------- #
review_output = ns.model(
    "Review",
    {
        "id": fields.String(readonly=True, description="Review UUID"),
        "booking_id": fields.String(
            readonly=True, description="UUID of the associated booking"
        ),
        "text": fields.String(description="Review text"),
        "rating": fields.Integer(description="Rating between 1 and 5"),
    },
)

review_input = ns.model(
    "ReviewInput",
    {
        "booking_id": fields.String(required=True, description="UUID of the booking"),
        "text": fields.String(required=True, description="Review text"),
        "rating": fields.Integer(required=True, description="Rating between 1 and 5"),
    },
)


# ----------------------- resources ----------------------- #
@ns.route("/")
class ReviewList(Resource):
    """
    GET  /reviews/  -> List all reviews.
    POST /reviews/  -> Create a new review.
                       Payload example:
                       {
                         "booking_id": "<UUID>",
                         "text": "Great stay!",
                         "rating": 5
                       }
    """

    @ns.doc("list_reviews", description="Retrieve all reviews with ratings")
    @ns.marshal_list_with(review_output)
    def get(self):
        """List all reviews."""
        reviews = facade.list_reviews()
        result = []
        for r in reviews:
            try:
                rating_val = int(r.rating)
            except Exception:
                rating_val = None
            result.append(
                {
                    "id": r.id,
                    "booking_id": r.booking.id,
                    "text": r.text,
                    "rating": rating_val,
                }
            )
        return result

    @ns.doc(
        "create_review",
        description="Create a new review; Payload: booking_id, text, rating",
    )
    @ns.expect(review_input, validate=True)
    @ns.marshal_with(review_output, code=201)
    def post(self):
        """
        Create a new review.

        Validates booking existence, non-empty text, and rating bounds.
        """
        payload = request.json.copy()

        # Validate booking exists
        if not facade.get_booking(payload.get("booking_id")):
            ns.abort(400, "Booking not found")

        # Validate text
        text = payload.get("text", "").strip()
        if not text:
            ns.abort(400, "Review text cannot be empty")
        payload["text"] = text

        # Validate rating
        try:
            rating = int(payload.get("rating"))
        except Exception:
            ns.abort(400, "Rating must be an integer between 1 and 5")
        if not (1 <= rating <= 5):
            ns.abort(400, "Rating must be between 1 and 5")
        payload["rating"] = rating

        try:
            review = facade.create_review(payload)
        except Exception as e:
            msg = str(e)
            if "already has a review" in msg:
                ns.abort(400, msg)
            ns.abort(500, "Could not create review")

        return {
            "id": review.id,
            "booking_id": review.booking.id,
            "text": review.text,
            "rating": int(review.rating) if review.rating is not None else None,
        }, 201


@ns.route("/<string:review_id>")
@ns.response(404, "Review not found")
class ReviewDetail(Resource):
    """
    GET    /reviews/{id}  -> Retrieve a review by ID.
    PUT    /reviews/{id}  -> Replace an existing review.
                         Payload example:
                         {
                           "booking_id": "<UUID>",
                           "text": "Updated review text",
                           "rating": 4
                         }
    DELETE /reviews/{id}  -> Delete a review by ID.
    """

    @ns.doc("get_review", description="Retrieve a review by its ID")
    @ns.marshal_with(review_output)
    def get(self, review_id):
        """Fetch a review by its ID."""
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
        }

    @ns.doc(
        "replace_review",
        description="Replace an existing review; Payload: booking_id, text, rating",
    )
    @ns.expect(review_input, validate=True)
    @ns.marshal_with(review_output)
    def put(self, review_id):
        """
        Replace an existing review.

        Requires booking_id, text, and rating; enforces non-empty text and rating bounds.
        """
        payload = request.json.copy()

        # Validate booking exists
        if not facade.get_booking(payload.get("booking_id")):
            ns.abort(400, "Booking not found")

        # Validate text
        text = payload.get("text", "").strip()
        if not text:
            ns.abort(400, "Review text cannot be empty")

        # Validate rating
        try:
            rating = int(payload.get("rating"))
        except Exception:
            ns.abort(400, "Rating must be an integer between 1 and 5")
        if not (1 <= rating <= 5):
            ns.abort(400, "Rating must be between 1 and 5")

        # Delegate update through facade
        updated = facade.update_review(review_id, payload)
        if not updated:
            ns.abort(404, f"Review {review_id} not found")
        return updated, 200

    @ns.doc("delete_review", description="Delete a review by its ID")
    @ns.response(204, "Review deleted")
    def delete(self, review_id):
        """Delete a review by its ID."""
        if not facade.get_review(review_id):
            ns.abort(404, f"Review {review_id} not found")
        facade.delete_review(review_id)
        return "", 204
