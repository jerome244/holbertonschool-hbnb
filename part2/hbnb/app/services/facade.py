# app/services/facade.py

from datetime import datetime
from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.host import Host
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
from app.models.booking import Booking

class HBnBFacade:
    def __init__(self):
        self.user_repo    = InMemoryRepository()
        self.host_repo    = InMemoryRepository()
        self.place_repo   = InMemoryRepository()
        self.review_repo  = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self.booking_repo = InMemoryRepository()

    # ----------- USERS -----------
    def create_user(self, data):
        if self.user_repo.get_by_attribute('email', data['email']):
            raise ValueError(f"Email '{data['email']}' is already in use")
        u = User(
            first_name=data['first_name'],
            last_name =data['last_name'],
            email     =data['email'],
            is_admin  =data.get('is_admin', False)
        )
        self.user_repo.add(u)
        return {
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'is_admin': u.is_admin
        }

    def get_all_users(self):
        return [self.get_user(u.id) for u in self.user_repo.get_all()]

    def get_user(self, uid):
        u = self.user_repo.get(uid)
        if not u:
            raise KeyError(f"User not found: {uid}")
        return {
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'is_admin': u.is_admin
        }

    def update_user(self, uid, data):
        u = self.user_repo.get(uid)
        if not u:
            raise KeyError(f"User not found: {uid}")
        if 'email' in data and data['email'] != u.email \
           and self.user_repo.get_by_attribute('email', data['email']):
            raise ValueError(f"Email '{data['email']}' is already in use")
        for fld in ('first_name','last_name','email','is_admin'):
            if fld in data:
                setattr(u, fld, data[fld])
        u.updated_at = datetime.now()
        return self.get_user(uid)

    def delete_user(self, uid):
        if not self.user_repo.get(uid):
            raise KeyError(f"User not found: {uid}")
        self.user_repo.delete(uid)

    # ----------- HOSTS -----------
    def create_host(self, data):
        if self.host_repo.get_by_attribute('email', data['email']):
            raise ValueError(f"Email '{data['email']}' already in use")
        h = Host(
            first_name=data['first_name'],
            last_name =data['last_name'],
            email     =data['email']
        )
        self.host_repo.add(h)
        return {
            'id': h.id,
            'first_name': h.first_name,
            'last_name': h.last_name,
            'email': h.email
        }

    def get_all_hosts(self):
        return [self.get_host(h.id) for h in self.host_repo.get_all()]

    def get_host(self, hid):
        h = self.host_repo.get(hid)
        if not h:
            raise KeyError(f"Host not found: {hid}")
        return {
            'id': h.id,
            'first_name': h.first_name,
            'last_name': h.last_name,
            'email': h.email
        }

    def update_host(self, hid, data):
        h = self.host_repo.get(hid)
        if not h:
            raise KeyError(f"Host not found: {hid}")
        if 'email' in data and data['email'] != h.email \
           and self.host_repo.get_by_attribute('email', data['email']):
            raise ValueError(f"Email '{data['email']}' already in use")
        for fld in ('first_name','last_name','email'):
            if fld in data:
                setattr(h, fld, data[fld])
        h.updated_at = datetime.now()
        return self.get_host(hid)

    def delete_host(self, hid):
        if not self.host_repo.get(hid):
            raise KeyError(f"Host not found: {hid}")
        self.host_repo.delete(hid)

    # ----------- PLACES -----------
    def create_place(self, data):
        host = self.host_repo.get(data['host_id'])
        if not host:
            raise KeyError(f"Host not found: {data['host_id']}")
        p = Place(
            title=data['title'],
            capacity=data['capacity'],
            price=data['price'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            description=data.get('description', ""),
            host=host
        )
        self.place_repo.add(p)
        return self.get_place(p.id)

    def get_all_places(self):
        return [self.get_place(p.id) for p in self.place_repo.get_all()]

    def get_place(self, pid):
        p = self.place_repo.get(pid)
        if not p:
            raise KeyError(f"Place not found: {pid}")
        return {
            'id': p.id,
            'title': p.title,
            'capacity': p.capacity,
            'price': p.price,
            'latitude': p.latitude,
            'longitude': p.longitude,
            'description': p.description,
            'host_id': p.host.id
        }

    def update_place(self, pid, data):
        p = self.place_repo.get(pid)
        if not p:
            raise KeyError(f"Place not found: {pid}")
        if 'host_id' in data and data['host_id'] != p.host.id:
            new_h = self.host_repo.get(data['host_id'])
            if not new_h:
                raise KeyError(f"Host not found: {data['host_id']}")
            p.host = new_h
        for fld in ('title','capacity','price','latitude','longitude','description'):
            if fld in data:
                setattr(p, fld, data[fld])
        p.updated_at = datetime.now()
        return self.get_place(pid)

    def delete_place(self, pid):
        if not self.place_repo.get(pid):
            raise KeyError(f"Place not found: {pid}")
        self.place_repo.delete(pid)

    # ----------- REVIEWS -----------
    def add_review(self, pid, data):
        p = self.place_repo.get(pid)
        if not p:
            raise KeyError(f"Place not found: {pid}")
        r = Review(
            user_id=data['user_id'],
            rating=data['rating'],
            comment=data.get('comment', "")
        )
        self.review_repo.add(r)
        p.add_review(r)
        return {
            'id': r.id,
            'user_id': r.user_id,
            'rating': r.rating,
            'comment': r.comment
        }

    def get_reviews(self, pid):
        p = self.place_repo.get(pid)
        if not p:
            raise KeyError(f"Place not found: {pid}")
        return [
            {'id': r.id, 'user_id': r.user_id, 'rating': r.rating, 'comment': r.comment}
            for r in p.reviews
        ]

    def delete_review(self, review_id):
        r = self.review_repo.get(review_id)
        if not r:
            raise KeyError(f"Review not found: {review_id}")
        for p in self.place_repo.get_all():
            if r in p.reviews:
                p.reviews.remove(r)
                break
        self.review_repo.delete(review_id)

    # ----------- AMENITIES -----------
    def create_amenity(self, data):
        a = Amenity(name=data['name'])
        self.amenity_repo.add(a)
        return {'id': a.id, 'name': a.name}

    def get_all_amenities(self):
        return [{'id': a.id, 'name': a.name} for a in self.amenity_repo.get_all()]

    def delete_amenity(self, aid):
        a = self.amenity_repo.get(aid)
        if not a:
            raise KeyError(f"Amenity not found: {aid}")
        for p in self.place_repo.get_all():
            if a in p.amenities:
                p.amenities.remove(a)
        self.amenity_repo.delete(aid)

    def add_amenity(self, pid, aid):
        p = self.place_repo.get(pid)
        a = self.amenity_repo.get(aid)
        if not p:
            raise KeyError(f"Place not found: {pid}")
        if not a:
            raise KeyError(f"Amenity not found: {aid}")
        p.add_amenity(a)
        return {'place_id': pid, 'amenity_id': aid, 'name': a.name}

    def get_amenities(self, pid):
        p = self.place_repo.get(pid)
        if not p:
            raise KeyError(f"Place not found: {pid}")
        return [{'id': a.id, 'name': a.name} for a in p.amenities]

    # ----------- AVERAGE RATING -----------
    def get_average_rating(self, pid):
        p = self.place_repo.get(pid)
        if not p:
            raise KeyError(f"Place not found: {pid}")
        return {'place_id': pid, 'avg_rating': p.get_average_rating()}

    # ----------- BOOKINGS -----------
    def create_booking(self, data):
        p = self.place_repo.get(data['place_id'])
        if not p:
            raise KeyError(f"Place not found: {data['place_id']}")
        try:
            ch = datetime.fromisoformat(data['checkin_date'])
        except Exception:
            raise ValueError("checkin_date must be ISO8601 string")
        b = Booking(
            guest_count=data['guest_count'],
            checkin_date=ch,
            night_count=data['night_count'],
            place=p
        )
        self.booking_repo.add(b)
        return {
            'id': b.id,
            'place_id': p.id,
            'guest_count': b.guest_count,
            'checkin_date': b.checkin_date.isoformat(),
            'night_count': b.night_count,
            'total_price': b.total_price
        }

    def get_all_bookings(self):
        return [self.get_booking(b.id) for b in self.booking_repo.get_all()]

    def get_booking(self, bid):
        b = self.booking_repo.get(bid)
        if not b:
            raise KeyError(f"Booking not found: {bid}")
        return {
            'id': b.id,
            'place_id': b.place.id,
            'guest_count': b.guest_count,
            'checkin_date': b.checkin_date.isoformat(),
            'night_count': b.night_count,
            'total_price': b.total_price
        }

    def update_booking(self, bid, data):
        b = self.booking_repo.get(bid)
        if not b:
            raise KeyError(f"Booking not found: {bid}")
        if 'guest_count' in data:
            b.guest_count = data['guest_count']
        if 'night_count' in data:
            b.night_count = data['night_count']
            b._Booking__total_price = b.night_count * b._Booking__place.price
        if 'checkin_date' in data:
            try:
                b._Booking__checkin_date = datetime.fromisoformat(data['checkin_date'])
            except Exception:
                raise ValueError("checkin_date must be ISO8601 string")
        b.updated_at = datetime.now()
        return self.get_booking(bid)

    def delete_booking(self, bid):
        if not self.booking_repo.get(bid):
            raise KeyError(f"Booking not found: {bid}")
        self.booking_repo.delete(bid)

# singleton instance
facade = HBnBFacade()
