import uuid
import os
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
    jsonify,
)
from flask_login import current_user, login_required
from app.models.place import Place
from app.models.host import Host
from app.models.user import User
from app.models.booking import Booking
from app.models.place_photo import PlacePhoto
from app.models.amenity import Amenity
from app.models.review import Review
from app.database import db
from app.utils.geocode import geocode_address
from app.utils.calculate_price import calculate_price
from app.utils.photo_utils import save_photo
from app.services.facade import facade
from datetime import datetime
from sqlalchemy import func
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import ObjectDeletedError
from functools import wraps




places = Blueprint("places", __name__, url_prefix="/places")



# Place-related routes
@places.route("/booking/<place_id>")
def booking_redirect(place_id):
    return redirect(url_for("places.booking", place_id=place_id))




@places.route("/<place_id>/booking", methods=["GET", "POST"])
@login_required
def booking(place_id):
    place = Place.query.get_or_404(place_id)

    if not current_user.is_authenticated:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))

    user = current_user
    user_id = user.id

    # Prevent booking your own listing
    if place.host_id == user_id:
        flash("You cannot book your own place.", "error")
        return redirect(url_for("places.place", place_id=place_id))

    # Check for duplicate booking
    existing_booking = (
        Booking.query.filter_by(user_id=user_id, place_id=place_id)
        .order_by(Booking.created_at.desc())
        .first()
    )
    if existing_booking and existing_booking.status in ["pending", "accepted"]:
        flash("You already have a pending or accepted booking for this place.", "error")
        return redirect(url_for("places.place", place_id=place_id))

    if request.method == "POST":
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")
        guest_count = request.form.get("guest_count")

        try:
            guest_count_int = int(guest_count)
            if guest_count_int < 1:
                flash("Guest count must be at least 1.", "error")
                return redirect(url_for("places.booking", place_id=place_id))
        except (ValueError, TypeError):
            flash("Invalid guest count.", "error")
            return redirect(url_for("places.booking", place_id=place_id))

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            total_price = calculate_price(place, start_date_str, end_date_str, guest_count_int)

            new_booking = Booking(
                user_id=user_id,
                place_id=place_id,
                host_id=place.host_id,
                start_date=start_date,
                end_date=end_date,
                total_price=total_price,
                guest_count=guest_count_int,
                status="pending",
            )

            db.session.add(new_booking)
            db.session.commit()

            flash("Booking request sent! Awaiting host approval.", "success")
            return redirect(url_for("places.place", place_id=place_id))

        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("places.booking", place_id=place_id))

    return render_template("booking.html", place=place)



@places.route("/<place_id>")
def place(place_id):
    try:
        place = Place.query.options(
            joinedload(Place.photos),
        ).get_or_404(place_id)

        print(f"[DEBUG] Loaded place: {place.title}, current views: {place.views}")

        user = current_user if current_user.is_authenticated else None
        confirmed_booking = None

        if user:
            print(f"[DEBUG] Logged in user: {user.id} - {user.email}")
            confirmed_booking = Booking.query.filter_by(
                user_id=user.id, place_id=place.id, status="confirmed"
            ).first()
        else:
            print("[DEBUG] No authenticated user")

        # Call the view increment logic with the actual current_user
        place.increment_views(user=user)

        db.session.refresh(place)

        owner = User.query.get(place.host_id)
        if not owner:
            flash("⚠️ This listing no longer has a valid host account.", "warning")

        avg_rating = (
            db.session.query(func.avg(Review.rating))
            .filter(Review.place_id == place.id)
            .scalar()
        )
        avg_rating = round(avg_rating, 2) if avg_rating else None

        return render_template(
            "place.html",
            place=place,
            user=user,
            confirmed_booking=confirmed_booking,
            avg_rating=avg_rating,
            owner=owner,
        )

    except ObjectDeletedError:
        flash("This place or its owner has been removed.", "warning")
        return redirect(url_for('views.index'))



