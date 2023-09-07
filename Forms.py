import shelve
from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, ValidationError
from wtforms.fields import EmailField, DateField, PasswordField, FileField, IntegerField
# from flask_wtf.file import FileRequired
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

classOptions = [('', 'Select'), ('1E2', '1E2'), ('3A1', '3A1')]
modulesOptions = [('', 'Select'), ('MATH', 'MATH'), ('Science', 'Science')]

# classes_dict = {}
# db = shelve.open('class.db', 'r')
# classes_dict = db['Class']
# for i in classes_dict:
#     print(i)
#     classOptions.append(tuple([i]))
# [(x,) for x in classes_dict]


# modules_dict = {}
# db = shelve.open('modules.db', 'r')
# modules_dict = db['Modules']
# for i in modules_dict:
#     print(i)
#     classOptions.append(tuple([i]))
# [(x,) for x in modules_dict]

# =======================Allister's validation============================
def validate_module_code(form, field):
    modules_dict = {}
    db = shelve.open("module.db", 'c')
    try:
        modules_dict = db["Modules"]
    except:
        db["Modules"] = modules_dict
    db.close()

    if field.data in modules_dict:
        message = field.data + " already exists"
        raise ValidationError(message)

def validate_module_name(form, field):
    modules_dict = {}
    db = shelve.open("module.db", 'c')
    modules_dict = db["Modules"]
    db.close()
    list_of_modules = []

    for i in modules_dict.values():
        k = i.get_module_name()
        list_of_modules.append(k)

    if field.data in list_of_modules:
        message = field.data + " is already being used"
        raise ValidationError(message)

def validate_select_field(form, field):
    if field.data == '':
        message = 'Please pick an option, if it is blank then create the other component before assigning it'
        raise ValidationError(message)

def validate_date_implementation(form, field):
    current_time = datetime.date.today()
    if field.data < current_time:
        message = str(field.data.strftime("%m-%d-%Y")) + " can't be implemented before current date"
        raise ValidationError(message)

def validate_class_name(form, field):
    db = shelve.open("class.db", 'c')
    class_dict = db["Classes"]
    db.close()
    list_of_classes = []

    for i in class_dict.values():
        k = i.get_class_name()
        list_of_classes.append(k)

    if field.data in list_of_classes:
        message = field.data + ' already exists'
        raise ValidationError(message)

def validate_student_names(form,field):
    db = shelve.open("class.db", 'c')
    class_dict = db["Classes"]
    db.close()
    student_names = []

    for i in class_dict.values():
        for k in i.get_student_names():
            student_names.append(k)

    if field.data in student_names:
        message = field.data + ' already is in a class'
        raise ValidationError(message)

def validate_form_teachers(form,field):
    db = shelve.open("class.db", 'c')
    class_dict = db["Classes"]
    db.close()
    form_teachers = []

    for i in class_dict.values():
        for k in i.get_form_teachers():
            form_teachers.append(k)

    if field.data in form_teachers:
        message = field.data + ' is already a form teacher for another class'
        raise ValidationError(message)

# ===============================================================
def validate_date(form, field):
    if field.data > datetime.date.today():
        raise ValidationError("Birthdate cannot be in the future!")
    if field.data > datetime.date.today() - relativedelta(years=12):
        raise ValidationError("Student cannot be younger 12")
    if field.data < datetime.date.today() - relativedelta(years=18):
        raise ValidationError("Student cannot be older 18")
    

def validate_password(form, field):
    if len(field.data) < 8:
        raise ValidationError("Admin No. should consists of more than 7 characters.")
    if not any(char.isalpha() for char in field.data):
        raise ValidationError("Include at least one letter.") 
    if not any(char.isdigit() for char in field.data):
        raise ValidationError("Include at least one numerical character.")

