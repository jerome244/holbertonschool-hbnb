#!/usr/bin/python3
from datetime import datetime, timedelta
import pytest

Amenity = __import__("amenity").Amenity
User = __import__("user").User
Booking = __import__("booking").Booking
Host = __import__("host").Host
Place = __import__("place").Place
Review = __import__("review").Review


# --- Test: User --- #
def test_user():
    user = User(
        first_name="Marcel", last_name="Vincent", email="marcel.vincent@gmail.com"
    )
    assert user.first_name == "Marcel"
    assert user.last_name == "Vincent"
    assert user.email == "marcel.vincent@gmail.com"
    assert user.is_admin is False
    assert user.bookings == []
    assert abs(user.created_at - datetime.now()) < timedelta(seconds=1)
    assert abs(user.updated_at - datetime.now()) < timedelta(seconds=1)
    print("User creation test passed!")


# --- Test: Host --- #
def test_host():
    host = Host(
        first_name="Fabien", last_name="Roussel", email="saucissonetpinard@gmail.com"
    )
    place = Place(
        title="Siège du PCF",
        capacity=4,
        price=150.0,
        latitude=45.0,
        longitude=-120.0,
        host=host,
        description="An avant-garde building",
    )
    assert host.first_name == "Fabien"
    assert host.last_name == "Roussel"
    assert host.email == "saucissonetpinard@gmail.com"
    assert host.owned_places == [place]
    assert host.rating == 0
    assert abs(host.created_at - datetime.now()) < timedelta(seconds=1)
    assert abs(host.updated_at - datetime.now()) < timedelta(seconds=1)
    print("Host creation test passed!")


# --- Test: Place --- #
def test_place():
    host = Host(first_name="Oui", last_name="Oui", email="ouioui@outlook.fr")
    userPlace = User(first_name="Jean", last_name="Jean", email="juanitodu34@gmail.com")
    place = Place(
        title="Maison Champignon",
        capacity=4,
        price=150.0,
        latitude=45.0,
        longitude=-120.0,
        host=host,
        description="A mushroom house",
    )
    checkin_date = datetime.today() + timedelta(days=3)
    booking = Booking(
        guest_count=2,
        checkin_date=checkin_date,
        night_count=3,
        place=place,
        user=userPlace,
    )
    text = "Not bad, not bad at all."
    amenity1 = Amenity("Bidet")
    # When review1 is created it is added to booking and appended
    # to Place.reviews[]
    review1 = Review(booking, text)
    place.add_amenity(amenity1)
    assert place.title == "Maison Champignon"
    assert place.capacity == 4
    assert place.price == 150.0
    assert place.latitude == 45.0
    assert place.longitude == -120.0
    assert place.host == host
    assert place.description == "A mushroom house"
    assert place.amenities == [amenity1]
    # The review is added automatically to the Place.reviews at creation of review1
    assert place.reviews == [review1]
    assert abs(place.created_at - datetime.now()) < timedelta(seconds=1)
    assert abs(place.updated_at - datetime.now()) < timedelta(seconds=1)
    print("Place creation test passed!")


# --- Test: Booking --- #
def test_booking():
    host = Host(first_name="René", last_name="Causse", email="tonpere@wanadoo.com")
    user1 = User(first_name="Jean", last_name="Jean", email="juanitodu34@gmail.com")
    place = Place(
        title="Maison Champignon",
        capacity=4,
        price=150.0,
        latitude=45.0,
        longitude=-120.0,
        host=host,
        description="A mushroom house",
    )
    checkin_date = datetime.today() + timedelta(days=3)
    booking = Booking(
        guest_count=2, checkin_date=checkin_date, night_count=3, place=place, user=user1
    )
    assert booking.guest_count == 2
    assert booking.checkin_date == checkin_date
    assert booking.night_count == 3
    assert booking.total_price == 450
    assert booking.checkout_date == checkin_date + timedelta(days=3)
    assert booking.review is None
    assert abs(booking.created_at - datetime.now()) < timedelta(seconds=1)
    assert abs(booking.updated_at - datetime.now()) < timedelta(seconds=1)
    print("Booking creation test passed!")


