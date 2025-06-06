class UserIdentity:
    def __init__(self, firstName, lastName, dateOfBirth, address, phoneNumber):
        self.__firstName = firstName
        self.__lastName = lastName
        self.__address = address
        self.__dateOfBirth = dateOfBirth
        self.__phoneNumber = phoneNumber

    def __str__(self):
        format = "L'utilisateur {} {} est né le {} à {}".format(
            self.__firstName,
            self.__lastName,
            self.__dateOfBirth,
            self.__address)
        return format

class User:
    def __init__(self, id, dateCreation, dateUpdate, isAdmin, userIdentity):
        self.__id = id
        self.__dateCreation = dateCreation
        self.__dateUpdate = dateUpdate
        self.__isAdmin = isAdmin
        self.__userIdentity = userIdentity

    def __str__(self):
        return str(self.__userIdentity)