def validate_adminNo(form, field):
    if len(field.data) != 7:
        raise ValidationError("Admin No. should only consists of 6 digits followed by a letter.")
    if field.data[0:5].isdigit() != True:
        raise ValidationError("First 6 Characters of Admin No. should be numerical.")
    if field.data[-1].isalpha() != True:
        raise ValidationError("Last Character of Admin No. should be a letter.")
    if field.data[-1].isupper() != True:
        raise ValidationError("Letter should be capitalized.")

    students_dict = {}
    db = shelve.open('Students.db', 'r')
    students_dict = db['Students']

    for i in students_dict:
        if field.data == i:
            raise ValidationError("Admin No. already exists.")
    db.close()

    teacher_dict = {}
    db = shelve.open('Teachers.db', 'r')
    teacher_dict = db['Teachers']

    for i in teacher_dict:
        if field.data == i:
            raise ValidationError("Admin No. already exists.")
    db.close()
    
    admin_dict = {}
    db = shelve.open('Admin.db', 'r')
    admin_dict = db['Admin']

    for i in admin_dict:
        if field.data == i:
            raise ValidationError("Admin No. already exists.")
    db.close()

def validate_staffID(form, field):
    if len(field.data) != 7:
        raise ValidationError("Staff ID should only consists of 6 digits followed by a letter.")
    if field.data[0:5].isdigit() != True:
        raise ValidationError("First 6 Characters of Staff ID should be numerical.")
    if field.data[-1].isalpha() != True:
        raise ValidationError("Last Character of Staff ID should be a letter.")
    if field.data[-1].isupper() != True:
        raise ValidationError("Letter should be capitalized.")

    students_dict = {}
    db = shelve.open('Students.db', 'r')
    students_dict = db['Students']

    for i in students_dict:
        if field.data == i:
            raise ValidationError("Staff ID already exists")
    db.close()

    teacher_dict = {}
    db = shelve.open('Teachers.db', 'r')
    teacher_dict = db['Teachers']

    for i in teacher_dict:
        if field.data == i:
            raise ValidationError("Staff ID already exists.")
    db.close()
    
    admin_dict = {}
    db = shelve.open('Admin.db', 'r')
    admin_dict = db['Admin']

    for i in admin_dict:
        if field.data == i:
            raise ValidationError("Staff ID already exists.")
    db.close()

