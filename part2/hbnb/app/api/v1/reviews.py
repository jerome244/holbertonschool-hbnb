from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import HBnBFacade

facade    = HBnBFacade()
review_ns = Namespace('reviews', description='Review operations')

review_model = review_ns.model('Review', {
    'id': fields.String(readonly=True),
    'user_id': fields.String(required=True),
    'rating': fields.Integer(required=True, description='1–5'),
    'comment': fields.String(),
    'place_id': fields.String(required=True)
})

@review_ns.route('/')
class ReviewList(Resource):
    @review_ns.doc('list_reviews')
    @review_ns.marshal_list_with(review_model)
    def get(self):
        """List all reviews across all places"""
        all_reviews = []
        for place in facade.get_all_places():
            place_id = place['id']
            try:
                reviews = facade.get_reviews(place_id)
                for r in reviews:
                    r['place_id'] = place_id
                    all_reviews.append(r)
            except KeyError:
                continue
        return all_reviews

    @review_ns.doc('create_review')
    @review_ns.expect(review_model, validate=True)
    @review_ns.marshal_with(review_model, code=201)
    def post(self):
        """Add a review to a place"""
        data = request.get_json()
        place_id = data.pop('place_id')
        try:
            rev = facade.add_review(place_id, data)
            rev['place_id'] = place_id
            return rev, 201
        except KeyError as e:
            review_ns.abort(404, str(e))
        except (TypeError, ValueError) as e:
            review_ns.abort(400, str(e))

@review_ns.route('/<string:id>')
@review_ns.response(404, 'Review not found')
@review_ns.param('id', 'The review identifier')
class ReviewResource(Resource):
    @review_ns.doc('delete_review')
    @review_ns.response(204, 'Review deleted')
    def delete(self, id):
        """Delete a review by its identifier"""
        try:
            facade.delete_review(id)
            return '', 204
        except KeyError as e:
            review_ns.abort(404, str(e))
