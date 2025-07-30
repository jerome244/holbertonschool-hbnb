from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy.orm.exc import ObjectDeletedError

from app.models.user import User 
from app.models.place import Place
from app.models.review import Review
from app.models.message import Message
from app.database import db

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/index")
def index():
    # Fetch the 4 newest places (order by the most recent)
    newest_places = Place.query.order_by(Place.created_at.desc()).limit(4).all()

    # Calculate average rating for each place (for the top-rated places)
    places = Place.query.all()
    for place in places:
        reviews = Review.query.filter_by(place_id=place.id).all()
        if reviews:
            place.average_rating = sum([review.rating for review in reviews]) / len(reviews)
            # Get the top review (or any other specific review data you want to display)
            place.top_review = reviews[0]  # Assuming we want the first review as the "top" review
        else:
            place.average_rating = 0  # No reviews, set rating to 0
            place.top_review = None

    # Fetch the top 4 rated places (sorted by average_rating)
    top_rated_places = sorted(places, key=lambda x: x.average_rating, reverse=True)[:4]

    return render_template(
        "index.html",
        places=newest_places,
        top_rated_places=top_rated_places
    )

@views.route("/owner/<owner_id>")
def owner_profile(owner_id):
    owner = User.query.get_or_404(owner_id)
    places = Place.query.filter_by(host_id=owner.id).all()
    place_ids = [place.id for place in places]

    reviews = []
    avg_rating = None
    if place_ids:
        reviews = Review.query.filter(Review.place_id.in_(place_ids)).all()
        avg_rating = db.session.query(db.func.avg(Review.rating)).filter(Review.place_id.in_(place_ids)).scalar()

    return render_template(
        "owner_profile.html",
        owner=owner,
        places=places,
        reviews=reviews,
        avg_rating=round(avg_rating, 2) if avg_rating else None
    )
    
@views.route("/user/<user_id>")
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    user_places = Place.query.filter_by(host_id=user.id).all() 
    user_reviews = Review.query.filter_by(user_id=user.id).all()

    for review in user_reviews:
        review.place = Place.query.get(review.place_id)

    return render_template("user_profile.html", user=user, places=user_places, reviews=user_reviews)

@views.route("/message/<receiver_id>", methods=["GET", "POST"])
def start_message(receiver_id):
    sender = current_user  # The logged-in user (sender)

    # Fetch receiver from the database
    receiver = User.query.get(receiver_id)

    if receiver is None:
        flash("User not found or has been deleted.", "danger")
        return redirect(url_for('views.index'))  # Redirect to the index page (home)

    if request.method == "POST":
        message_content = request.form.get('message')

        if message_content:
            try:
                # Creating the new message and saving it to the database
                new_message = Message(
                    sender_id=sender.id,
                    receiver_id=receiver.id,
                    content=message_content
                )
                db.session.add(new_message)
                db.session.commit()

                flash("Message sent!", "success")

                # After committing, double-check if the receiver still exists
                receiver_check = User.query.get(receiver_id)
                if receiver_check:
                    return redirect(url_for('views.user_profile', user_id=receiver.id))
                else:
                    flash("The user has been deleted. Message sent, but profile not available.", "danger")
                    return redirect(url_for('views.index'))

            except Exception as e:
                # Handle unexpected errors
                return redirect(url_for('views.index'))

        else:
            flash("Message content cannot be empty", "danger")

    return render_template("message_form.html", receiver=receiver)