class CreateLoginForm(Form):
    adminNo = StringField('Admin No. /Staff ID', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class VerifyForm(Form):
    adminNo = StringField('Admin No.', [validators.DataRequired()])

class VerifyCodeForm(Form):
    code = StringField('Enter OTP here', [validators.DataRequired()])

class NewPwForm(Form):
    password = PasswordField('New Password', [validators.DataRequired(), validate_password])

class StudentProfileForm(Form):
    name = StringField('Full Name', [validators.DataRequired()], render_kw={'readonly': True})
    gender = StringField('Gender', [validators.DataRequired()], render_kw={'readonly': True})
    birthDate = DateField('Birth Date', [validators.DataRequired()], render_kw={'readonly': True})
    className = StringField('Class', [validators.DataRequired()], render_kw={'readonly': True})
    adminNo = StringField('Admin Number', [validators.DataRequired()], render_kw={'readonly': True})
    email = EmailField('Email Address', [validators.DataRequired()], render_kw={'readonly': True})

class TeacherProfileForm(Form):
    name = StringField('Full Name', [validators.DataRequired()], render_kw={'readonly': True})
    gender = StringField('Gender', [validators.DataRequired()], render_kw={'readonly': True})
    adminNo = StringField('Staff ID', [validators.DataRequired()], render_kw={'readonly': True})
    email = EmailField('Email Address', [validators.DataRequired()], render_kw={'readonly': True})
    module1 = StringField('Modules', [validators.DataRequired()], render_kw={'readonly': True})

class AdminProfileForm(Form):
    name = StringField('Full Name', [validators.DataRequired()], render_kw={'readonly': True})
    gender = StringField('Gender', [validators.DataRequired()], render_kw={'readonly': True})
    adminNo = StringField('Staff ID', [validators.DataRequired()], render_kw={'readonly': True})
    email = EmailField('Email Address', [validators.DataRequired()], render_kw={'readonly': True})

class CreateStudentForm(Form):
    name = StringField('Full Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = RadioField('Gender', [validators.DataRequired()], choices=[('Female', 'Female'), ('Male', 'Male')])
    birthDate = DateField('Birth Date', [validators.DataRequired(), validate_date], format='%Y-%m-%d')
    adminNo = StringField('Admin Number', [validators.DataRequired(), validate_adminNo])
    password = PasswordField('Password', [validators.DataRequired(), validate_password])
    email = EmailField('Email Address', [validators.DataRequired()])

class UpdateStudentForm(Form):
    name = StringField('Full Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = RadioField('Gender', [validators.DataRequired()], choices=[('Female', 'Female'), ('Male', 'Male')])
    birthDate = DateField('Birth Date', [validators.DataRequired(), validate_date], format='%Y-%m-%d')
    adminNo = StringField('Admin Number', [validators.DataRequired()], render_kw={'readonly': True})
    password = PasswordField('Password', [validators.DataRequired(), validate_password])
    email = EmailField('Email Address', [validators.DataRequired()])

class CreateTeacherForm(Form):
    name = StringField('Full Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = RadioField('Gender', [validators.DataRequired()], choices=[('Female', 'Female'), ('Male', 'Male')])
    adminNo = StringField('Staff ID', [validators.DataRequired(), validate_staffID])
    password = PasswordField('Password', [validators.DataRequired(), validate_password])
    email = EmailField('Email Address', [validators.DataRequired()])
    module1 = SelectField('Modules', [validators.DataRequired()], default='Select')
    # module3 = SelectField('Modules', [validators.DataRequired()], choices=modulesOptions, default='')

class UpdateTeacherForm(Form):
    name = StringField('Full Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = RadioField('Gender', choices=[('Female', 'Female'), ('Male', 'Male')])
    adminNo = StringField('Staff ID', [validators.DataRequired()], render_kw={'readonly': True})
    password = PasswordField('Password', [validators.DataRequired(), validate_password])
    email = EmailField('Email Address', [validators.DataRequired()])
    module1 = SelectField('Modules', [validators.DataRequired()], choices=modulesOptions, default='')
    # module2 = SelectField('Modules', [validators.DataRequired()], choices=modulesOptions, default='')

class CreateAdminForm(Form):
    name = StringField('Full Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = RadioField('Gender', [validators.DataRequired()],choices=[('F', 'Female'), ('M', 'Male')])
    adminNo = StringField('Staff ID', [validators.DataRequired(), validate_staffID])
    password = PasswordField('Password', [validators.DataRequired(), validate_password])
    email = EmailField('Email Address', [validators.DataRequired()])

class UpdateAdminForm(Form):
    name = StringField('Full Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = RadioField('Gender', choices=[('Female', 'Female'), ('Male', 'Male')])
    adminNo = StringField('Staff ID', [validators.DataRequired()], render_kw={'readonly': True})
    password = PasswordField('Password', [validators.DataRequired(), validate_password])
    email = EmailField('Email Address', [validators.DataRequired()])

class CreateFeedback(Form):
    modules = StringField('Modules', [validators.DataRequired()], render_kw={'readonly': True})
    message1 = StringField('What i like about this class is', [validators.DataRequired()])
    message2 = StringField('I learn best by', [validators.DataRequired()])
    message3 = StringField('I am experiencing some difficulty in', [validators.DataRequired()])
    message4 = TextAreaField("Additional questions or comments")

class TeacherViewFeedback(Form):
    message1 = StringField('What i like about this class is', [validators.DataRequired()], render_kw={'readonly': True})
    message2 = StringField('I learn best by', [validators.DataRequired()], render_kw={'readonly': True})
    message3 = StringField('I am experiencing some difficulty in', [validators.DataRequired()], render_kw={'readonly': True})
    message4 = TextAreaField("Additional questions or comments", render_kw={'readonly': True})

class UpdateFeedback(Form):
    modules = StringField('Modules', render_kw={'readonly': True})
    message1 = StringField('What i like about this class is', [validators.DataRequired()], render_kw={'readonly': True})
    message2 = StringField('I learn best by', [validators.DataRequired()], render_kw={'readonly': True})
    message3 = StringField('I am experiencing some difficulty in', [validators.DataRequired()], render_kw={'readonly': True})
    message4 = TextAreaField("Additional questions or comments", render_kw={'readonly': True})

class changePasswordForm(Form):
    old_password = PasswordField('Current Password', [validators.DataRequired(), validate_password])
    new_password = PasswordField('New Password', [validators.DataRequired(), validate_password])
    confirm_password = PasswordField('Confirm Password', [validators.DataRequired(), validate_password])

# =======================Elijah's work============================
class CreateAssignmentForm(Form):
    AssignmentName = StringField('Assignment Name', [validators.Length(min=1, max=30), validators.DataRequired()])
    DueDate = DateField('Due Date', [validators.DataRequired()])
    AssignmentDetails = TextAreaField('Assignment Details', [validators.DataRequired()])
    file = FileField('File')
    module_code = StringField('Module Name', [validators.DataRequired()], render_kw={'readonly': True})
    classes_assigned = SelectField('Assigned Classes', [validators.DataRequired()], choices=[])

def validate_DueDate(form, field):
        CurrentDate = date.today()
        if field.data < CurrentDate:
            raise ValidationError("Due date cannot be in the past")

def validate_AssignmentName(form, field):
    if field.data.isnumeric():
        raise ValidationError("Assignment Name can only contain words and a mixture of words and numbers")

    
# =======================Allister's work============================
class Search(Form):
    search_bar = StringField(render_kw={"placeholder": "Search"})

class CreateModuleForm(Form):
    module_image = FileField('Module Image')
    module_code = StringField('Module Code', [validators.Length(min=1, max=10), validators.DataRequired(), validate_module_code])
    module_name = StringField('Module Name', [validators.Length(min=1, max=100), validators.DataRequired(), validate_module_name])
    implementation_date = DateField('Implementation date', [validators.DataRequired(), validate_date_implementation], format='%Y-%m-%d', default=datetime.datetime.now())
    module_description = TextAreaField('Module Description', [validators.Optional()])
    classes_assigned = SelectField('Assign Class 1', [validate_select_field], default="")
    classes_assigned2 = SelectField('Assign Class 2', [validators.Optional(), validate_select_field], default='')
    classes_assigned3 = SelectField('Assign Class 3', [validators.Optional(), validate_select_field], default='')
    classes_assigned4 = SelectField('Assign Class 4', [validators.Optional(), validate_select_field], default='')
    classes_assigned5 = SelectField('Assign Class 5', [validators.Optional(), validate_select_field], default='')
    classes_assigned6 = SelectField('Assign Class 6', [validators.Optional(), validate_select_field], default='')
    classes_assigned7 = SelectField('Assign Class 7', [validators.Optional(), validate_select_field], default='')
    classes_assigned8 = SelectField('Assign Class 8', [validators.Optional(), validate_select_field], default='')


class UpdateModuleForm(Form):
    module_code = ''
    module_image = FileField('Module Image')
    previous_image = ''
    module_name = StringField('Module Name', [validators.Length(min=1, max=100), validators.DataRequired(), validate_module_name])
    implementation_date = DateField('Implementation Date', [validators.DataRequired(), validate_date_implementation], format='%Y-%m-%d', default=datetime.datetime.now())
    module_description = TextAreaField('Module Description', [validators.Optional()])
    db = shelve.open("class.db", 'c')
    classes_dict = {}
    try:
        classes_dict = db["Classes"]
    except:
        db["Classes"] = classes_dict
    class_assigned_choices = ['']
    for i in list(classes_dict.values()):
        class_assigned_choices.append(str(i.get_class_id()) + '.' + i.get_class_name())
    db.close()
    classes_assigned = SelectField('Assign Class 1', [validate_select_field], default="")
    classes_assigned2 = SelectField('Assign Class 2', [validators.Optional(), validate_select_field], default='')
    classes_assigned3 = SelectField('Assign Class 3', [validators.Optional(), validate_select_field], default='')
    classes_assigned4 = SelectField('Assign Class 4', [validators.Optional(), validate_select_field], default='')
    classes_assigned5 = SelectField('Assign Class 5', [validators.Optional(), validate_select_field], default='')
    classes_assigned6 = SelectField('Assign Class 6', [validators.Optional(), validate_select_field], default='')
    classes_assigned7 = SelectField('Assign Class 7', [validators.Optional(), validate_select_field], default='')
    classes_assigned8 = SelectField('Assign Class 8', [validators.Optional(), validate_select_field], default='')

class CreateClassForm(Form):
    class_name = StringField('Class Name', [validators.Length(min=1, max=150), validators.DataRequired(), validate_class_name])
    implementation_date = DateField('Implementation Date', [validators.DataRequired(), validate_date_implementation], format='%Y-%m-%d', default=datetime.datetime.now())
    student_names = SelectField('Student Name 1', [validate_student_names, validate_select_field], default='')
    student_names2 = SelectField('Student Name 2', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names3 = SelectField('Student Name 3', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names4 = SelectField('Student Name 4', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names5 = SelectField('Student Name 5', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names6 = SelectField('Student Name 6', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names7 = SelectField('Student Name 7', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names8 = SelectField('Student Name 8', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names9 = SelectField('Student Name 9', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names10 = SelectField('Student Name 10', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names11 = SelectField('Student Name 11', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names12 = SelectField('Student Name 12', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names13 = SelectField('Student Name 13', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names14 = SelectField('Student Name 14', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names15 = SelectField('Student Name 15', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names16 = SelectField('Student Name 16', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names17 = SelectField('Student Name 17', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names18 = SelectField('Student Name 18', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names19 = SelectField('Student Name 19', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names20 = SelectField('Student Name 20', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names21 = SelectField('Student Name 21', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names22 = SelectField('Student Name 22', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names23 = SelectField('Student Name 23', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names24 = SelectField('Student Name 24', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names25 = SelectField('Student Name 25', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names26 = SelectField('Student Name 26', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names27 = SelectField('Student Name 27', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names28 = SelectField('Student Name 28', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names29 = SelectField('Student Name 29', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names30 = SelectField('Student Name 30', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names31 = SelectField('Student Name 31', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names32 = SelectField('Student Name 32', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names33 = SelectField('Student Name 33', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names34 = SelectField('Student Name 34', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names35 = SelectField('Student Name 35', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names36 = SelectField('Student Name 36', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names37 = SelectField('Student Name 37', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names38 = SelectField('Student Name 38', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names39 = SelectField('Student Name 39', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names40 = SelectField('Student Name 40', [validators.Optional(), validate_student_names, validate_select_field], default='')

    form_teachers = SelectField('Form Teacher 1', [validate_form_teachers, validate_select_field], default='')
    form_teachers2 = SelectField('Form Teacher 2', [validators.Optional(), validate_form_teachers, validate_select_field], default='')
    form_teachers3 = SelectField('Form Teacher 3', [validators.Optional(), validate_form_teachers, validate_select_field], default='')
    form_teachers4 = SelectField('Form Teacher 4', [validators.Optional(), validate_form_teachers, validate_select_field], default='')
    class_description = TextAreaField('Class Description', [validators.Optional()])

class UpdateClassForm(Form):
    class_name = ''
    implementation_date = DateField('Implementation Date', [validators.DataRequired(), validate_date_implementation], format='%Y-%m-%d', default=datetime.datetime.now())
    student_names = SelectField('Student Name 1', [validate_student_names, validate_select_field], default='')
    student_names2 = SelectField('Student Name 2', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names3 = SelectField('Student Name 3', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names4 = SelectField('Student Name 4', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names5 = SelectField('Student Name 5', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names6 = SelectField('Student Name 6', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names7 = SelectField('Student Name 7', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names8 = SelectField('Student Name 8', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names9 = SelectField('Student Name 9', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names10 = SelectField('Student Name 10', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names11 = SelectField('Student Name 11', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names12 = SelectField('Student Name 12', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names13 = SelectField('Student Name 13', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names14 = SelectField('Student Name 14', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names15 = SelectField('Student Name 15', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names16 = SelectField('Student Name 16', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names17 = SelectField('Student Name 17', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names18 = SelectField('Student Name 18', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names19 = SelectField('Student Name 19', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names20 = SelectField('Student Name 20', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names21 = SelectField('Student Name 21', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names22 = SelectField('Student Name 22', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names23 = SelectField('Student Name 23', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names24 = SelectField('Student Name 24', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names25 = SelectField('Student Name 25', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names26 = SelectField('Student Name 26', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names27 = SelectField('Student Name 27', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names28 = SelectField('Student Name 28', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names29 = SelectField('Student Name 29', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names30 = SelectField('Student Name 30', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names31 = SelectField('Student Name 31', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names32 = SelectField('Student Name 32', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names33 = SelectField('Student Name 33', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names34 = SelectField('Student Name 34', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names35 = SelectField('Student Name 35', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names36 = SelectField('Student Name 36', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names37 = SelectField('Student Name 37', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names38 = SelectField('Student Name 38', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names39 = SelectField('Student Name 39', [validators.Optional(), validate_student_names, validate_select_field], default='')
    student_names40 = SelectField('Student Name 40', [validators.Optional(), validate_student_names, validate_select_field], default='')

    form_teachers = SelectField('Form Teacher 1', [validate_form_teachers, validate_select_field], default='')
    form_teachers2 = SelectField('Form Teacher 2', [validators.Optional(), validate_form_teachers, validate_select_field], default='')
    form_teachers3 = SelectField('Form Teacher 3', [validators.Optional(), validate_form_teachers, validate_select_field], default='')
    form_teachers4 = SelectField('Form Teacher 4', [validators.Optional(), validate_form_teachers, validate_select_field], default='')
    class_description = TextAreaField('Class Description', [validators.Optional()])

#validate_student_names, validate_module_update, validate_form_teachers
# form_teachers_choices =
# student_name_choices =

# =======================Eshton's work============================

class CreateSubmissionForm(Form):
    assignment = StringField("Assignment", render_kw={'readonly': True})
    submission_name = StringField('Submission Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    details = TextAreaField('Details (200 Character Limit)', [validators.Optional()])
    answers = TextAreaField('Answers')
    file = FileField('File Upload')

    def validate_details(form, field):
        if len(field.data)>200:
            raise ValidationError("This has exceeded 200 characters.")

class UpdateSubmissionForm(Form):
    details = TextAreaField('Details (200 Character Limit)', [validators.Optional()])
    file = FileField('File Upload')

class TeacherForm(Form):
    status = SelectField('Status', [validators.DataRequired()], choices=[('Unseen','Unseen'), ('Seen','Seen'), ('Accepted','Accepted'), ('Rejected','Rejected')], default='Unseen')
    grades = IntegerField('Marks (In Percentage)', [validators.DataRequired()])

    def validate_grades(form, field):
        if field.data > 100 or field.data < 0:
            raise ValidationError("Grades must be between 0 and 100.")