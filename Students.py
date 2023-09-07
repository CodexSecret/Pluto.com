from User import *

class Student(User):
    def __init__(self, name, gender, adminNo, password, email, birthDate):
        super().__init__(name, gender, adminNo, password, email, user="Student")
        self.__birthDate = birthDate

    def set_birthDate(self, birthDate):
        self.__birthDate = birthDate

    def get_birthDate(self):
        return self.__birthDate
    

    

        