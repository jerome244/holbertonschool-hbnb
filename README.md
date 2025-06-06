```
classDiagram
    User <|-- Host
    UserIdentity --* User
    Host "1" --> "1.." Place : owns
    User "1" --> "0.." Review : leaves
    User "1" --> "0.." Booking : makes
    Review "0..1" --> "1" Booking : concerns
    Place "1" <--> "0.." Booking
    Place o-- "0.." Amenity : features
    class User{
        - int id
        - datetime dateCreation
        - datettime dateUpdate
        - bool isAdmin
        - UserIdentity uId
        + makeBooking(booking)
        + get()
        + set()
    }
    class UserIdentity{
        - string firstName
        - string lastName
        - String dateOfBirth
        - string address
        - string phoneNumber
        + get()
        + set()
    }
    class Host{
        - int rating
        + getPlaces()
        + editPlace()
    }
    class Place{
        - int Id
        - string name
        - string address
        - string description
        - int rating
        - int capacity
        - int pricePerNight
        - List amenities
        + addAmenity(amenity)
        + getAvailability()
        + get()
        + set()
    }
    class Review{
        - int id
        - int rating
        - string comment
        - datetime date
        + get()
        + set()
    }
    class Booking{
        - int id
        - int guestCount
        - int totalPrice
        - string status
        + get()
        + set()
    }
    class Amenity{
        - int id
        - string name
        - string description
        - string icon
        + get()
        + set()
    }


```
