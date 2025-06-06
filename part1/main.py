#!/usr/bin/python3
from classesAgreg import Amenity, Place
from classesComp import UserIdentity, User

if __name__ == '__main__':

    place1 = Place(1, "Siège du PCF", "2, place du Colonel-Fabien", "Un bâtiment avant-gardiste")

    userId = UserIdentity("Thierry", "Martin", "22 avril 1970", "Clermont-Ferrand", "+33 6 75 58 12 12")
    user1 = User(1, "06/06/2025", "06/06/2025", True, userId)

    """ amenity1 = Amenity(1, "micro onde", "ne pas y sécher le chien")
    amenity2 = Amenity(2, "sèche cheveux", "peut servir à sécher le chien")
    amenity3 = Amenity(3, "wifi", "code wifi: Octore1917")

    place1.add_amenities(amenity1)
    place1.add_amenities(amenity2)
    place1.add_amenities(amenity3) """

    print(place1, end="")

    print("_" * 50)
    print()

    print(user1)