def test_review():
    hostReview = Host(first_name="Oui", last_name="Oui", email="ouioui@outlook.fr")

    placeReview = Place(
        title="Maison Champignon",
        capacity=4,
        price=150.0,
        latitude=45.0,
        longitude=-120.0,
        host=hostReview,
        description="A mushroom house",
    )
    checkin_date = datetime.today() + timedelta(days=3)
    night_count = 3
    userReview = User(
        first_name="Jean", last_name="Jean", email="juanitodu34@gmail.com"
    )
    booking = Booking(
        guest_count=2,
        checkin_date=checkin_date,
        night_count=night_count,
        place=placeReview,
        user=userReview,
    )

    text = "Very nice except for the dude chasing us and trying to make us eat saucisson and drink pinard. Pretty cringe if you ask me"

    review = Review(booking=booking, text=text, rating=5)

    assert review.booking == booking
    assert (
        review.text
        == "Very nice except for the dude chasing us and trying to make us eat saucisson and drink pinard. Pretty cringe if you ask me"
    )
    assert review.rating == 5
    assert abs(review.created_at - datetime.now()) < timedelta(seconds=1)
    assert abs(review.updated_at - datetime.now()) < timedelta(seconds=1)
    print("Review creation test passed!")


# --- Test: Amenity --- #


def test_amenity():
    amenity = Amenity(name="Wi-Fi")
    assert amenity.name == "Wi-Fi"
    assert abs(amenity.created_at - datetime.now()) < timedelta(seconds=1)
    assert abs(amenity.updated_at - datetime.now()) < timedelta(seconds=1)
    print("Amenity creation test passed!")


def test_invalid_email_format():
    try:
        User(first_name="Frank", last_name="Zappa", email="+33 9 89 52 47 12")
    except ValueError as e:
        assert str(e) == "Email must have valid mail address format"
        print("Email went through validation and raised Value Error")
    else:
        pytest.fail("Expected ValueError for invalid email format")
        print("Email went through validation successfully")


def test_invalid_guest_count():
    # guest_count = 5 and Place.capacity = 4 should raise ValueError
    try:
        checkin_date = datetime.now() + timedelta(
            days=5
        )  # Make sure date is 5 days from whenever this is tested
        host = Host(first_name="Oui", last_name="Oui", email="ouioui@outlook.fr")
        place = Place(
            title="Maison Champignon",
            capacity=4,
            price=150.0,
            latitude=45.0,
            longitude=-120.0,
            host=host,
            description="A mushroom house",
        )
        user = User(first_name="Jean", last_name="Jean", email="juanitodu34@gmail.com")
        Booking(
            guest_count=5,
            checkin_date=checkin_date,
            night_count=3,
            place=place,
            user=user,
        )
    except ValueError as e:
        assert str(e) == f"Number of guests exceeds {place.title}'s capacity"
        print("Guest Count exceeded Place capacity and raised Value Error")
    else:
        pytest.fail("Expected ValueError from guests' overflow")
        print("Guest count did not exceed place capacity")


def test_invalid_checkin_date():
    try:
        checkin_date = datetime.now() - timedelta(days=5)  # Corrected
        host = Host(first_name="Oui", last_name="Oui", email="ouioui@outlook.fr")
        place = Place(
            title="Maison Champignon",
            capacity=4,
            price=150.0,
            latitude=45.0,
            longitude=-120.0,
            host=host,
            description="A mushroom house",
        )
        user = User(first_name="Jean", last_name="Jean", email="juanitodu34@gmail.com")
        Booking(
            guest_count=3,
            checkin_date=checkin_date,
            night_count=3,
            place=place,
            user=user,
        )
    except ValueError as e:
        assert str(e) == "Checkin_date must be later than today"
        print("Checkin date is in the past and raised Value Error")
    else:
        pytest.fail("Expected ValueError for checkin date being in the past")


if __name__ == "__main__":
    test_user()
    test_host()
    test_place()
    test_booking()
    test_review()

    print("\n#------- Testing setter validation -------#\n")

    test_invalid_email_format()
    test_invalid_guest_count()
    test_invalid_checkin_date()
