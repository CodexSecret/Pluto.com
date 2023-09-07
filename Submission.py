from datetime import datetime

# User class
class Submission:
    # initializer method
    def __init__(self, student_id, submission_id, assignment_id, assignment_name, module_code, submission_name, details, answers, filename):
        self.__submission_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.__student_id = student_id
        self.__submission_id = submission_id
        self.__assignment_id = assignment_id
        self.__assignment_name = assignment_name
        self.__module_code = module_code
        self.__submission_name = submission_name
        self.__details = details
        self.__answers = answers
        self.__filename = filename
        self.__status = "Unseen"
        self.__grades = "Ungraded"

    # accessor methods
    def get_student_id(self):
        return self.__student_id

    def get_submission_id(self):
        return self.__submission_id

    def get_submission_date(self):
        return self.__submission_date

    def get_assignment_name(self):
        return self.__assignment_name

    def get_assignment_id(self):
        return self.__assignment_id

    def get_module_code(self):
        return self.__module_code

    def get_submission_name(self):
        return self.__submission_name

    def get_details(self):
        return self.__details

    def get_filename(self):
        return self.__filename

    def get_status(self):
        return self.__status

    def get_grades(self):
        return self.__grades

    def get_answers(self):
        return self.__answers

    # mutator methods
    def set_student_id(self, student_id):
        self.__student_id = student_id

    def set_submission_id(self, submission_id):
        self.__submission_id = submission_id

    def set_submission_date(self, submission_date):
        self.__submission_date = submission_date

    def set_assignment_name(self, assignment_name):
        self.__assignment_name = assignment_name
    
    def set_assignment_id(self, assignment_id):
        self.__assignment_id = assignment_id

    def set_module_code(self, module_code):
        self.__module_code = module_code

    def set_submission_name(self, submission_name):
        self.__submission_name = submission_name

    def set_details(self, details):
        self.__details = details

    def set_filename(self, filename):
        self.__filename = filename

    def set_status(self,status):
        self.__status = status

    def set_grades(self,grades):
        self.__grades = grades

    def set_answers(self,answers):
        self.__grades = answers