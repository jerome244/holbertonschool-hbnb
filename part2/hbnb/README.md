# HBnB Project - Part 2 - API and Business Logic

---

# Scope of the Project
In this phase of the Hbnb project, we focused on building the `Presentation and Business Logic layers` using `Python` and `Flask`. We defined the core functionality by creating the necessary classes, methods, and endpoints that will define the foundation of the **HBnB application**.

We structured the project by first developing the business logic classes upon which we implemented the API endpoints to build a robust and scalable skeleton for further implementation of the project. Our work included setting up essential features such as managing `users`, `places`, `reviews`, `bookings` and `amenities`, while following best practices in `RESTful API design`.

---

## Structure Description
The project structure will be laid out ad follow:

```
hbnb/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── users.py
│   │   │   ├── places.py
│   │   │   ├── reviews.py
│   │   │   ├── amenities.py
│   │   │   ├── bookings.py
│   │   │   ├── host.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── base.py
│   │   ├── place.py
│   │   ├── review.py
│   │   ├── amenity.py
│   │   ├── booking.py
│   │   ├── host.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── facade.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── repository.py
│   ├── tests/
│   │   ├── test_classes.py
├── run.py
├── config.py
├── requirements.txt
├── README.md

```

`hbnb/`
Directory for the whole project; it contains the following
- `run.py` : The entry point of the app
- `config.py` : Config file of the app
- `requirements.txt` : Text file contains a list of the app's dependencies
- `README.md` : The documentation of the project you're hopefully enjoying to read.

`hbnb/app/api/v1`
Contains the API endpoint, organised by version.

`hbnb/app/models`
Contains the classes describing relevant business entities such as:</br>
- `base.py` : Parent of all classes in this project. Used to give everyone of its children **id**, **created_at** and **updated_at** attributes
- `user.py` : Describes an user of the app.
- `host.py` : Describes a place's owner. Inherits from the User class.
- `booking.py` : Describes a booking made by a user concerning a place.
- `place.py` : Describes the service provided by the hosts in the form of an accomodation.
- `review.py` : Describes a review left by an user describing his feelings towards a booking.
- `amenity.py` : Describes extra services provided by the host in the form of amenities.</br>

`hbnb/app/services`
Contains `facede.py` that implements the Facade pattern describing layers and components interactions.

`hbnb/app/persistence`
Contains `repository.py` that allows in memory persistence and serves as a placeholder for the future database integration.


## Building the Business Logic Layer

The **Business Logic Layer** represented by classes used to abstract and describe relevant **Business Entities** to the functioning of the app.

As a rule of thumb, attributes of the classes described below will be private and be accessed and updated through getters (``@property``) and setters (``@attribute.setter``) to ensure data integrity.</br>
Their behavior in relation to one another is described by the Class diagram from the previous part of the project. They will be elaborated on a little bit later.

### Classes Presentation

**Base Class**

- `id` (UUID): Unique identifier for each object instance.
- `created_at` (DateTime): Timestamp when the object is created.
- `updated_at` (DateTime): Timestamp when the object is last updated.

```python
class BaseModel:
    def __init__(self, id=None, created_at=None, updated_at=None):
        self.__id = id or str(uuid.uuid4())
        self.__created_at = created_at or datetime.now()
        self.__updated_at = updated_at or datetime.now()
```

---

**User Class** (inherits from Base)

- `first_name` (String): The first name of the user. Required, maximum length of 50 characters.
- `last_name` (String): The last name of the user. Required, maximum length of 50 characters.
- `email` (String): The email address of the user. Required, must be unique, and should follow standard email format validation.
- `is_admin` (Boolean): Indicates whether the user has administrative privileges. Defaults to `False`.</br>
***Additional attribute***</br>
- `bookings` (List[Booking]): List of bookings made by the user. Appended automatically with given booking on creation.

```python
class User(BaseModel):
    def __init__(self, first_name, last_name, email, is_admin=False, **kwargs):
        super().__init__(**kwargs)
        self.__first_name = first_name
        self.__last_name = last_name
        self.email = email
        self.__is_admin = is_admin
        self.__bookings = []

```

---

**Host Class** (inherits from User)

- `owned_places` (List[Place]): A list of `Place` instances owned by the host. Defaults to an empty list if not provided.
- `rating` (Float): The host's average rating, calculated from guest reviews. Calculated with the average of every place's booking's reviews from `owned_places`.

```python
class Host(User):
    def __init__(self, first_name, last_name, email, owned_places=None, **kwargs):
        super().__init__(first_name, last_name, email, **kwargs)
        self.__rating = None
        self.__owned_places = owned_places if owned_places is not None else []
```

---

**Booking Class** (inherits from Base)

- `guest_count` (Integer): Number of guests included in the booking. Must be a positive value.
- `checkin_date` (DateTime): Date and time when the guest checks in.
- `night_count` (Integer): Total number of nights booked. Must be a positive integer.
- `place` (Place): The `Place` instance being booked. Must be validated to ensure the place exists.
- `user` (User): The `User` who made the booking. Must be validated to ensure the user exists.</br>
***Additional attributes:***</br>
- `total_price` (Integer) : Calculated by multiplying ``night_count`` by ``place.price``
- `chechout_date` (DateTime) : Calculated by adding `night_count` to `checkin_date`
- `rating` (Integer) : Rating from user's review.
- `review` (Review) : user's review concerning this booking.

