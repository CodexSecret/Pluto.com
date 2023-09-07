from User import *

class Teacher(User):
    def __init__(self, name, gender, adminNo, password, email, modules):
        super().__init__(name, gender, adminNo, password, email, user="Teacher")
        self.__modules = modules
    
    def set_modules(self, modules):
        self.__modules = modules
    
    def get_modules(self):
        return self.__modules

