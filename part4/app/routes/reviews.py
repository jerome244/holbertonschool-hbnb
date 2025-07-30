from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.review import Review
from app.models.place import Place
from app.models.booking import Booking
from app import db

reviews = Blueprint("reviews", __name__)


@reviews.route("/place/<place_id>/reviews")
def place_reviews(place_id):
    place = Place.query.get_or_404(place_id)
    return render_template("reviews/place_reviews.html", place=place)


