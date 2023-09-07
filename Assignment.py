class Assignment:
    def __init__(self, FileID, AssignmentName, DueDate, AssignmentDetails, module_code, classes_assigned, filename):
        self.__FileID = FileID
        self.__AssignmentName = AssignmentName
        self.__DueDate = DueDate
        self.__AssignmentDetails = AssignmentDetails
        self.__module_code = module_code
        self.__classes_assigned = classes_assigned
        self.__filename = filename
        
    def set_FileID(self, FileID):
        self.__FileID = FileID

    def set_AssignmentName(self, AssignmentName):
        self.__AssignmentName = AssignmentName
        
    def set_DueDate(self, DueDate):
        self.__DueDate = DueDate
    
    def set_AssignmentDetails(self, AssignmentDetails):
        self.__AssignmentDetails = AssignmentDetails

    def set_module_code(self, module_code):
        self.__module_code = module_code

    def set_classes_assigned(self, classes_assigned):
        self.__classes_assigned = classes_assigned

    def set_filename(self, filename):
        self.__filename = filename

    def get_FileID(self):
        return self.__FileID

    def get_AssignmentName(self):
        return self.__AssignmentName

    def get_DueDate(self):
        return self.__DueDate
    
    def get_AssignmentDetails(self):
        return self.__AssignmentDetails
    
    def get_module_code(self):
        return self.__module_code
    
    def get_classes_assigned(self):
        return self.__classes_assigned

    def get_filename(self):
        return self.__filename
    