```python
class Booking(BaseModel):
    def __init__(self, guest_count, checkin_date, night_count, place, user, **kwargs):
        super().__init__(**kwargs)
        self.__place = place
        self.__guest_count = guest_count
        self.checkin_date = checkin_date
        self.__night_count = night_count
        self.__user = user

        self.__total_price = self.night_count * self.__place.price
        self.__checkout_date = self.checkin_date + timedelta(days=self.night_count)
        self.__rating = None
        self.__review = None

        user.add_booking(self)
```

---

**Place Class** (inherits from Base)

- `title` (String): The title of the place. Required, maximum length of 100 characters.
- `description` (String): Detailed description of the place. Optional.
- `price` (Float): The price per night for the place. Must be a positive value.
- `latitude` (Float): Latitude coordinate for the place location. Must be within the range of -90.0 to 90.0.
- `longitude` (Float): Longitude coordinate for the place location. Must be within the range of -180.0 to 180.0.
- `host` (Host): Instance of place's user. Must be validated to ensure the owner exists.</br>
***Additional attributes:***</br>
- `amenities` (List[Amenity]) : List of a given place amenities.
- `reviews` (List[Review]) : List of reviews left by users on bookings related to this place.

```python
class Place(BaseModel):
    def __init__(self, title, capacity, price, latitude, longitude, host, description="", **kwargs):
        super().__init__(**kwargs)
        self.__title = title
        self.__capacity = capacity
        self.__price = price
        self.__latitude = latitude
        self.__longitude = longitude
        self.__host = host
        self.__description = description

        self.__amenities = []
        self.__reviews = []
```

---

**Review Class** (inherits from Base)

- `booking` (Booking): Booking object that is reviewed.
- `text` (String): The content of the review. Required.
- `rating` (Integer): Rating given to the place. Must be between 1 and 5.</br>
***Additional methods:***</br>
- `booking.review = self` : Is a method (looking like an assignation thank to decorator) that when Review constructor is called, <span style="color:#fc8a5d">assigns the created review object as the review of the booking passed in parameter.</span>
- `booking.place.add_review(self)` : Method called when Review object creator is called. <span style="color:#fc8a5d">Adds created review object to the place object that is concerned by the booking object passed as parameter.</span>

```python
class Review(BaseModel):
    def __init__(self, booking, text, rating=None, **kwargs):
        super().__init__(**kwargs)
        self.__booking = booking
        self.__text = text
        self.__rating = rating

        booking.review = self
        booking.place.add_review(self)
```

---

**Amenity Class** (inherits from Base)

- `name` (String): The name of the amenity (e.g., "Wi-Fi", "Parking"). Maximum length of 50 characters.

```python
class Amenity(BaseModel):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.__name = name
```

---

### Important functional class relationships:

Below is a list of important associations between classes that will be carefully implemented to enforce a solid base for the app and to ensure persistent data integrity.
The associations will be enfored either with method calls from within the objects constructors or by using conditions and exceptions to validate data relevance be it within object constructors or inside attribute setters.

#### <ins>A booking object must have only one review</ins>
```python
@review.setter
    def review(self, review):
        if self.__review:
            raise ValueError("This Booking already has a review")
        self.__review = review
```
In the above code, in the object constructor of the class `Booking`, `self.__review` vas initialised to `None`. Then, in `@review.setter` we check if `self.__review` has already been set, if it was, raise ValueError.
Otherwise, sets `self.__review` to passed review object.
#### <ins>A booking object must concern only one place object</ins>
In the object constructor of the `Booking` class, we initialise `self.__place = place`, then pass the created `booking` object as parameter of `place.add_booking()`
```python
self.__place = place
place.add_booking(self)
```
Then, in the `Place` class:
```python
def add_booking(self, booking):
        if booking not in self.__bookings:
            self.__bookings.append(booking)
```
We check if this specific booking object does not already exist in `place.__boookings`, if it doesn't, we append it.
#### <ins>A place object must be owned by a host</ins>
```python
if hasattr(host, "add_place") and isinstance(host, Host):
            host.add_place(self)
        self.__host = host
```
The above code is from the `Place` class object constructor. When creating a `place` object, an `host` object is passed as attribute. The `place` object created is then passed as an argument to `host.add_place()` appending it to `host.owned_places[]`. Furthermore, we check if passed argument is indeed of the type `Host` and that it contains the method `add_place`

## Building RESTful API Endpoints



## Testing and Validating

### Testing Model Classes

Classes and their methods and attributes are tested in the file `app/tests/test_classes.py`.
The following function calls are used to test every attribute, and every methods of every classes:


**The below code should be run from ``/hbnb`` with ``python -m app.tests.test_classes``**


```python
if __name__ == "__main__":
    test_user()
    test_host()
    test_place()
    test_booking()
    test_review()

    print("\n#------- Testing validation -------#\n")

    test_invalid_email_format()
    test_invalid_guest_count()
    test_invalid_checkin_date()
    test_two_reviews_one_booking()
```
The output is as follow:
```sh
$ python test_classes.py
User creation test passed!
Host creation test passed!
Place creation test passed!
Booking creation test passed!
Review creation test passed!

#------- Testing validation -------#

Email went through validation and raised Value Error
Guest Count exceeded Place capacity and raised Value Error
Checkin date is in the past and raised Value Error
More than one review was added to a given booking and raised Value Error
```
No error message, meaning every test went through as asserted values are as expected.

### Testing API Endpoints and HTTP Methods

---
Authors - [DESSAIGNE Théo](https://github.com/Theo-D) & [TRAN Jérôme](https://github.com/jerome244)
