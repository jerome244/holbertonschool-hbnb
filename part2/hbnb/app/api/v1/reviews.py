# app/api/v1/reviews.py

from flask import request
from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace('reviews', description='Review operations')

# Response model for a review
review_output = ns.model('Review', {
    'id':         fields.String(readOnly=True, description='Review UUID'),
    'booking_id': fields.String(readOnly=True, description='UUID of the associated booking'),
    'text':       fields.String(description='Review text'),
    'rating':     fields.Integer(description='Rating between 1 and 5'),
})

# Input model for POST
review_input = ns.model('ReviewInput', {
    'booking_id': fields.String(required=True, description='UUID of the booking'),
    'text':       fields.String(required=True, description='Review text'),
    'rating':     fields.Integer(required=True, description='Rating between 1 and 5'),
})

# Patch model for PATCH
review_patch = ns.model('ReviewPatch', {
    'text':   fields.String(description='Review text'),
    'rating': fields.Integer(description='Rating between 1 and 5'),
})

@ns.route('/')
class ReviewList(Resource):
    @ns.marshal_list_with(review_output)
    def get(self):
        """List all reviews"""
        reviews = facade.list_reviews()
        result = []
        for r in reviews:
            # Coerce rating to int or None
            try:
                rating = int(r.rating)
            except Exception:
                rating = None
            result.append({
                'id':         r.id,
                'booking_id': r.booking.id,
                'text':       r.text,
                'rating':     rating,
            })
        return result

    @ns.expect(review_input, validate=True)
    @ns.marshal_with(review_output, code=201)
    def post(self):
        """Create a new review"""
        payload = request.json.copy()

        # Validate booking exists
        booking = facade.get_booking(payload.get('booking_id'))
        if not booking:
            ns.abort(400, 'Booking not found')

        # Validate text
        text = payload.get('text', '').strip()
        if not text:
            ns.abort(400, 'Review text cannot be empty')
        payload['text'] = text

        # Validate rating
        rating = payload.get('rating')
        try:
            rating = int(rating)
        except Exception:
            ns.abort(400, 'Rating must be an integer between 1 and 5')
        if not (1 <= rating <= 5):
            ns.abort(400, 'Rating must be between 1 and 5')
        payload['rating'] = rating

        # Create review
        review = facade.create_review(payload)

        # Coerce rating for output
        try:
            out_rating = int(review.rating)
        except Exception:
            out_rating = None

        return {
            'id':         review.id,
            'booking_id': review.booking.id,
            'text':       review.text,
            'rating':     out_rating,
        }, 201

@ns.route('/<string:review_id>')
class ReviewDetail(Resource):
    @ns.marshal_with(review_output)
    def get(self, review_id):
        """Fetch a review by ID"""
        r = facade.get_review(review_id)
        if not r:
            ns.abort(404, f"Review {review_id} not found")
        try:
            rating = int(r.rating)
        except Exception:
            rating = None
        return {
            'id':         r.id,
            'booking_id': r.booking.id,
            'text':       r.text,
            'rating':     rating,
        }

    @ns.expect(review_patch, validate=True)
    @ns.marshal_with(review_output)
    def patch(self, review_id):
        """Update an existing review"""
        r = facade.get_review(review_id)
        if not r:
            ns.abort(404, f"Review {review_id} not found")

        payload = request.json.copy()

        if 'text' in payload:
            text = payload.get('text', '').strip()
            if not text:
                ns.abort(400, 'Review text cannot be empty')
            r.text = text

        if 'rating' in payload:
            try:
                rating = int(payload.get('rating'))
            except Exception:
                ns.abort(400, 'Rating must be an integer between 1 and 5')
            if not (1 <= rating <= 5):
                ns.abort(400, 'Rating must be between 1 and 5')
            r.rating = rating

        try:
            out_rating = int(r.rating)
        except Exception:
            out_rating = None

        return {
            'id':         r.id,
            'booking_id': r.booking.id,
            'text':       r.text,
            'rating':     out_rating,
        }