@places.route("/search", methods=["GET", "POST"])
def search_places():
    # Retrieve query parameters for GET request
    location = request.args.get("location")
    max_price = request.args.get("price")

    print(f"Location: {location}")
    print(f"Max Price: {max_price}")

    query = Place.query
    lat, lon = None, None
    radius_km = 20
    filtered_places = []
    places_list = []

    # Geocode location if provided
    if location:
        try:
            lat, lon = geocode_address(location)
        except Exception as e:
            print("Geocoding failed:", e)
            lat, lon = None, None

        def haversine(lat1, lon1, lat2, lon2):
            import math

            R = 6371
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (
                math.sin(dlat / 2) ** 2
                + math.cos(math.radians(lat1))
                * math.cos(math.radians(lat2))
                * math.sin(dlon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        if lat is not None and lon is not None:
            all_places = query.filter(
                Place.latitude.isnot(None),
                Place.longitude.isnot(None),
                Place.latitude != 0,
                Place.longitude != 0,
            ).all()
            filtered_places = [
                place
                for place in all_places
                if place.latitude
                and place.longitude
                and haversine(lat, lon, place.latitude, place.longitude) <= radius_km
            ]
            places_list = filtered_places
        else:
            flash(
                f"Could not geocode '{location}' (no network). Showing all places.",
                "warning",
            )
            places_list = (
                query.filter(
                    Place.latitude.isnot(None),
                    Place.longitude.isnot(None),
                    Place.latitude != 0,
                    Place.longitude != 0,
                )
                .order_by(Place.id.desc())
                .all()
            )
    else:
        places_list = (
            query.filter(
                Place.latitude.isnot(None),
                Place.longitude.isnot(None),
                Place.latitude != 0,
                Place.longitude != 0,
            )
            .order_by(Place.id.desc())
            .all()
        )

    # Apply price filter if provided
    if max_price:
        places_list = filter_by_price(places_list, max_price)

    places_json = [place.to_dict() for place in places_list]
    return render_template(
        "search_places.html", places=places_list, places_json=places_json
    )


def filter_by_price(places_list, max_price):
    try:
        max_price_value = float(max_price)
        print(f"Max Price Value: {max_price_value}")  # Debugging line
        filtered_places = [
            place for place in places_list if place.price <= max_price_value
        ]
        return filtered_places
    except ValueError:
        flash("Invalid price filter (must be a valid number).", "warning")
        return places_list



# --- Host CRUD and Photos ---


@places.route("/new", methods=["GET", "POST"])
@login_required
def new_place():
    amenities = Amenity.query.all()
    host = current_user  # Assuming the host is the currently logged-in user

    # Ensure the user is a host before allowing them to create a place
    if not current_user.is_authenticated or not current_user.type == "host":  # Check if the user is a host
        flash("You must become a host to create a place.", "error")
        return redirect(url_for("dashboard.become_host"))  # Redirect to become_host page

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        price = float(request.form["price"])
        latitude = float(request.form["latitude"])
        longitude = float(request.form["longitude"])
        capacity = int(request.form["capacity"])

        # Get selected amenities as a list of Amenity objects
        selected_amenities = Amenity.query.filter(
            Amenity.id.in_(request.form.getlist("amenities"))
        ).all()

        location = request.form.get("location", "").strip()
        address, city = "", ""
        if "," in location:
            last_comma = location.rfind(",")
            address = location[:last_comma].strip()
            city = location[last_comma + 1 :].strip()
        else:
            tokens = location.split()
            if len(tokens) >= 2:
                address = " ".join(tokens[:-1])
                city = tokens[-1]
            elif len(tokens) == 1:
                address = city = tokens[0]

        new_place = Place(
            title=title,
            description=description,
            price=price,
            latitude=latitude,
            longitude=longitude,
            capacity=capacity,
            host_id=host.id,
            amenities=selected_amenities,
            address=address,
            city=city,
        )

        db.session.add(new_place)
        db.session.commit()

        # Handle multiple photos upload
        photo_files = request.files.getlist("photos")
        for photo_file in photo_files:
            if photo_file and photo_file.filename != "":
                filename = save_photo(photo_file)
                place_photo = PlacePhoto(url=filename, place_id=new_place.id)
                db.session.add(place_photo)
        db.session.commit()

        
        flash("Place created!", "success")
        return redirect(url_for("places.place", place_id=new_place.id))

    return render_template("new_place.html", amenities=amenities)


@places.route("/host/places/<place_id>/edit", methods=["GET", "POST"])
@login_required
def edit_place(place_id):
    user = current_user
    place = Place.query.options(joinedload(Place.photos)).get_or_404(place_id)
    amenities = Amenity.query.all()

    if place.host_id != user.id:
        flash("You can't edit this place.")
        return redirect(url_for("dashboard.dashboard_view"))

    if request.method == "POST":
        place.title = request.form.get("title")
        place.description = request.form.get("description")
        place.price = float(request.form.get("price"))
        place.latitude = float(request.form.get("latitude"))
        place.longitude = float(request.form.get("longitude"))
        place.capacity = int(request.form.get("capacity"))

        selected_amenity_ids = request.form.getlist("amenities")
        place.amenities = Amenity.query.filter(Amenity.id.in_(selected_amenity_ids)).all()

        uploaded_files = request.files.getlist("photos")
        for file in uploaded_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                upload_folder = os.path.join(current_app.root_path, "static", "uploads")
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, unique_filename))
                photo = PlacePhoto(url=unique_filename, place=place)
                db.session.add(photo)

        db.session.commit()
        return redirect(url_for("dashboard.dashboard_view"))

    return render_template("edit_place.html", place=place, amenities=amenities)


