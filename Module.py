class Module:
    def __init__(self, module_image, module_code, module_name, implementation_date, module_description, classes_assigned):
        self.__module_code = module_code
        self.__module_name = module_name
        self.__module_image = module_image
        self.__module_description = module_description
        self.__implementation_date = implementation_date
        self.__classes_assigned = classes_assigned

    def get_module_code(self):
        return self.__module_code

    def get_module_name(self):
        return self.__module_name

    def get_module_image(self):
        return self.__module_image

    def get_module_description(self):
        return self.__module_description

    def get_implementation_date(self):
        return self.__implementation_date

    def get_classes_assigned(self):
        return self.__classes_assigned

    def set_module_code(self, module_code):
        self.__module_code = module_code

    def set_module_name(self, module_name):
        self.__module_name = module_name

    def set_module_image(self, module_image):
        self.__module_image = module_image

    def set_module_description(self, module_description):
        self.__module_description = module_description

    def set_implementation_date(self, implementation_date):
        self.__implementation_date = implementation_date

    def set_classes_assigned(self, classes_assigned):
        self.__classes_assigned = classes_assigned
