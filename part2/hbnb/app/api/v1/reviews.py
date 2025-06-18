from flask_restx import Namespace, Resource, fields
from app import facade
from datetime import datetime

ns = Namespace('reviews', description='Review operations')

review_model = ns.model('Review', {
    'id':         fields.String(readonly=True),
    'booking_id': fields.String(required=True),
    'text':       fields.String(required=True),
    'rating':     fields.Integer,
})

@ns.route('/')
class ReviewList(Resource):
    @ns.marshal_list_with(review_model)
    def get(self):
        """List all reviews"""
        return facade.list_reviews()

    @ns.expect(review_model, validate=True)
    @ns.marshal_with(review_model, code=201)
    def post(self):
        """Create a new review"""
        payload = ns.payload
        booking = facade.get_booking(payload.get('booking_id'))
        if not booking:
            ns.abort(400, "Booking not found")
        text = payload.get('text', '').strip()
        if not text:
            ns.abort(400, "Review text cannot be empty")
        rating = payload.get('rating')
        if rating is not None and not (1 <= rating <= 5):
            ns.abort(400, "Rating must be between 1 and 5")
        review = facade.create_review(payload)
        return review, 201

@ns.route('/<string:review_id>')
@ns.response(404, 'Review not found')
class ReviewDetail(Resource):
    @ns.marshal_with(review_model)
    def get(self, review_id):
        """Fetch a review by ID"""
        review = facade.get_review(review_id)
        if not review:
            ns.abort(404, f"Review {review_id} doesn't exist")
        return review

    @ns.response(204, 'Review deleted')
    def delete(self, review_id):
        """Delete a review"""
        if not facade.get_review(review_id):
            ns.abort(404, f"Review {review_id} doesn't exist")
        facade.delete_review(review_id)
        return '', 204