@places.route("/host/places/<place_id>/delete", methods=["POST"])
@login_required
def delete_place(place_id):
    user = current_user


    host = Host.query.get(user.id) if user else None
    place = Place.query.get_or_404(place_id)
    if not host or place.host.id != host.id:
        flash("You can't delete this place.")
        return redirect(url_for("dashboard.dashboard_view"))
    db.session.delete(place)
    db.session.commit()

    
    return redirect(url_for("dashboard.dashboard_view"))








# --- Reviews ---


@places.route("/<place_id>/review", methods=["GET", "POST"])
@login_required
def leave_review(place_id):
    place = Place.query.get_or_404(place_id)

    user = current_user
    user_id = user.id

    confirmed_booking = Booking.query.filter_by(
        user_id=user_id, place_id=place.id, status="confirmed"
    ).first()
    if not confirmed_booking:
        flash("You can only review places you have confirmed bookings for.", "error")
        return redirect(url_for("places.place", place_id=place_id))

    existing_review = Review.query.filter_by(user_id=user_id, place_id=place.id).first()
    if existing_review:
        flash("You have already reviewed this place.", "error")
        return redirect(url_for("places.place", place_id=place_id))

    if request.method == "POST":
        text = request.form.get("content")
        rating = request.form.get("rating")

        if not text or not rating:
            flash("Please fill in all fields.", "error")
            return render_template("leave_review.html", place=place)

        try:
            rating_int = int(rating)
            if rating_int < 1 or rating_int > 5:
                raise ValueError()
        except ValueError:
            flash("Rating must be an integer between 1 and 5.", "error")
            return render_template("leave_review.html", place=place)

        review = Review(
            user_id=user_id,
            place_id=place.id,
            text=text,
            rating=rating_int,
        )
        db.session.add(review)
        db.session.commit()

        flash("Review submitted. Thank you!", "success")
        return redirect(url_for("places.place", place_id=place_id))

    return render_template("leave_review.html", place=place)







# --- API for Place Search (map, etc) ---


@places.route("/api", methods=["GET"])
def api_places():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    radius_km = request.args.get("radius", 20, type=float)  # Default radius of 20 km
    max_price = request.args.get("price", type=float)
    
    print(f"API Request - Lat: {lat}, Lon: {lon}, Radius: {radius_km}km")  # Debugging line
    
    query = Place.query
    filtered_places = []

    if lat and lon:
        # Filter places by radius using Haversine formula
        all_places = query.filter(
            Place.latitude.isnot(None),
            Place.longitude.isnot(None),
            Place.latitude != 0,
            Place.longitude != 0,
        ).all()
        filtered_places = [
            place for place in all_places
            if haversine(lat, lon, place.latitude, place.longitude) <= radius_km
        ]
    else:
        filtered_places = query.filter(
            Place.latitude.isnot(None),
            Place.longitude.isnot(None),
            Place.latitude != 0,
            Place.longitude != 0,
        ).all()

    # Apply price filter if provided
    if max_price is not None:
        filtered_places = [
            place for place in filtered_places if place.price <= max_price
        ]

    print(f"Filtered Places: {len(filtered_places)}")  # Debugging line
    places_json = [place.to_dict() for place in filtered_places]
    return jsonify(places_json)

