### Class diagram [<a href="https://mermaid.js.org/syntax/classDiagram.html">docs</a> - <a href="[https://mermaid.live/edit#pako:eNpdkTFPwzAQhf-K5QlQ2zQJJG1UBaGWDYmBgYEwXO1LYuTEwXYqlZL_jt02asXm--690zvfgTLFkWaUSTBmI6DS0BTt2lfzkKx-p1PytEO9f1FtdaQkI2ulZNGuVqK1qEtgmOfk7BitSzKdOhg59XuNGgk0RDxed-_IOr6uf8cZ6UhTZ8bvHqS5ub1mr9svZPbjk6DEBlu7AQuXyBkx4gcvDk9cUMJq0XT_YaW0kNK5j-ufAoRzcihaQvLcoN4Jv50vvVxw_xrnD3RCG9QNCO4-8OgpqK1dpoJm7smxhF7agp6kfcfB4jMXVmmalW4tnFDorXrbt4xmVvc4is53GKFUwNF5DtTuO3-sShjrJjLVlqLyvNfS4drazmRB4NuzSti6386YagIjeA3a1rtlEiRRsoAoxiSN4SGOOduGy0UZ3YclT-dhBHQYhj8dc6_I](https://mermaid.live/edit#pako:eNqdVd9vmzAQ_leQn7otIeFHIUHVpLabtEpTV63qy5QXBxuwChjZJl3W5n_f2UAKCW238pCY-z7ffXe-M48o5oSiCMU5lvILw6nAxaq04LmTVFhnT9Op9Y1L9Wy7IrRUTG2t6fSjMTSQJlkr5KwQAJ_1yrZhfZPjmFqRxR9K2fPbJ84N8SfdMPoAzJziDX2de8H5PStTIBf4vuO2Dgynp2JAj3kZU9EpabQ1nLMR_30Whzp08HlBS12AyEooVrXoFJgaGs2PjUE_U4uVymKkbyFYUcUKahaXApwwXh4R9oy7Sv_28TXnucXkOSnYYN_gfOqrXtBPplRtYifr5v9DH0-pOhkY5LNhd5hgF2SQqFRClzlhQqprXNARDBwcQbcNpHP8kVwwobKRjZgQqLMcQaqMl_S6LtZdJ_5nOrpxj85LwJF0DbD3ZzpBDr1Swhr7qG-DHDm_IiNplOMFezlvQmUsWHXYOmPqG2uMKxzDmR3aK8FiekPFNUsz1Qe_MxhpbJqdUdnPGlS1Q3DS4NvDVjrfYJbjNcs153191gz0G6M0nm5bopgXoE69OHrvktXO0D_oSmsq1SWvhwo0orjC-Y2u-4hqqeBSke_S1h7KG9pe77gX-qpFWdw3vykNTVAqGEGREjWdoIKKAutXZCSukMooiEARLAkW9yu0Knewp8LlL86LbpvgdZqhKMG5hLfaXIftt2pvFbQkVJhqo8h3jQ8UPaLfKHKDhR0uvGUQzAPfP_WcCdqiaOp59tz3gzAMPd8LT3cT9MfEdGzXc0PP85YLZwE7nKCL-RWGnYt9SFwrfrst405mzjFI0EHVttIf1RQGCLKBkiUs1fZa5GDOlKpkNJtp2E6Zyuq1Da06k4xkGK6_zTKYBSAaux4NQg-feh6J185ykbi-k5Bw7rgY7Xa7v18FONI)">live editor</a>]

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
