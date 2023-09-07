import shelve
class Class:
    def __init__(self, class_id, class_name, implementation_date, student_names, form_teachers, class_description):
        self.__class_id = class_id
        self.__class_name = class_name
        self.__student_names = student_names
        self.__implementation_date = implementation_date
        self.__form_teachers = form_teachers
        self.__class_description = class_description

    def get_class_name(self):
        return self.__class_name

    def get_student_names(self):
        return self.__student_names

    def get_form_teachers(self):
        return self.__form_teachers

    def get_class_id(self):
        return self.__class_id

    def get_implementation_date(self):
        return self.__implementation_date

    def get_class_description(self):
        return self.__class_description

    def set_class_name(self, class_name):
        self.__class_name = class_name

    def set_student_names(self, student_names):
        self.__student_names = student_names

    def set_implementation_date(self, implementation_date):
        self.__implementation_date = implementation_date

    def set_form_teachers(self, form_teachers):
        self.__form_teachers = form_teachers

    def set_class_description(self, class_description):
        self.__class_description = class_description
