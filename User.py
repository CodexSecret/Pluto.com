from datetime import date

today = date.today()

class User:
    def __init__(self, name, gender, adminNo, password, email, user):
        self.__name = name
        self.__gender = gender
        self.__adminNo = adminNo
        self.__password = password
        self.__email = email
        self.__user = user
        self.__dateJoined = today.strftime('%d/%m/%Y')

    def set_name(self, name):
        self.__name = name
    def set_gender(self, gender):
        self.__gender = gender
    def set_adminNo(self, adminNo):
        self.__adminNo = adminNo
    def set_password(self, password):
        self.__password = password
    def set_email(self, email):
        self.__email = email
    
    def get_name(self):
        return self.__name
    def get_gender(self):
        return self.__gender
    def get_adminNo(self):
        return self.__adminNo
    def get_password(self):
        return self.__password
    def get_email(self):
        return self.__email
    def get_user(self):
        return self.__user
    def get_dateJoined(self):
        return self.__dateJoined

  
