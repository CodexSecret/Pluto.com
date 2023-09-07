from User import *

class Admin(User):
    def __init__(self, name, gender, adminNo, password, email):
        super().__init__(name, gender, adminNo, password, email, user="Administrator")


