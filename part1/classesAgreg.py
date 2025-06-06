class Amenity:
    def __init__(self, id : int, name : str, description : str):
        self.__id = id
        self.__name = name
        self.__description = description

    def __str__(self):
        return self.__name

class Place:
    def __init__(self, id : int, name : str, address : str, description : str):
        self.__id = id
        self.__name = name
        self.__address = address
        self.__description = description
        self.__amenities =  []

    def __str__(self):
        strList = ', '.join(str(amenity) for amenity in self.__amenities)
        format = "Nom du lieu: {}\n" \
        "Adresse: {}\n" \
        "Description: {}\n" \
        "Commodités: {}\n".format(self.__name, self.__address, self.__description, strList)
        return format

    def add_amenities(self, amenity):
        self.__amenities.append(amenity)
