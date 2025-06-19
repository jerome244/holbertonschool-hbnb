from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace('reviews', description='Review operations')

# Shared fields
rating_field = fields.Integer(description='Rating between 1 and 5')

# 1) Input model for POST
review_input = ns.model('ReviewInput', {
    'booking_id': fields.String(required=True, description='UUID of the booking'),
    'text':       fields.String(required=True, description='Review text'),
    'rating':     rating_field,
})

# 1b) Patch model (all fields optional)
review_patch = ns.model('ReviewPatch', {
    'text':   fields.String(description='Review text'),
    'rating': rating_field,
})

# 2) Response model (explicitly expose booking_id via attribute)
review_model = ns.model('Review', {
    'id':         fields.String(readOnly=True, description='Review UUID'),
    'booking_id': fields.String(attribute='booking.id', description='UUID of the associated booking'),
    'text':       fields.String(description='Review text'),
    'rating':     rating_field,
})

@ns.route('/')
class ReviewList(Resource):
    @ns.marshal_list_with(review_model)
    def get(self):
        """List all reviews"""
        return facade.list_reviews()

    @ns.expect(review_input, validate=True)
    @ns.marshal_with(review_model, code=201)
    def post(self):
        """Create a new review"""
        payload = ns.payload.copy()

        # Validate booking exists
        booking = facade.get_booking(payload.get('booking_id'))
        if not booking:
            ns.abort(400, 'Booking not found')

        # Validate text
        text = payload.get('text', '').strip()
        if not text:
            ns.abort(400, 'Review text cannot be empty')

        # Validate rating type and range
        rating = payload.get('rating')
        if rating is not None:
            try:
                rating = int(rating)
            except (ValueError, TypeError):
                ns.abort(400, 'Rating must be an integer between 1 and 5')
            if not (1 <= rating <= 5):
                ns.abort(400, 'Rating must be between 1 and 5')
            payload['rating'] = rating

        # Create via facade
        review = facade.create_review(payload)
        return review, 201

@ns.route('/<string:review_id>')
class ReviewDetail(Resource):
    @ns.marshal_with(review_model)
    def get(self, review_id):
        """Fetch a review by ID"""
        review = facade.get_review(review_id)
        if not review:
            ns.abort(404, f"Review {review_id} not found")
        return review

    @ns.expect(review_patch, validate=True)
    @ns.marshal_with(review_model)
    def patch(self, review_id):
        """Update an existing review"""
        review = facade.get_review(review_id)
        if not review:
            ns.abort(404, f"Review {review_id} not found")

        payload = ns.payload.copy()

        # Validate text if provided
        if 'text' in payload:
            text = payload.get('text', '').strip()
            if not text:
                ns.abort(400, 'Review text cannot be empty')
            review.text = text

        # Validate rating if provided
        if 'rating' in payload:
            rating = payload.get('rating')
            try:
                rating = int(rating)
            except (ValueError, TypeError):
                ns.abort(400, 'Rating must be an integer between 1 and 5')
            if not (1 <= rating <= 5):
                ns.abort(400, 'Rating must be between 1 and 5')
            review.rating = rating

        return review
