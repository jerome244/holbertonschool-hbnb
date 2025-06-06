### Class diagram [<a href="https://mermaid.js.org/syntax/classDiagram.html">docs</a> - <a href="https://mermaid.live/edit#pako:eNpNkctuwjAQRX8lmlUrQYLzjheVykPqolIlyqqEhYmdxGpiI8cp0JB_rw2i7aw89_rO0dgDFJIywFA28ljURGnndZ0Lx9Tz9oUounOm06fLhp30xZk_rGUv6OPNn1vHWQxLVvCOSzHe5MU18CbYxVlu16zrG-2g3X9vc5QXZ3X3_B1MoFKcAtaqZxNomWqJbWGwqRx0zVqWAzZHStRnDrkYTeZAxIeU7T2mZF_VgEvSdKbrD5RotuSkUuTvChOUqYXZQQMO4-sIwAOcAE9j5EbBLE4zP8iiGcqiCZwBozByk2icwPeVNHPTJMxMJQFKwyDO0J20olxL9YsnvZbvZ1HcyY0khmxZ-nywz13xTpsdCilKXlm9V42Ra60PHfY8a7sV13W_dwvZeh2n9m_qryz2Yj9OiR-wOAlIFAS02KMsLf0QlTSZIZ_AOI4__6CStw">live editor</a>]

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
