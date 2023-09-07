from flask import Flask, render_template, request, redirect, url_for, session, send_file
from Forms import *
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from datetime import date
import shelve, Students, Teachers, Admin, Feedback, Assignment, Module, Class, Submission
from functools import wraps
import random
import os
from datetime import datetime, date

UPLOAD_FOLDER = ('static/files')

app = Flask(__name__)
app.debug = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "actuallyavailable456@gmail.com"
app.config['MAIL_PASSWORD'] = "rmfinvpjsdoaukdn"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
mail = Mail(app) 

app.config["SECRET_KEY"] = "plutosecretkey"

def allowed_file(filename):
    return'.' in filename and \
        filename.rsplit('.', 1)[1].lower() 

def authenticate():
    account = session.get('account')
    return account and len(account.strip()) > 0


def login_check(f):
    @wraps(f)
    def _wrapper(*args, **kwargs):  
        if authenticate():
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return _wrapper

@app.route('/', methods=['GET', 'POST'])
def login():
    session.clear()
    login_form = CreateLoginForm(request.form)
    if request.method == 'POST' and login_form.validate():
        users = []
        students_dict = {}
        db = shelve.open('Students.db')
        try:
            if 'Students' in db:
                students_dict = db['Students']
                users.append(students_dict)
            else:
                db['Students'] = students_dict
        except:
            print('Error in opening Students.db')
        
        db.close()

        teachers_dict = {}
        db = shelve.open('Teachers.db')
        try:
            if 'Teachers' in db:
                teachers_dict = db['Teachers']
                users.append(teachers_dict)
            else:
                db['Teachers'] = teachers_dict
        except:
            print('Error in opening Teachers.db')  
            
        db.close()
        
        admin_dict = {}
        db = shelve.open('Admin.db')
        try:
            if 'Admin' in db:
                admin_dict = db['Admin']
                users.append(admin_dict)
            else:
                db['Admin'] = admin_dict
        except:
            print('Error in opening Admin.db')

        db.close()

        for i in users:
            if login_form.adminNo.data in i and login_form.password.data == i.get(login_form.adminNo.data).get_password():
                session['account'] = login_form.adminNo.data
                session['users'] = i.get(login_form.adminNo.data).get_user()
                session['name'] = i.get(login_form.adminNo.data).get_name()
                
                if session['users'] == 'Student':
                    return redirect(url_for('studentHome'))
                elif session['users'] == 'Teacher':
                    return redirect(url_for('teacherHome'))
                elif session['users'] == 'Administrator':
                    return redirect(url_for('adminHome'))
                
        return render_template('login.html', form=login_form, message='Incorrect Admin No. or password!')

    return render_template('login.html', form=login_form)

@app.route('/forgetpw', methods=['GET', 'POST'])
def forgetPw():
    forget_pw_form = VerifyForm(request.form)
    if request.method == 'POST' and forget_pw_form.validate():
        with shelve.open('Teachers.db') as teacher_db:
            with shelve.open('Students.db') as student_db:
                with shelve.open('Admin.db') as admin_db:
                    if forget_pw_form.adminNo.data in teacher_db['Teachers']:
                        session['adminNo'] = forget_pw_form.adminNo.data
                        session['email'] = teacher_db['Teachers'].get(forget_pw_form.adminNo.data).get_email()
                        return redirect(url_for('verify'))
                    elif forget_pw_form.adminNo.data in student_db['Students']:
                        session['adminNo'] = forget_pw_form.adminNo.data
                        session['email'] = student_db['Students'].get(forget_pw_form.adminNo.data).get_email()
                        return redirect(url_for('verify'))
                    elif forget_pw_form.adminNo.data in admin_db['Admin']:
                        session['adminNo'] = forget_pw_form.adminNo.data
                        session['email'] = admin_db['Admin'].get(forget_pw_form.adminNo.data).get_email()
                        return redirect(url_for('verify'))
                    else:
                        return render_template('forgetpw.html', form=forget_pw_form, message='Admin No. does not exists.')
    return render_template('forgetpw.html', form=forget_pw_form)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    otp = random.randint(100000, 999999)
    if 'otp' not in session:
        session['otp'] = otp
    msg = Message('Your OTP is ' + str(otp) , sender = 'actuallyavailable456@gmail.com', recipients = [session['email']])
    msg.body = "Do not share your OTP with anyone. Enter the OTP to reset password."
    mail.send(msg)
    code_form = VerifyCodeForm(request.form)
    if request.method == 'POST' and code_form.validate():
        if code_form.code.data == str(session['otp']):
            return redirect(url_for('resetpw'))
        else:
            return render_template('verify.html', form=code_form, message="Incorrect OTP. Try again.")

    return render_template('verify.html', form=code_form)

@app.route('/resetPw', methods=['GET', 'POST'])
def resetpw():
    reset_pw_form = NewPwForm(request.form)
    if request.method == 'POST' and reset_pw_form.validate():
        with shelve.open('Teachers.db') as teacher_db:
            with shelve.open('Students.db') as student_db:
                with shelve.open('Admin.db') as admin_db:
                    if session['adminNo'] in teacher_db['Teachers']:
                        teacher_db['Teachers'].get(session['adminNo']).set_password(reset_pw_form.password.data)
                        return redirect(url_for('login'))
                    elif session['adminNo'] in student_db['Students']:
                        student_db['Students'].get(session['adminNo']).set_password(reset_pw_form.password.data)
                        return redirect(url_for('login'))
                    elif session['adminNo'] in admin_db['Admin']:
                        admin_db['Admin'].get(session['adminNo']).set_password(reset_pw_form.password.data)
                        return redirect(url_for('login'))
                    
    return render_template('resetpw.html', form=reset_pw_form)

@app.route('/changePassword', methods=['POST', 'GET'])
def changePassword():
    change_pw_form = changePasswordForm(request.form)
    if request.method == 'POST' and change_pw_form.validate():
        with shelve.open('Teachers.db') as teacher_db:
            with shelve.open('Students.db') as student_db:
                with shelve.open('Admin.db') as admin_db:
                    if session['account'] in teacher_db['Teachers']:
                        account = teacher_db['Teachers'][session['account']]
                        db = teacher_db
                        name = 'Teachers'
                    elif session['account'] in student_db['Students']:
                        account = student_db['Students'][session['account']]
                        db = student_db
                        name = 'Students'
                        
                    elif session['account'] in admin_db['Admin']:
                        account = admin_db['Admin'][session['account']]
                        db = admin_db
                        name = 'Admin'

                    else:
                        return render_template('changePw.html', form=change_pw_form, message='Incorrect Admin Number')
                    if change_pw_form.old_password.data != account.get_password():
                        return render_template('changePw.html', form=change_pw_form, message='Current password is incorrect')
                    if change_pw_form.new_password.data != change_pw_form.confirm_password.data:
                        return render_template('changePw.html', form=change_pw_form, message='New passwords does not match')
                    if change_pw_form.old_password.data == change_pw_form.new_password.data:
                        return render_template('changePw.html', form=change_pw_form, message='New password cannot be the same as current password')
                    account.set_password(change_pw_form.new_password.data)
                    db2 = db[name]
                    db2[session['account']] = account
                    db[name] = db2
                    return redirect(url_for('userHome'))

    return render_template('changePw.html', form=change_pw_form)

@app.route('/userHome')
@login_check
def userHome():
    if session['users'] == 'Student':
        return redirect(url_for('studentHome'))
    elif session['users'] == 'Teacher':
        return redirect(url_for('teacherHome'))
    else:
        return redirect(url_for('adminHome'))
    
   

@app.route('/studentHome')
@login_check
def studentHome():
    assignments_dict = {}
    db = shelve.open('assignment.db')
    try:
        assignments_dict = db['Assignments']
    except:
        db['Assignments'] = assignments_dict
    db.close
    assignments_list = []
    for assignment in assignments_dict:
        assignments_list.append(assignments_dict.get(assignment))

    submission_dict = {}
    db = shelve.open('submission.db')
    try:
        submission_dict = db['Submissions']
    except:
        db["Submissions"] = submission_dict
    db.close()
    submissions_list = []
    for submission in submission_dict:
        submissions_list.append(submission_dict.get(submission))

    labels = []
    modules_dict = {}
    db = shelve.open('module.db')
    modules_dict = db['Modules']
    db.close()
    modules_list = []
    for module in modules_dict:
        modules_list.append(modules_dict.get(module))

    classes_dict = {}
    db = shelve.open('class.db')
    classes_dict = db['Classes']
    db.close()
    classes_list = []
    for classes in classes_dict:
        classes_list.append(classes_dict.get(classes))

    labels = []
    studentModule_list = []
    for module in modules_list:
        for classes in classes_list:
            if str(session['account'] + '.' + session['name']) in classes.get_student_names():
                if str(classes.get_class_id()) + '.' + classes.get_class_name() in module.get_classes_assigned():
                    studentModule_list.append(module)
                    labels.append(module.get_module_name())

    marksCount = {}
    marks = {}
    for module in studentModule_list:
        marks[module.get_module_name()] = 0
        marksCount[module.get_module_name()] = 0
        for assignment in assignments_list:
            for submission in submissions_list:
                if assignment.get_module_code() == module.get_module_code():
                    if assignment.get_AssignmentName() == submission.get_assignment():
                        if submission.get_grades() != "Ungraded":
                            marksCount[module.get_module_name()] += 1
                            marks[module.get_module_name()] += submission.get_grades()

    values = []
    for mark in marks:
        for count in marksCount:
            if count == mark:
                if marks.get(mark) == 0 or marksCount.get(count) == 0:
                    values.append(marks.get(mark))
                else:
                    values.append(marks.get(mark)/marksCount.get(count))


    Olvl = datetime(2023, 10, 16)
    now = datetime.now()
    delta = Olvl - now
    
    bar_labels=labels
    bar_values=values

    return render_template('studentHome.html', assignments_list=assignments_list, assignmentsCount=len(assignments_list), submissions_list=submissions_list, submissionsCount=len(submissions_list), studentModule_list=studentModule_list, modulesCount=len(studentModule_list), Olvlcountdown=delta.days, title='Average marks of each module', max=100, labels=bar_labels, values=bar_values)

@app.route('/teacherHome')
@login_check
def teacherHome():
    teacher_dict = {}
    db = shelve.open('Teachers.db', 'r')
    teacher_dict = db['Teachers']
    db.close()
    teacher = teacher_dict.get(session['account'])
    moduleName = teacher.get_modules()

    student_dict = {}
    db = shelve.open('Students.db', 'r')
    student_dict = db['Students']
    db.close()
    students_list = []
    for student in student_dict:
        students_list.append(student_dict.get(student))

    modules_dict = {}
    db = shelve.open('module.db')
    modules_dict = db['Modules']
    db.close()
    for module in modules_dict:
        if modules_dict.get(module).get_module_name() == moduleName:
            modules = modules_dict.get(module)
            
    assignments_dict = {}
    db = shelve.open('assignment.db')
    try:
        assignments_dict = db['Assignments']
    except:
        db['Assignments'] = assignments_dict
    db.close
    labels = []
    assignments_list = []
    for assignment in assignments_dict:
        if assignments_dict.get(assignment).get_module_code() == teacher.get_modules():
            labels.append(assignments_dict.get(assignment).get_AssignmentName())
            assignments_list.append(assignments_dict.get(assignment))

    submissions_dict = {}
    db = shelve.open('submission.db')
    try:
        submissions_dict = db['Submissions']
    except:
        db['Submissions'] = submissions_dict
    db.close()
    submissionsUngraded_list = []
    submissions_list = []
    for submission in submissions_dict:
        if submissions_dict.get(submission).get_module_code() == moduleName:
            if submissions_dict.get(submission).get_grades() == "Ungraded":
                submissions_dict.get(submission).set_submission_date(datetime.strptime(submissions_dict.get(submission).get_submission_date(), '%d/%m/%Y %H:%M:%S').date().strftime("%b %d"))
                submissionsUngraded_list.append(submissions_dict.get(submission))
            else:
                submissions_list.append(submissions_dict.get(submission))

    marksCount = {}
    marks = {}
    for assignment in assignments_list:
        marks[assignment.get_AssignmentName()] = 0
        marksCount[assignment.get_AssignmentName()] = 0
        # for submission in submissions_list:
            
                    # print(marks)
    for submission in submissions_list:
        print(submission.get_assignment_name())
        if submission.get_grades() != "Ungraded":
            marksCount[submission.get_assignment_name()] += 1
            marks[submission.get_assignment_name()] += submission.get_grades()

    values = []
    for mark in marks:
        for count in marksCount:
            if count == mark:
                if marks.get(mark) == 0 or marksCount.get(count) == 0:
                    values.append(marks.get(mark))
                else:
                    values.append(marks.get(mark)/marksCount.get(count))

    feedback_dict = {}
    db = shelve.open('Feedback.db', 'r')
    try:
        feedback_dict = db['Feedback']
    except:
        db['Feedback'] = feedback_dict

    db.close()
    feedback_list = []
    for feedback in feedback_dict:
        if feedback_dict.get(feedback).get_moduleID() == teacher.get_modules():
            feedback_list.append(feedback)

    ungradedSubmission = len(submissionsUngraded_list)
    for assignment in assignments_list:
        for submission in submissionsUngraded_list:
            if assignment.get_module_code() == submission.get_module_code():
                if submission.get_grades() != "Ungraded":
                    ungradedSubmission -= 1

    if ungradedSubmission < 0:
        ungradedSubmission = 0

    Olvl = datetime(2023, 10, 16)
    now = datetime.now()
    delta = Olvl - now

    line_labels=labels
    line_values=values

    return render_template('teacherHome.html', feedback_list=feedback_list, feedbackCount=len(feedback_list), ungradedSubmission=ungradedSubmission, Olvlcountdown=delta.days, moduleName=moduleName, submissions_list=submissions_list, submissionsUngraded_list=submissionsUngraded_list, submissionsCount=len(submissions_list), modules=modules, students_list=students_list, title='Average Scores For Each Assignment', max=100, labels=line_labels, values=line_values)

@app.route('/adminHome')
@login_check
def adminHome():
    students_dict = {}
    db = shelve.open('Students.db', 'r')
    students_dict = db['Students']
    db.close
    studentCount = len(students_dict)

    teachers_dict = {}
    db = shelve.open('Teachers.db', 'r')
    teachers_dict = db['Teachers']
    db.close
    teacherCount = len(teachers_dict)

    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()
    moduleCount = len(modules_dict)

    classes_dict = {}
    db = shelve.open('class.db', 'r')
    classes_dict = db['Classes']
    db.close()
    classCount = len(classes_dict)


    return render_template('adminHome.html', studentCount=studentCount, teacherCount=teacherCount, moduleCount=moduleCount, classCount=classCount)

@app.route('/studentProfile', methods=['POST', 'GET'])
@login_check
def student_profile():
    view_profile_form = StudentProfileForm(request.form)
    if request.method == 'POST':
        return redirect(url_for('studentHome'))
    else:
        students_dict = {}
        db = shelve.open('Students.db', 'r')
        students_dict = db['Students']
        db.close

        student = students_dict.get(session['account'])
        view_profile_form.name.data = student.get_name()
        view_profile_form.gender.data = student.get_gender()
        view_profile_form.birthDate.data = student.get_birthDate()
        view_profile_form.email.data = student.get_email()
        view_profile_form.adminNo.data = student.get_adminNo()

        return render_template('studentProfile.html', form=view_profile_form)

@app.route('/viewTeacher', methods=['GET', 'POST'])
@login_check
def view_teacher():
    
    view_teacher_form = TeacherProfileForm(request.form)
    if request.method == 'POST' and view_teacher_form.validate():
        return redirect(url_for('teacherHome'))
    else:
        teachers_dict = {}
        db = shelve.open('Teachers.db', 'r')
        teachers_dict = db['Teachers']
        db.close

        teacher = teachers_dict.get(session['account'])
        view_teacher_form.name.data = teacher.get_name()
        view_teacher_form.gender.data = teacher.get_gender()
        view_teacher_form.email.data = teacher.get_email()
        view_teacher_form.module1.data = teacher.get_modules()
        view_teacher_form.adminNo.data = teacher.get_adminNo()

        return render_template('teacherProfile.html', form=view_teacher_form)

@app.route('/viewAdmin', methods=['GET', 'POST'])
@login_check
def view_admin():
    
    view_admin_form =AdminProfileForm(request.form)
    if request.method == 'POST' and view_admin_form.validate():
        return redirect(url_for('adminHome'))
    else:
        admin_dict = {}
        db = shelve.open('Admin.db', 'r')
        admin_dict = db['Admin']
        db.close

        admin = admin_dict.get(session['account'])
        view_admin_form.name.data = admin.get_name()
        view_admin_form.gender.data = admin.get_gender()
        view_admin_form.email.data = admin.get_email()
        view_admin_form.adminNo.data = admin.get_adminNo()
        return render_template('adminProfile.html', form=view_admin_form)


@app.route('/createStudent', methods=['GET', 'POST'])
@login_check
def create_student():
    create_student_form = CreateStudentForm(request.form)
    if request.method == 'POST' and create_student_form.validate():
        students_dict = {}
        db = shelve.open('Students.db', 'c')

        try:
            if 'Students' in db:
                students_dict = db['Students']
        except:
            print("Error retrieving student from Students.db.")

        student = Students.Student(create_student_form.name.data,
                                   create_student_form.gender.data, create_student_form.adminNo.data, 
                                   create_student_form.password.data, create_student_form.email.data, 
                                   create_student_form.birthDate.data)

        students_dict[student.get_adminNo()] = student
        db['Students'] = students_dict

        db.close()
        return redirect(url_for('retrieve_students'))

    return render_template('createStudent.html', form=create_student_form)

@app.route('/createTeacher', methods=['GET', 'POST'])
@login_check
def create_teacher():
    create_teacher_form = CreateTeacherForm(request.form)
    modules_list = ['Select']
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()
    
    for module in modules_dict:
        modules_list.append(modules_dict.get(module).get_module_name())
    create_teacher_form.module1.choices = modules_list

    if request.method == 'POST' and create_teacher_form.validate():
        teachers_dict = {}
        db = shelve.open('Teachers.db', 'c')

        try:
            if 'Teachers' in db:
                teachers_dict = db['Teachers']
        except:
            print("Error retrieving teacher from teachers.db.")

        teacher = Teachers.Teacher(create_teacher_form.name.data,
                                   create_teacher_form.gender.data, create_teacher_form.adminNo.data,
                                   create_teacher_form.password.data, create_teacher_form.email.data, 
                                   create_teacher_form.module1.data)

        teachers_dict[teacher.get_adminNo()] = teacher
        db['Teachers'] = teachers_dict

        db.close()

        return redirect(url_for('retrieve_teachers'))

    return render_template('createTeacher.html', form=create_teacher_form)

@app.route('/createAdmin', methods=['GET', 'POST'])
@login_check
def create_admin():
    create_admin_form = CreateAdminForm(request.form)
    if request.method == 'POST' and create_admin_form.validate(): 
        admin_dict = {}
        db = shelve.open('Admin.db', 'c')

        try:
            if 'Admin' in db:
                admin_dict = db['Admin']
        except:
            print("Error retrieving admin from Admin.db.")

        admin = Admin.Admin(create_admin_form.name.data,
        create_admin_form.gender.data, create_admin_form.adminNo.data, 
        create_admin_form.password.data, create_admin_form.email.data)

        admin_dict[admin.get_adminNo()] = admin
        db['Admin'] = admin_dict

        db.close()
        
        return redirect(url_for('retrieve_admin'))
    
    return render_template('createAdmin.html', form=create_admin_form)

@app.route('/retrieveStudents', defaults={'search': None})
@app.route('/retrieveStudents/<search>', methods=['GET'])
@login_check
def retrieve_students(search):
    if search != None:
        pass

    students_dict = {}
    db = shelve.open('Students.db', 'r')
    students_dict = db['Students']
    db.close()

    students_list = []
    for key in students_dict:
        student = students_dict.get(key)
        students_list.append(student)

    #     if request.method == 'POST':
    #         searchFunction = request.form['search']
    #         return redirect(url_for('retrieve_students', search=searchFunction))
    # else:

    # searchFunction = request.args.get('search')
    return render_template('retrieveStudents.html', count=len(students_list), students_list=students_list)


@app.route('/retrieveTeachers')
@login_check
def retrieve_teachers():
    teachers_dict = {}
    db = shelve.open('Teachers.db', 'r')
    teachers_dict = db['Teachers']
    db.close()

    teachers_list = []
    for key in teachers_dict:
        teacher = teachers_dict.get(key)
        teachers_list.append(teacher)

    return render_template('retrieveTeachers.html', count=len(teachers_list), teachers_list=teachers_list)

@app.route('/retrieveAdmin')
@login_check
def retrieve_admin():
    admin_dict = {}
    db = shelve.open('Admin.db', 'r')
    admin_dict = db['Admin']
    db.close()

    admin_list = []
    for key in admin_dict:
        admin = admin_dict.get(key)
        admin_list.append(admin)

    return render_template('retrieveAdmin.html', count=len(admin_list), admin_list=admin_list)

@app.route('/updateStudent/<id>/', methods=['GET', 'POST'])
@login_check
def update_student(id):
    update_student_form = UpdateStudentForm(request.form)
    if request.method == 'POST' and update_student_form.validate():
        students_dict = {}
        db = shelve.open('Students.db', 'w')
        students_dict = db['Students']

        student = students_dict.get(id)
        student.set_name(update_student_form.name.data)
        student.set_gender(update_student_form.gender.data)
        student.set_birthDate(update_student_form.birthDate.data)
        student.set_email(update_student_form.email.data)
        student.set_adminNo(update_student_form.adminNo.data)
        student.set_password(update_student_form.password.data)

        db['Students'] = students_dict
        db.close()

        # session['user_updated'] = student.get_name()

        return redirect(url_for('retrieve_students'))
    else:
        students_dict = {}
        db = shelve.open('Students.db', 'r')
        students_dict = db['Students']
        db.close

        student = students_dict.get(id)
        update_student_form.name.data = student.get_name()
        update_student_form.gender.data = student.get_gender()
        update_student_form.birthDate.data = student.get_birthDate()
        update_student_form.email.data = student.get_email()
        update_student_form.adminNo.data = student.get_adminNo()
        update_student_form.password.data = student.get_password()

        return render_template('updateStudent.html', form=update_student_form)

@app.route('/updateTeacher/<id>/', methods=['GET', 'POST'])
@login_check
def update_teacher(id):
    update_teacher_form = UpdateTeacherForm(request.form)
    modules_list = ['Select']
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()
    
    for module in modules_dict:
        modules_list.append(modules_dict.get(module).get_module_name())
    update_teacher_form.module1.choices = modules_list

    if request.method == 'POST' and update_teacher_form.validate():
        teachers_dict = {}
        db = shelve.open('Teachers.db', 'w')
        teachers_dict = db['Teachers']

        teacher = teachers_dict.get(id)
        teacher.set_name(update_teacher_form.name.data)
        teacher.set_gender(update_teacher_form.gender.data)
        teacher.set_email(update_teacher_form.email.data)
        teacher.set_modules(update_teacher_form.module1.data)
        teacher.set_adminNo(update_teacher_form.adminNo.data)
        teacher.set_password(update_teacher_form.password.data)

        db['Teachers'] = teachers_dict
        db.close()

        return redirect(url_for('retrieve_teachers'))
    else:
        teachers_dict = {}
        db = shelve.open('Teachers.db', 'r')
        teachers_dict = db['Teachers']
        db.close

        teacher = teachers_dict.get(id)
        update_teacher_form.name.data = teacher.get_name()
        update_teacher_form.gender.data = teacher.get_gender()
        update_teacher_form.email.data = teacher.get_email()
        update_teacher_form.module1.data = teacher.get_modules()
        update_teacher_form.adminNo.data = teacher.get_adminNo()
        update_teacher_form.password.data = teacher.get_password()

        return render_template('updateTeacher.html', form=update_teacher_form)
    
@app.route('/updateAdmin/<id>/', methods=['GET', 'POST'])
@login_check
def update_admin(id):
    
    update_admin_form = UpdateAdminForm(request.form)
    if request.method == 'POST' and update_admin_form.validate():
        admin_dict = {}
        db = shelve.open('Admin.db', 'w')
        admin_dict = db['Admin']

        admin = admin_dict.get(id)
        admin.set_name(update_admin_form.name.data)
        admin.set_gender(update_admin_form.gender.data)
        admin.set_email(update_admin_form.email.data)
        admin.set_adminNo(update_admin_form.adminNo.data)
        admin.set_password(update_admin_form.password.data)
        
        db['Admin'] = admin_dict
        db.close()
        
        return redirect(url_for('retrieve_admin'))
    else:
        admin_dict = {}
        db = shelve.open('Admin.db', 'r')
        admin_dict = db['Admin']
        db.close

        admin = admin_dict.get(id)
        update_admin_form.name.data = admin.get_name()
        update_admin_form.gender.data = admin.get_gender()
        update_admin_form.email.data = admin.get_email()
        update_admin_form.adminNo.data = admin.get_adminNo()
        update_admin_form.password.data = admin.get_password()

        return render_template('updateAdmin.html', form=update_admin_form)

@app.route('/deleteStudent/<id>', methods=['POST'])
@login_check
def delete_student(id):
    students_dict = {}
    db = shelve.open('Students.db', 'w')
    students_dict = db['Students']
    students_dict.pop(id)

    db['Students'] = students_dict
    db.close()

    # session['student_deleted'] = student.get_name()

    return redirect(url_for('retrieve_students'))


@app.route('/deleteTeacher/<id>', methods=['POST'])
@login_check
def delete_teacher(id):
    teachers_dict = {}
    db = shelve.open('Teachers.db', 'w')
    teachers_dict = db['Teachers']
    teachers_dict.pop(id)

    db['Teachers'] = teachers_dict
    db.close()

    return redirect(url_for('retrieve_teachers'))

@app.route('/deleteAdmin/<id>', methods=['POST'])
@login_check
def delete_admin(id):
    admin_dict = {}
    db = shelve.open('Admin.db', 'w')
    admin_dict = db['Admin']
    admin_dict.pop(id)

    db['Admin'] = admin_dict
    db.close()
    
    return redirect(url_for('retrieve_admin'))

@app.route('/studentFeedback/<moduleID>', methods=['GET', 'POST'])
@login_check
def create_feedback(moduleID):
    feedback_form = CreateFeedback(request.form)
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    for module in modules_dict:
        if module == moduleID:
            feedback_form.modules.data = modules_dict.get(module).get_module_name()
        
    if request.method == 'POST' and feedback_form.validate():
        feedback_dict = {}
        db = shelve.open('Feedback.db', 'c')
        try:
            if 'Feedback' in db:
                feedback_dict = db['Feedback']
        except:
            print("Error retrieving feedback from Feedback.db.")
        
        message = [feedback_form.message1.data, feedback_form.message2.data, feedback_form.message3.data, feedback_form.message4.data]
        adminNo = session['account']
        while True:
            FeedbackKey = random.randint(0, 1000)
            if FeedbackKey not in feedback_dict:
                break
        
        feedback = Feedback.Feedback(FeedbackKey, adminNo, feedback_form.modules.data, message, status="Not Reviewed")
        feedback_dict[feedback.get_key()] = feedback
        db['Feedback'] = feedback_dict

        db.close()
        # session['user_created'] = student.get_name()
        return redirect(url_for('student_retrieve_feedback'))

    return render_template('studentFeedback.html', form=feedback_form)

@app.route('/studentRetrieveFeedback')
@login_check
def student_retrieve_feedback():
    feedback_dict = {}
    db = shelve.open('Feedback.db', 'r')
    feedback_dict = db['Feedback']
    db.close()
    feedback_list = []
    for key in feedback_dict:
        if feedback_dict.get(key).get_studentID() == session['account']:
            feedback_list.append(feedback_dict.get(key))
            
    modules_list = []
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    for module in modules_dict:
        modules_list.append(module)

    return render_template('studentRetrieveFeedback.html', count=len(feedback_list), feedback_list=feedback_list, modules_list=modules_list)

@app.route('/teacherRetrieveFeedback')
@login_check
def teacher_retrieve_feedback():
    teachers_dict = {}
    db = shelve.open('Teachers.db', 'r')
    teachers_dict = db['Teachers']
    db.close()
    for teacher in teachers_dict:
        if session['account'] == teacher:
            moduleName = teachers_dict.get(teacher).get_modules()

    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    for key in modules_dict:
        if moduleName == modules_dict.get(key).get_module_name():
            moduleID = modules_dict.get(key)
            
    feedback_dict = {}
    db = shelve.open('Feedback.db', 'r')
    feedback_dict = db['Feedback']
    db.close()

    feedback_list = []
    for key in feedback_dict:
        if moduleID.get_module_name() == feedback_dict.get(key).get_moduleID():
            feedback_list.append(feedback_dict.get(key))         

    students_dict = {}
    db = shelve.open('Students.db', 'r')
    students_dict = db['Students']
    db.close()
    students_list = []
    for student in students_dict:
        students_list.append(students_dict.get(student))

    return render_template('teacherRetrieveFeedback.html', count=len(feedback_list), feedback_list=feedback_list, students_list=students_list)

@app.route('/teacherViewFeedback/<int:id>/', methods=['GET', 'POST'])
@login_check
def teacher_view_feedback(id):
    
    teacher_view_feedback_form = TeacherViewFeedback(request.form)
    if request.method == 'POST' and teacher_view_feedback_form.validate():

        feedback_dict = {}
        db = shelve.open('Feedback.db', 'w')
        feedback_dict = db['Feedback']

        feedback = feedback_dict.get(id)
        messages = [teacher_view_feedback_form.message1.data, teacher_view_feedback_form.message2.data, 
                    teacher_view_feedback_form.message3.data, teacher_view_feedback_form.message4.data]
        feedback.set_message(messages)
        feedback.set_status('Reviewed')

        db['Feedback'] = feedback_dict
        db.close()
        
        return redirect(url_for('teacher_retrieve_feedback'))
    else:
        feedback_dict = {}
        db = shelve.open('Feedback.db', 'r')
        feedback_dict = db['Feedback']
        db.close

        feedback = feedback_dict.get(id)
        messages = feedback.get_message()
        teacher_view_feedback_form.message1.data = messages[0]
        teacher_view_feedback_form.message2.data = messages[1]
        teacher_view_feedback_form.message3.data = messages[2]
        teacher_view_feedback_form.message4.data = messages[3]
        
        return render_template('teacherViewFeedback.html', form=teacher_view_feedback_form)

@app.route('/updateFeedback/<int:id>/', methods=['GET', 'POST'])
@login_check
def update_feedback(id):
    update_feedback_form = UpdateFeedback(request.form)
    if request.method == 'POST' and update_feedback_form.validate():
        feedback_dict = {}
        db = shelve.open('Feedback.db', 'w')
        feedback_dict = db['Feedback']

        feedback = feedback_dict.get(id)
        messages = [update_feedback_form.message1.data, update_feedback_form.message2.data, 
                    update_feedback_form.message3.data, update_feedback_form.message4.data]
        feedback.set_message(messages)

        db['Feedback'] = feedback_dict
        db.close()
        
        return redirect(url_for('student_retrieve_feedback'))
    else:
        feedback_dict = {}
        db = shelve.open('Feedback.db', 'r')
        feedback_dict = db['Feedback']
        db.close

        feedback = feedback_dict.get(id)
        update_feedback_form.modules.data = feedback.get_moduleID()
        messages = feedback.get_message()
        update_feedback_form.message1.data = messages[0]
        update_feedback_form.message2.data = messages[1]
        update_feedback_form.message3.data = messages[2]
        update_feedback_form.message4.data = messages[3]
        
        return render_template('updateFeedback.html', form=update_feedback_form)

@app.route('/deleteFeedback/<int:id>', methods=['POST'])
@login_check
def delete_feedback(id):
    feedback_dict = {}
    db = shelve.open('Feedback.db', 'w')
    feedback_dict = db['Feedback']
    feedback_dict.pop(id)
    db['Feedback'] = feedback_dict
    db.close()

    return redirect(url_for('student_retrieve_feedback'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404

# ==============================Elijah's work============================================
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'mp4', 'jpg', 'png', 'txt'}

def allowed_file(filename):
    return'.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Create Assignments

@app.route('/createAssignments', methods=['GET', 'POST'])
@login_check
def create_assignment():
    db = shelve.open("Teachers.db", 'r')
    teacher_dict = {}
    try:
        teacher_dict = db["Teachers"]
    except:
        print("Error in retrieving Teachers from Teachers.db (Elijah's Part)")
        db["teachers"] = teacher_dict
    db.close()
    teacher = teacher_dict.get(session['account'])

    db = shelve.open("module.db", 'r')
    module_dict = {}
    try:
        module_dict = db["Modules"]
    except:
        print("Error in retrieving Modules from module.db (Elijah's Part)")
        db["Modules"] = module_dict
    db.close()
    for module in module_dict:
        if teacher.get_modules() == module_dict.get(module).get_module_name():
            moduleName = module_dict.get(module).get_module_name()

    db = shelve.open("class.db", 'r')
    class_dict = {}
    try:
        class_dict = db["Classes"]
    except:
        print("Error in retrieving Classes from class.db (Elijah's Part)")
        db["Classes"] = class_dict
    db.close()
    
    class_list = {}
    for classs in class_dict:
        classes = class_dict.get(classs)
        classes_assigned = classes.get_class_name()
        class_list[classes_assigned] = str(classes_assigned)
    
    create_assignment_form = CreateAssignmentForm(request.form)
    create_assignment_form.module_code.data = moduleName
    create_assignment_form.classes_assigned.choices = [(classs, class_list[classs]) for classs in class_list]
    
    if request.method == 'POST' and create_assignment_form.validate():
        assignments_dict = {}
        db = shelve.open('assignment.db','c')

        try:
            assignments_dict = db['Assignments']

        except:
            print("Error in retrieving Assignments from assignment.db (Initial Opening Stage)")
            db['Assignments'] = assignments_dict


        # File Upload Part
        if 'file' not in request.files:
            redirect('home')

        file = request.files['file']

        if file.filename == '':
            print('No Selected Field')
            return redirect(url_for('create_assignment'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        else:
            return redirect(url_for('create_assignment'))

        # Normal Form Part

        try:
            assignments_dict = db['Assignments']
            FileID = 1
            while True:
                if FileID in assignments_dict.keys():
                    FileID += 1

                else:
                    break
        
        except:
            print("Error in retrieveing Assignments from assignment.db")
            FileID = 1

        assignment = Assignment.Assignment(FileID, 
                                           create_assignment_form.AssignmentName.data,
                                           create_assignment_form.DueDate.data,
                                           create_assignment_form.AssignmentDetails.data,
                                           create_assignment_form.module_code.data, 
                                           create_assignment_form.classes_assigned.data,
                                           filename)

        assignments_dict[assignment.get_FileID()] = assignment
        db['Assignments'] = assignments_dict

        return redirect(url_for('teacher_retrieve_assignments', id=assignment.get_module_code()))
    return render_template('createAssignment.html', form = create_assignment_form)

#Update Assignments

@app.route('/updateAssignment/<int:FileID>/', methods=['GET', 'POST'])
@login_check
def update_assignment(FileID):
    db = shelve.open("Teachers.db", 'r')
    teacher_dict = {}
    try:
        teacher_dict = db["Teachers"]
    except:
        print("Error in retrieving Teachers from Teachers.db (Elijah's Part)")
        db["teachers"] = teacher_dict
    db.close()
    teacher = teacher_dict.get(session['account'])

    db = shelve.open("module.db", 'r')
    module_dict = {}
    try:
        module_dict = db["Modules"]
    except:
        print("Error in retrieving Modules from module.db (Elijah's Part)")
        db["Modules"] = module_dict
    db.close()
    for module in module_dict:
        if teacher.get_modules() == module_dict.get(module).get_module_name():
            moduleName = module_dict.get(module).get_module_name()

    db = shelve.open("class.db", 'r')
    class_dict = {}
    try:
        class_dict = db["Classes"]
    except:
        print("Error in retrieving Classes from class.db (Elijah's Part)")
        db["Classes"] = class_dict
    db.close()
    
    class_list = {}
    for classs in class_dict:
        classes = class_dict.get(classs)
        classes_assigned = classes.get_class_name()
        class_list[classes_assigned] = str(classes_assigned)
    
    update_assignment_form = CreateAssignmentForm(request.form)
    update_assignment_form.module_code.data = moduleName
    update_assignment_form.classes_assigned.choices = [(classs, class_list[classs]) for classs in class_list]
    
    if request.method == 'POST' and update_assignment_form.validate(): 
        assignment_dict = {}
        db = shelve.open('assignment.db', 'w')
        assignment_dict = db['Assignments']

        if 'file' not in request.files:
            redirect(url_for('home'))

        file = request.files['file']
        
        assignment = assignment_dict.get(FileID)
        assignment.set_AssignmentName(update_assignment_form.AssignmentName.data)
        assignment.set_DueDate(update_assignment_form.DueDate.data)
        assignment.set_AssignmentDetails(update_assignment_form.AssignmentDetails.data)
        assignment.set_module_code(update_assignment_form.module_code.data)
        assignment.set_classes_assigned(update_assignment_form.classes_assigned.data)

        if file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            assignment.set_filename(filename)

        db['Assignments'] = assignment_dict
        db.close()
        return redirect(url_for('teacher_retrieve_assignments', id = assignment.get_module_code()))

    else: 
        assignment_dict = {} 
        db = shelve.open('assignment.db', 'r')
        assignment_dict = db['Assignments']
        db.close()
        
        assignment = assignment_dict.get(FileID) 
        update_assignment_form.AssignmentName.data = assignment.get_AssignmentName()
        update_assignment_form.DueDate.data = assignment.get_DueDate()
        update_assignment_form.AssignmentDetails.data = assignment.get_AssignmentDetails()
        update_assignment_form.file.data = assignment.get_filename()
        update_assignment_form.module_code.data = assignment.get_module_code()
        update_assignment_form.classes_assigned.data = assignment.get_classes_assigned()

        return render_template('updateAssignment.html', form = update_assignment_form)
    
# Teacher Assignment View
@app.route('/teacherRetrieveAssignments', methods=['GET', 'POST'])
@login_check
def teacher_retrieve_assignments():

    teacher_dict = {}
    db = shelve.open('Teachers.db', 'r')
    teacher_dict = db['Teachers']
    db.close()
    teacher = teacher_dict.get(session['account'])

    assignments_dict = {}
    db = shelve.open('assignment.db')
    try:
        assignments_dict = db['Assignments']
    except:
        assignments_dict = {}
    db.close()

    assignments_list = []
    for assignment in assignments_dict:
        print(assignments_dict.get(assignment).get_module_code())
        if assignments_dict.get(assignment).get_module_code() == teacher.get_modules():
            assignments_list.append(assignments_dict.get(assignment))
    
    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != "":
        assignment_code = search_form.search_bar.data

        return redirect(url_for('retrieve_teacher_assignment_searches', assignment_search = assignment_code))
    return render_template("teacherRetrieveAssignments.html", form = search_form, count = len(assignments_list), assignments_list = assignments_list)

# Teacher's Search Bar

@app.route('/teacherRetrieveAssignments/<assignment_search>', methods=['GET', 'POST'])
@login_check
def retrieve_teacher_assignment_searches(assignment_search):

    teacher_dict = {}
    db = shelve.open('Teachers.db', 'r')
    teacher_dict = db['Teachers']
    db.close()
    teacher = teacher_dict.get(session['account'])

    assignment_dict = {}
    db = shelve.open('assignment.db', 'r')
    assignment_dict = db['Assignments']
    db.close()

    assignments_list = []
    try:
        for i in range (1, max(list(assignment_dict.keys())) + 1):
            if str(assignment_search) in str(assignment_dict[i].get_FileID()) or str(assignment_search).upper() in str(assignment_dict[i].get_AssignmentName()).upper() or str(assignment_search).upper() in str(assignment_dict[i].get_DueDate()).upper() and assignment_dict.get(assignment).get_module_code() == teacher.get_modules().split()[1]:
                assignment = assignment_dict.get(i)
                assignments_list.append(assignment)
    
    except:
        print("Empty Dictionary")

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != "":
        assignment_code = search_form.search_bar.data

        return redirect(url_for('retrieve_teacher_assignment_searches', assignment_search = assignment_code))
    return render_template('teacherRetrieveAssignments.html', form=search_form, count=len(assignments_list), assignments_list=assignments_list)

# Teacher Advanced Assignment View

@app.route('/teacherAdvancedAssignmentView/<int:file_id>', methods=['GET', 'POST'])
@login_check
def teacher_advanced_assignment_view(file_id):
    assignments_dict = {}
    db = shelve.open('assignment.db', 'c')
    assignments_dict = db['Assignments']
    
    db.close()

    assignment = assignments_dict.get(file_id)

    return render_template("teacherAdvancedAssignmentView.html", assignment = assignment)

# Student All Assignments View

@app.route('/studentRetrieveAllAssignments', methods=['GET', 'POST'])
@login_check
def student_retrieve_all_assignments():

    assignments_dict = {}
    db = shelve.open('assignment.db','c')
    try:
        assignments_dict = db['Assignments']
    except:
        assignments_dict = {}
    finally:
        db.close()

    class_dict = {}
    db = shelve.open('class.db', 'r')
    class_dict = db['Classes']
    db.close()

    User = session['account'] + "." + session['name']
    for classs in class_dict.values():
        for i in classs.get_student_names():
            if User in i:
                class_assigned = classs.get_class_name()

    assignments_list = []
    try:
        for i in assignments_dict.keys():
            if i in assignments_dict.keys() and assignments_dict[i].get_classes_assigned() == class_assigned:
                assignment = assignments_dict.get(i)
                assignments_list.append(assignment)
    
    except:
        print("Empty Dictionary")

    now = date.today()

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != "":
        assignment_code = search_form.search_bar.data

        return redirect(url_for('retrieve_students_all_assignment_search', assignment_search = assignment_code))

    return render_template("studentRetrieveAssignments.html", form=search_form, count = len(assignments_list), assignments_list=assignments_list, now = now)

# Student's Search All Assignments Bar

@app.route('/studentRetrieveAllAssignments/<assignment_search>', methods=['GET', 'POST'])
@login_check
def retrieve_students_all_assignment_search(assignment_search):
    
    assignment_dict = {}
    db = shelve.open('assignment.db', 'r')
    assignment_dict = db['Assignments']
    db.close()

    class_dict = {}
    db = shelve.open('class.db', 'r')
    class_dict = db['Classes']
    db.close()

    User = session['account'] + "." + session['name']
    for classs in class_dict.values():
        for i in classs.get_student_names():
            if User in i:
                class_assigned = classs.get_class_name()

    assignments_list = []
    try:
        for i in range (1, max(list(assignment_dict.keys())) + 1):
            if str(assignment_search) in str(assignment_dict[i].get_FileID()) or str(assignment_search).upper() in str(assignment_dict[i].get_AssignmentName()).upper() or str(assignment_search).upper() in str(assignment_dict[i].get_DueDate()).upper() and assignment.classes_assigned() == class_assigned:
                assignment = assignment_dict.get(i)
                assignments_list.append(assignment)
    
    except:
        print("Empty Dictionary")

    now = date.today()

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != "":
        assignment_code = search_form.search_bar.data

        return redirect(url_for('retrieve_students_assignment_search', assignment_search = assignment_code))
    return render_template('studentRetrieveAssignments.html', now = now, form=search_form, count=len(assignments_list), assignments_list=assignments_list)

# Student Assignment View

@app.route('/studentRetrieveAssignments/<module_code>', methods=['GET', 'POST'])
@login_check
def student_retrieve_assignments(module_code):

    assignments_dict = {}
    db = shelve.open('assignment.db','c')
    try:
        assignments_dict = db['Assignments']
    except:
        db['Assignments'] = assignments_dict
    db.close()

    assignments_list = []
    try:
        for i in range (1, max(list(assignments_dict.keys())) + 1):
            if i in assignments_dict.keys():
                assignment = assignments_dict[i]
                AssignmentModuleCode = assignment.get_module_code()
                if AssignmentModuleCode == module_code:
                    assignments_list.append(assignment)

    except:
        print("Empty Dictionary")

    now = date.today()

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != "":
        assignment_code = search_form.search_bar.data

        return redirect(url_for('retrieve_students_assignment_search', now = now, module_code = AssignmentModuleCode, assignment_search = assignment_code))
    return render_template("studentRetrieveAssignments.html", form=search_form, count = len(assignments_list), assignments_list=assignments_list, now = now)

# Student's Search Bar

@app.route('/studentRetrieveAssignments/<module_code>/<assignment_search>', methods=['GET', 'POST'])
@login_check
def retrieve_students_assignment_search(module_code, assignment_search):
    assignment_dict = {}
    db = shelve.open('assignment.db', 'r')
    assignment_dict = db['Assignments']
    db.close()

    class_dict = {}
    db = shelve.open('class.db', 'r')
    class_dict = db['Classes']
    db.close()

    assignments_list = []
    try:
        for i in assignment_dict.keys():
            if str(assignment_search) in str(assignment_dict[i].get_FileID()) or str(assignment_search).upper() in str(assignment_dict[i].get_AssignmentName()).upper() or str(assignment_search).upper() in str(assignment_dict[i].get_DueDate()).upper() and assignment.get_module_code() == module_code:
                assignment = assignment_dict.get(i)
                assignments_list.append(assignment)
    
    except:
        print("Empty Dictionary")

    now = date.today()

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != "":
        assignment_code = search_form.search_bar.data

        return redirect(url_for('retrieve_students_assignment_search', module_code = module_code, assignment_search = assignment_code))
    return render_template('studentRetrieveAssignments.html', now = now, form=search_form, count=len(assignments_list), assignments_list=assignments_list)

# Student Advanced Assignment View

@app.route('/studentAdvancedAssignmentView/<int:file_id>', methods=['GET', 'POST'])
@login_check
def student_advanced_assignment_view(file_id):
    assignments_dict = {}
    db = shelve.open('assignment.db', 'c')
    try:
        assignments_dict = db['Assignments']
    except:
        assignments_dict = {}
    
    db.close()

    assignment = assignments_dict.get(file_id)

    return render_template("studentAdvancedAssignmentView.html", assignment = assignment)

#Delete Assignments

@app.route('/deleteAssignment/<int:id>', methods=['POST'])
@login_check
def delete_assignment(id):
    assignment_dict = {}
    db = shelve.open('assignment.db', 'w')
    assignment_dict = db['Assignments']

    assignment_dict.pop(id)

    db['Assignments'] = assignment_dict
    db.close()

    return redirect(url_for('teacher_retrieve_assignments'))

# Download Assignments

@app.route('/downloadAssignment/<string:filename>', methods=['GET', 'POST'])
@login_check
def download_assignment(filename):
    return send_file("static/files/" + filename, as_attachment=True)

@app.route("/quoteGenerator")
def show_quote():
    quotes = ["Success is not final, failure is not fatal: it is the courage to continue that counts.", "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle.", "Don't watch the clock; do what it does. Keep going.", "Don't wait for opportunity. Create it.", "The only way to do great work is to love what you do.","Life isn’t about getting and having, it’s about giving and being.","Whatever the mind of man can conceive and believe, it can achieve.","Strive not to be a success, but rather to be of value.","Two roads diverged in a wood, and I—I took the one less traveled by, And that has made all the difference.","I attribute my success to this: I never gave or took any excuse.","You miss 100% of the shots you don’t take.","I’ve missed more than 9000 shots in my career. I’ve lost almost 300 games. 26 times I’ve been trusted to take the game winning shot and missed. I’ve failed over and over and over again in my life. And that is why I succeed.","The most difficult thing is the decision to act, the rest is merely tenacity.","Every strike brings me closer to the next home run.",
    "Definiteness of purpose is the starting point of all achievement.",
    "We must balance conspicuous consumption with conscious capitalism.",
    "Life is what happens to you while you’re busy making other plans.",
    "We become what we think about.",
    "Twenty years from now you will be more disappointed by the things that you didn’t do than by the ones you did do, so throw off the bowlines, sail away from safe harbor, catch the trade winds in your sails.  Explore, Dream, Discover.",
    "Life is 10% what happens to me and 90 per cent of how I react to it.",
    "The most common way people give up their power is by thinking they don’t have any.",
    "The mind is everything. What you think you become.",
    "The best time to plant a tree was 20 years ago. The second best time is now.",
    "An unexamined life is not worth living.",
    "Eighty percent of success is showing up.",
    "Your time is limited, so don’t waste it living someone else’s life.",
    "Winning isn’t everything, but wanting to win is.",
    "I am not a product of my circumstances. I am a product of my decisions.",
    "Every child is an artist.  The problem is how to remain an artist once he grows up.",
    "You can never cross the ocean until you have the courage to lose sight of the shore.",
    "I’ve learned that people will forget what you said, people will forget what you did, but people will never forget how you made them feel.",
    "Either you run the day, or the day runs you.",
    "Whether you think you can or you think you can’t, you’re right.",
    "The two most important days in your life are the day you are born and the day you find out why.",
    "Whatever you can do, or dream you can, begin it.  Boldness has genius, power and magic in it.",
    "The best revenge is massive success.",
    "People often say that motivation doesn’t last. Well, neither does bathing.  That’s why we recommend it daily.",
    "Life shrinks or expands in proportion to one’s courage.",
    "If you hear a voice within you say “you cannot paint,” then by all means paint and that voice will be silenced.",
    "There is only one way to avoid criticism: do nothing, say nothing, and be nothing.",
    "Ask and it will be given to you; search, and you will find; knock and the door will be opened for you.",
    "The only person you are destined to become is the person you decide to be.",
    "Go confidently in the direction of your dreams.  Live the life you have imagined.",
    "When I stand before God at the end of my life, I would hope that I would not have a single bit of talent left and could say, I used everything you gave me.",
    "Few things can help an individual more than to place responsibility on him, and to let him know that you trust him.",
    "Certain things catch your eye, but pursue only those that capture the heart.",
    "Believe you can and you’re halfway there.",
    "Everything you’ve ever wanted is on the other side of fear.",
    "We can easily forgive a child who is afraid of the dark; the real tragedy of life is when men are afraid of the light.",
    "Teach thy tongue to say, “I do not know,” and thous shalt progress.",
    "Start where you are. Use what you have.  Do what you can.",
    "When I was 5 years old, my mother always told me that happiness was the key to life.  When I went to school, they asked me what I wanted to be when I grew up.  I wrote down ‘happy’.  They told me I didn’t understand the assignment, and I told them they didn’t understand life.",
    "Fall seven times and stand up eight.",
    "When one door of happiness closes, another opens, but often we look so long at the closed door that we do not see the one that has been opened for us.",
    "Everything has beauty, but not everyone can see.",
    "How wonderful it is that nobody need wait a single moment before starting to improve the world.",
    "When I let go of what I am, I become what I might be.",
    "Life is not measured by the number of breaths we take, but by the moments that take our breath away.",
    "Happiness is not something readymade.  It comes from your own actions.",
    "If you’re offered a seat on a rocket ship, don’t ask what seat! Just get on.",
    "First, have a definite, clear practical ideal; a goal, an objective. Second, have the necessary means to achieve your ends; wisdom, money, materials, and methods. Third, adjust all your means to that end.",
    "If the wind will not serve, take to the oars.",
    "You can’t fall if you don’t climb.  But there’s no joy in living your whole life on the ground.",
    "We must believe that we are gifted for something, and that this thing, at whatever cost, must be attained.",
    "Too many of us are not living our dreams because we are living our fears.",
    "Challenges are what make life interesting and overcoming them is what makes life meaningful.",
    "If you want to lift yourself up, lift up someone else.",
    "I have been impressed with the urgency of doing. Knowing is not enough; we must apply. Being willing is not enough; we must do.",
    "Limitations live only in our minds.  But if we use our imaginations, our possibilities become limitless.",
    "You take your life in your own hands, and what happens? A terrible thing, no one to blame.",
    "What’s money? A man is a success if he gets up in the morning and goes to bed at night and in between does what he wants to do.",
    "I didn’t fail the test. I just found 100 ways to do it wrong.",
    "In order to succeed, your desire for success should be greater than your fear of failure.",
    "A person who never made a mistake never tried anything new.",
    "The person who says it cannot be done should not interrupt the person who is doing it.",
    "There are no traffic jams along the extra mile.",
    "It is never too late to be what you might have been.",
    "You become what you believe.",
    "I would rather die of passion than of boredom.",
    "A truly rich man is one whose children run into his arms when his hands are empty.",
    "It is not what you do for your children, but what you have taught them to do for themselves, that will make them successful human beings.",
    "If you want your children to turn out well, spend twice as much time with them, and half as much money.",
    "Build your own dreams, or someone else will hire you to build theirs.",
    "The battles that count aren’t the ones for gold medals. The struggles within yourself–the invisible battles inside all of us–that’s where it’s at.",
    "Education costs money.  But then so does ignorance.",
    "I have learned over the years that when one’s mind is made up, this diminishes fear.",
    "It does not matter how slowly you go as long as you do not stop.",
    "If you look at what you have in life, you’ll always have more. If you look at what you don’t have in life, you’ll never have enough.",
    "Remember that not getting what you want is sometimes a wonderful stroke of luck.","You can’t use up creativity.  The more you use, the more you have.","Dream big and dare to fail.","Our lives begin to end the day we become silent about things that matter.",
    "Do what you can, where you are, with what you have.","If you do what you’ve always done, you’ll get what you’ve always gotten.",
    "Dreaming, after all, is a form of planning.","It’s your place in the world; it’s your life. Go on and do all you can with it, and make it the life you want to live.","You may be disappointed if you fail, but you are doomed if you don’t try.",
    "Remember no one can make you feel inferior without your consent.",
    "Life is what we make it, always has been, always will be.",
    "The question isn’t who is going to let me; it’s who is going to stop me.","When everything seems to be going against you, remember that the airplane takes off against the wind, not with it.","It’s not the years in your life that count. It’s the life in your years.","Change your thoughts and you change your world.","Either write something worth reading or do something worth writing.","Nothing is impossible, the word itself says, “I’m possible!”","The only way to do great work is to love what you do.","If you can dream it, you can achieve it."]
    quote = random.choice(quotes)
    return render_template("quoteGenerator.html", quote=quote)

# ==============================Allister's work============================================

module_name = ''
student_namess = []
teacher_names = []
module_id = ''
class_id = 0

@app.route('/createModule', methods=['GET', 'POST'])
@login_check
def create_module():
    create_module_form = CreateModuleForm(request.form)
    db = shelve.open("class.db", 'c')
    classes_dict = {}
    try:
        classes_dict = db["Classes"]
    except:
        db["Classes"] = classes_dict
    db.close()

    class_assigned_choices = ['']
    for i in list(classes_dict.keys()):
        class_assigned_choices.append(str(classes_dict[i].get_class_id()) + '.' + classes_dict[i].get_class_name())

    create_module_form.classes_assigned.choices = class_assigned_choices
    create_module_form.classes_assigned2.choices = class_assigned_choices
    create_module_form.classes_assigned3.choices = class_assigned_choices
    create_module_form.classes_assigned4.choices = class_assigned_choices
    create_module_form.classes_assigned5.choices = class_assigned_choices
    create_module_form.classes_assigned6.choices = class_assigned_choices
    create_module_form.classes_assigned7.choices = class_assigned_choices
    create_module_form.classes_assigned8.choices = class_assigned_choices
    if request.method == 'POST' and create_module_form.validate():
        modules_dict = {}
        db = shelve.open('module.db', 'c')
        filename = ''

        try:
            modules_dict = db['Modules']
        except:
            print("Error in retrieving Modules from module.db.")

        file = request.files['module_image']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save("static/img/" + filename)

        classes_assigned = []
        classes_assigned.append(create_module_form.classes_assigned.data)
        if create_module_form.classes_assigned2.data != '' and create_module_form.classes_assigned2.data not in classes_assigned:
            classes_assigned.append(create_module_form.classes_assigned2.data)
        if create_module_form.classes_assigned3.data != '' and create_module_form.classes_assigned3.data not in classes_assigned:
            classes_assigned.append(create_module_form.classes_assigned3.data)
        if create_module_form.classes_assigned4.data != '' and create_module_form.classes_assigned4.data not in classes_assigned:
            classes_assigned.append(create_module_form.classes_assigned4.data)
        if create_module_form.classes_assigned5.data != '' and create_module_form.classes_assigned5.data not in classes_assigned:
            classes_assigned.append(create_module_form.classes_assigned5.data)
        if create_module_form.classes_assigned6.data != '' and create_module_form.classes_assigned6.data not in classes_assigned:
            classes_assigned.append(create_module_form.classes_assigned6.data)
        if create_module_form.classes_assigned7.data != '' and create_module_form.classes_assigned7.data not in classes_assigned:
            classes_assigned.append(create_module_form.classes_assigned7.data)
        if create_module_form.classes_assigned8.data != '' and create_module_form.classes_assigned8.data not in classes_assigned:
            classes_assigned.append(create_module_form.classes_assigned8.data)

        module = Module.Module(filename, create_module_form.module_code.data, create_module_form.module_name.data, create_module_form.implementation_date.data, create_module_form.module_description.data, classes_assigned)
        modules_dict[module.get_module_code()] = module
        db['Modules'] = modules_dict

        db.close()

        session['module_created'] = module.get_module_code() + " " + module.get_module_name()

        return redirect(url_for('retrieve_modules'))
    return render_template('createModule.html', form=create_module_form)

@app.route('/createClass', methods=['GET', 'POST'])
@login_check
def create_class():
    create_class_form = CreateClassForm(request.form)
    db = shelve.open("Students.db", 'c')
    students_dict = {}
    try:
        students_dict = db["Students"]
    except:
        db["Students"] = students_dict
    db.close()

    db = shelve.open("Teachers.db", 'c')
    teachers_dict = {}
    try:
        teachers_dict = db["Teachers"]
    except:
        db["Teachers"] = teachers_dict
    db.close()

    students_choices = ['']
    for i in list(students_dict.keys()):
        students_choices.append(str(students_dict[i].get_adminNo()) + '.' + students_dict[i].get_name())
    create_class_form.student_names.choices = students_choices
    create_class_form.student_names2.choices = students_choices
    create_class_form.student_names3.choices = students_choices
    create_class_form.student_names4.choices = students_choices
    create_class_form.student_names5.choices = students_choices
    create_class_form.student_names6.choices = students_choices
    create_class_form.student_names7.choices = students_choices
    create_class_form.student_names8.choices = students_choices
    create_class_form.student_names9.choices = students_choices
    create_class_form.student_names10.choices = students_choices
    create_class_form.student_names11.choices = students_choices
    create_class_form.student_names12.choices = students_choices
    create_class_form.student_names13.choices = students_choices
    create_class_form.student_names14.choices = students_choices
    create_class_form.student_names15.choices = students_choices
    create_class_form.student_names16.choices = students_choices
    create_class_form.student_names17.choices = students_choices
    create_class_form.student_names18.choices = students_choices
    create_class_form.student_names19.choices = students_choices
    create_class_form.student_names20.choices = students_choices
    create_class_form.student_names21.choices = students_choices
    create_class_form.student_names22.choices = students_choices
    create_class_form.student_names23.choices = students_choices
    create_class_form.student_names24.choices = students_choices
    create_class_form.student_names25.choices = students_choices
    create_class_form.student_names26.choices = students_choices
    create_class_form.student_names27.choices = students_choices
    create_class_form.student_names28.choices = students_choices
    create_class_form.student_names29.choices = students_choices
    create_class_form.student_names30.choices = students_choices
    create_class_form.student_names31.choices = students_choices
    create_class_form.student_names32.choices = students_choices
    create_class_form.student_names33.choices = students_choices
    create_class_form.student_names34.choices = students_choices
    create_class_form.student_names35.choices = students_choices
    create_class_form.student_names36.choices = students_choices
    create_class_form.student_names37.choices = students_choices
    create_class_form.student_names38.choices = students_choices
    create_class_form.student_names39.choices = students_choices
    create_class_form.student_names40.choices = students_choices

    teacher_choices = ['']
    for i in list(teachers_dict.keys()):
        teacher_choices.append(str(teachers_dict[i].get_adminNo()) + '.' + teachers_dict[i].get_name())
    create_class_form.form_teachers.choices = teacher_choices
    create_class_form.form_teachers2.choices = teacher_choices
    create_class_form.form_teachers3.choices = teacher_choices
    create_class_form.form_teachers4.choices = teacher_choices

    if request.method == 'POST' and create_class_form.validate():
        classes_dict = {}
        db = shelve.open('class.db', 'c')

        try:
            classes_dict = db['Classes']
            class_id = 1
            while True:
                if class_id in classes_dict.keys():
                    class_id += 1
                else:
                    break

        except:
            print("Error in retrieving Classes from class.db.")
            class_id = 1

        student_names = []
        student_names.append(create_class_form.student_names.data)
        if create_class_form.student_names2.data != '' and create_class_form.student_names2.data not in student_names:
            student_names.append(create_class_form.student_names2.data)
        if create_class_form.student_names3.data != '' and create_class_form.student_names3.data not in student_names:
            student_names.append(create_class_form.student_names3.data)
        if create_class_form.student_names4.data != '' and create_class_form.student_names4.data not in student_names:
            student_names.append(create_class_form.student_names4.data)
        if create_class_form.student_names5.data != '' and create_class_form.student_names5.data not in student_names:
            student_names.append(create_class_form.student_names5.data)
        if create_class_form.student_names6.data != '' and create_class_form.student_names6.data not in student_names:
            student_names.append(create_class_form.student_names6.data)
        if create_class_form.student_names7.data != '' and create_class_form.student_names7.data not in student_names:
            student_names.append(create_class_form.student_names7.data)
        if create_class_form.student_names8.data != '' and create_class_form.student_names8.data not in student_names:
            student_names.append(create_class_form.student_names8.data)
        if create_class_form.student_names9.data != '' and create_class_form.student_names9.data not in student_names:
            student_names.append(create_class_form.student_names9.data)
        if create_class_form.student_names10.data != '' and create_class_form.student_names10.data not in student_names:
            student_names.append(create_class_form.student_names10.data)
        if create_class_form.student_names11.data != '' and create_class_form.student_names11.data not in student_names:
            student_names.append(create_class_form.student_names11.data)
        if create_class_form.student_names12.data != '' and create_class_form.student_names12.data not in student_names:
            student_names.append(create_class_form.student_names12.data)
        if create_class_form.student_names13.data != '' and create_class_form.student_names13.data not in student_names:
            student_names.append(create_class_form.student_names13.data)
        if create_class_form.student_names14.data != '' and create_class_form.student_names14.data not in student_names:
            student_names.append(create_class_form.student_names14.data)
        if create_class_form.student_names15.data != '' and create_class_form.student_names15.data not in student_names:
            student_names.append(create_class_form.student_names15.data)
        if create_class_form.student_names16.data != '' and create_class_form.student_names16.data not in student_names:
            student_names.append(create_class_form.student_names16.data)
        if create_class_form.student_names17.data != '' and create_class_form.student_names17.data not in student_names:
            student_names.append(create_class_form.student_names17.data)
        if create_class_form.student_names18.data != '' and create_class_form.student_names18.data not in student_names:
            student_names.append(create_class_form.student_names18.data)
        if create_class_form.student_names19.data != '' and create_class_form.student_names19.data not in student_names:
            student_names.append(create_class_form.student_names19.data)
        if create_class_form.student_names20.data != '' and create_class_form.student_names20.data not in student_names:
            student_names.append(create_class_form.student_names20.data)
        if create_class_form.student_names21.data != '' and create_class_form.student_names21.data not in student_names:
            student_names.append(create_class_form.student_names21.data)
        if create_class_form.student_names22.data != '' and create_class_form.student_names22.data not in student_names:
            student_names.append(create_class_form.student_names22.data)
        if create_class_form.student_names23.data != '' and create_class_form.student_names23.data not in student_names:
            student_names.append(create_class_form.student_names23.data)
        if create_class_form.student_names24.data != '' and create_class_form.student_names24.data not in student_names:
            student_names.append(create_class_form.student_names24.data)
        if create_class_form.student_names25.data != '' and create_class_form.student_names25.data not in student_names:
            student_names.append(create_class_form.student_names25.data)
        if create_class_form.student_names26.data != '' and create_class_form.student_names26.data not in student_names:
            student_names.append(create_class_form.student_names26.data)
        if create_class_form.student_names27.data != '' and create_class_form.student_names27.data not in student_names:
            student_names.append(create_class_form.student_names27.data)
        if create_class_form.student_names28.data != '' and create_class_form.student_names28.data not in student_names:
            student_names.append(create_class_form.student_names28.data)
        if create_class_form.student_names29.data != '' and create_class_form.student_names29.data not in student_names:
            student_names.append(create_class_form.student_names29.data)
        if create_class_form.student_names30.data != '' and create_class_form.student_names30.data not in student_names:
            student_names.append(create_class_form.student_names30.data)
        if create_class_form.student_names31.data != '' and create_class_form.student_names31.data not in student_names:
            student_names.append(create_class_form.student_names31.data)
        if create_class_form.student_names32.data != '' and create_class_form.student_names32.data not in student_names:
            student_names.append(create_class_form.student_names32.data)
        if create_class_form.student_names33.data != '' and create_class_form.student_names33.data not in student_names:
            student_names.append(create_class_form.student_names33.data)
        if create_class_form.student_names34.data != '' and create_class_form.student_names34.data not in student_names:
            student_names.append(create_class_form.student_names34.data)
        if create_class_form.student_names35.data != '' and create_class_form.student_names35.data not in student_names:
            student_names.append(create_class_form.student_names35.data)
        if create_class_form.student_names36.data != '' and create_class_form.student_names36.data not in student_names:
            student_names.append(create_class_form.student_names36.data)
        if create_class_form.student_names37.data != '' and create_class_form.student_names37.data not in student_names:
            student_names.append(create_class_form.student_names37.data)
        if create_class_form.student_names38.data != '' and create_class_form.student_names38.data not in student_names:
            student_names.append(create_class_form.student_names38.data)
        if create_class_form.student_names39.data != '' and create_class_form.student_names39.data not in student_names:
            student_names.append(create_class_form.student_names39.data)
        if create_class_form.student_names40.data != '' and create_class_form.student_names40.data not in student_names:
            student_names.append(create_class_form.student_names40.data)

        form_teachers = []
        form_teachers.append(create_class_form.form_teachers.data)
        if create_class_form.form_teachers2.data != '' and create_class_form.form_teachers2.data not in form_teachers:
            form_teachers.append(create_class_form.form_teachers2.data)
        if create_class_form.form_teachers3.data != '' and create_class_form.form_teachers2.data not in form_teachers:
            form_teachers.append(create_class_form.form_teachers3.data)
        if create_class_form.form_teachers4.data != '' and create_class_form.form_teachers2.data not in form_teachers:
            form_teachers.append(create_class_form.form_teachers4.data)

        classs = Class.Class(class_id, create_class_form.class_name.data, create_class_form.implementation_date.data, student_names, form_teachers, create_class_form.class_description.data,)
        classes_dict[classs.get_class_id()] = classs
        db['Classes'] = classes_dict

        db.close()

        session['class_created'] = str(classs.get_class_id()) + "." + classs.get_class_name()

        return redirect(url_for('retrieve_classes'))
    return render_template('createClass.html', form=create_class_form)

@app.route('/retrieveModules', methods=['GET', 'POST'])
@login_check
def retrieve_modules():
    modules_dict = {}
    db = shelve.open('module.db', 'c')
    modules_dict = db['Modules']
    if module_name != '' and module_id in modules_dict:
        if modules_dict[module_id].get_module_name() == '':
            modules_dict[module_id].set_module_name(module_name)
            db['Modules'] = modules_dict
    db.close()

    modules_list = []
    for key in modules_dict:
        module = modules_dict.get(key)
        modules_list.append(module)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        module_search = search_form.search_bar.data

        return redirect(url_for('retrieve_module_searches', module_search=module_search))
    return render_template('retrieveModules.html', form=search_form, count=len(modules_list), modules_list=modules_list)

@app.route('/retrieveModuleClasses/<module_code>', methods=['GET', 'POST'])
@login_check
def retrieve_module_classes(module_code):
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()
    classes_dict = {}
    db = shelve.open('class.db', 'r')
    classes_dict = db["Classes"]
    db.close()

    classes_assigned_list = []
    for i in classes_dict.values():
        if str(i.get_class_id()) + "." + i.get_class_name() in modules_dict[module_code].get_classes_assigned():
            classes_assigned_list.append(i)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        class_search = search_form.search_bar.data

        return redirect(url_for('retrieve_module_classes_searches', module_code=module_code, class_search=class_search))
    return render_template('retrieveModuleClasses.html', form=search_form, count=len(classes_assigned_list), classes_assigned_list=classes_assigned_list)

@app.route('/retrieveModulesStudent', methods=['GET', 'POST'])
@login_check
def retrieve_student_modules():
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()
    classes_dict = {}
    db = shelve.open('class.db', 'r')
    classes_dict = db['Classes']
    db.close()
    students_dict = {}
    db = shelve.open('Students.db', 'r')
    students_dict = db['Students']
    db.close()

    student_id = students_dict[session["account"]].get_adminNo() + "." + students_dict[session["account"]].get_name()

    class_assigned = []
    for values in classes_dict.values():
        if student_id in values.get_student_names():
            class_assigned = str(values.get_class_id()) + "." + values.get_class_name()

    modules_list = []
    for key in modules_dict:
        if date.today() >= modules_dict[key].get_implementation_date() and class_assigned in modules_dict[key].get_classes_assigned():
            module = modules_dict.get(key)
            modules_list.append(module)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        module_search = search_form.search_bar.data

        return redirect(url_for('retrieve_module_student_searches', module_search=module_search))
    return render_template('retrieveModuleStudent.html', form=search_form, count=len(modules_list), modules_list=modules_list)

@app.route('/retrieveModulesTeacher', methods=['GET', 'POST'])
@login_check
def retrieve_teacher_modules():
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()
    teachers_dict = {}
    db = shelve.open('Teachers.db', 'r')
    teachers_dict = db['Teachers']
    db.close()

    print(date.today())
    print(teachers_dict[session['account']].get_modules())
    modules_list = []
    for key in modules_dict:
        if date.today() >= modules_dict[key].get_implementation_date() and modules_dict[key].get_module_name() == teachers_dict[session['account']].get_modules():
            module = modules_dict.get(key)
            modules_list.append(module)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        module_search = search_form.search_bar.data

        return redirect(url_for('retrieve_module_teacher_searches', module_search=module_search))
    return render_template('retrieveModuleTeacher.html', form=search_form, count=len(modules_list), modules_list=modules_list)

@app.route('/retrieveClassesTeacher/<module_code>', methods=['GET', 'POST'])
@login_check
def retrieve_teacher_module_classes(module_code):
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()
    classes_dict = {}
    db = shelve.open('class.db', 'r')
    classes_dict = db['Classes']
    db.close()

    module = modules_dict[module_code]

    classes_list = []
    for j in classes_dict.values():
        if str(j.get_class_id()) + "." + j.get_class_name() in modules_dict[module_code].get_classes_assigned():
            classes_list.append(j)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        class_search = search_form.search_bar.data

        return redirect(url_for('retrieve_teacher_module_classes_searches', module_code=module_code, class_search=class_search))
    return render_template('moduleClassesTeachers.html', form=search_form, count=len(classes_list), classes_list=classes_list, module=module)

@app.route('/retrieveClasses', methods=['GET', 'POST'])
@login_check
def retrieve_classes():
    classes_dict = {}
    db = shelve.open('class.db', 'c')
    classes_dict = db['Classes']
    db.close()

    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()

    classes_assigned_list = []
    for k in modules_dict.values():
        for l in k.get_classes_assigned():
            classes_assigned_list.append(l)

    classes_list = []
    try:
        for i in range(1, max(list(classes_dict.keys())) + 1):
            if i in classes_dict.keys():
                classs = classes_dict.get(i)
                classes_list.append(classs)
    except:
        print("Empty Dictionary")

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        class_search = search_form.search_bar.data

        return redirect(url_for('retrieve_class_searches', class_search=class_search))
    return render_template('retrieveClasses.html', form=search_form, count=len(classes_list), classes_list=classes_list, classes_assigned_list=classes_assigned_list)

@app.route('/retrieveClassesInfo/<int:class_id>', methods=['GET', 'POST'])
@login_check
def retrieve_classes_information(class_id):
    classes_dict = {}
    db = shelve.open('class.db', 'r')
    classes_dict = db['Classes']
    db.close()
    teachers_dict = {}
    db = shelve.open('Teachers.db', 'r')
    teachers_dict = db['Teachers']
    db.close()
    students_dict = {}
    db = shelve.open('Students.db', 'r')
    students_dict = db['Students']
    db.close()
    if student_namess != [] and int(class_id) in classes_dict.keys():
        if classes_dict[class_id].get_student_names() == []:
            db = shelve.open('class.db', 'c')
            classes_dict = db['Classes']
            classes_dict[class_id].set_student_names(student_namess)
            db["Classes"] = classes_dict
            db.close()
    if teacher_names != [] and int(class_id) in classes_dict.keys():
        if classes_dict[class_id].get_form_teachers() == []:
            db = shelve.open('class.db', 'c')
            classes_dict = db['Classes']
            classes_dict[class_id].set_form_teachers(teacher_names)
            db["Classes"] = classes_dict
            db.close()

    teachers_list = []
    for k in teachers_dict.values():
        if k.get_adminNo() + "." + k.get_name() in classes_dict[class_id].get_form_teachers():
            teachers_list.append(k)

    students_list = []
    for l in students_dict.values():
        if l.get_adminNo() + "." + l.get_name() in classes_dict[class_id].get_student_names():
            students_list.append(l)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        person_search = search_form.search_bar.data

        return redirect(url_for('retrieve_classes_information_searches', class_id=class_id, person_search=person_search))
    return render_template('retrieveClassesInformation.html', form=search_form, count=len(teachers_list) + len(students_list), teachers_list=teachers_list, students_list=students_list)

@app.route('/retrieveModules/<module_search>', methods=['GET', 'POST'])
@login_check
def retrieve_module_searches(module_search):
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()

    modules_list = []
    for key in modules_dict.keys():
        if module_search.upper() in modules_dict[key].get_module_code().upper() or module_search.upper() in modules_dict[key].get_module_name().upper() or module_search in str(modules_dict[key].get_implementation_date()) or module_search.upper() in modules_dict[key].get_module_description().upper():
            module = modules_dict.get(key)
            modules_list.append(module)
        else:
            for k in modules_dict[key].get_classes_assigned():
                if module_search.upper() in k.upper():
                    module = modules_dict.get(key)
                    if module not in modules_list:
                        modules_list.append(module)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        module_search = search_form.search_bar.data

        return redirect(url_for('retrieve_module_searches', module_search=module_search))
    return render_template('retrieveModules.html', form=search_form, count=len(modules_list), modules_list=modules_list)

@app.route('/retrieveModuleClasses/<module_code>/<class_search>', methods=['GET', 'POST'])
@login_check
def retrieve_module_classes_searches(module_code, class_search):
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()
    classes_dict = {}
    db = shelve.open('class.db', 'r')
    classes_dict = db["Classes"]
    db.close()

    classes_list = []
    for i in classes_dict.values():
        if str(i.get_class_id()) + "." + i.get_class_name() in modules_dict[module_code].get_classes_assigned():
            classes_list.append(i)

    classes_assigned_list = []
    for value in classes_list:
        if class_search.upper() in value.get_class_name().upper() or class_search in str(value.get_class_id()) or class_search in str(value.get_implementation_date()) or class_search.upper() in value.get_class_description().upper():
            classes_assigned_list.append(value)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        class_search = search_form.search_bar.data

        return redirect(url_for('retrieve_module_classes_searches', module_code=module_code, class_search=class_search))
    return render_template('retrieveModuleClasses.html', form=search_form, count=len(classes_assigned_list), classes_assigned_list=classes_assigned_list)

@app.route('/retrieveModuleStudent/<module_search>', methods=['GET', 'POST'])
@login_check
def retrieve_module_student_searches(module_search):
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()
    classes_dict = {}
    db = shelve.open('class.db', 'r')
    classes_dict = db['Classes']
    db.close()
    students_dict = {}
    db = shelve.open('Students.db', 'r')
    students_dict = db['Students']
    db.close()

    student_id = students_dict[session["account"]].get_adminNo() + "." + students_dict[session["account"]].get_name()

    class_assigned = []
    for values in classes_dict.values():
        if student_id in values.get_student_names():
            class_assigned = str(values.get_class_id()) + "." + values.get_class_name()

    modules_avaliable_list = []
    for key in modules_dict.keys():
        if date.today() >= modules_dict[key].get_implementation_date() and class_assigned in modules_dict[key].get_classes_assigned():
            module = modules_dict.get(key)
            modules_avaliable_list.append(module)

    modules_list = []
    for value in modules_avaliable_list:
        if module_search.upper() in value.get_module_name().upper() or module_search.upper() in value.get_module_code() or module_search.upper() in value.get_module_description().upper():
            modules_list.append(value)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        module_search = search_form.search_bar.data

        return redirect(url_for('retrieve_module_student_searches', module_search=module_search))
    return render_template('retrieveModuleStudent.html', form=search_form, count=len(modules_list), modules_list=modules_list)

@app.route('/retrieveModuleTeacher/<module_search>', methods=['GET', 'POST'])
@login_check
def retrieve_module_teacher_searches(module_search):
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()
    teachers_dict = {}
    db = shelve.open('Teachers.db','r')
    teachers_dict = db["Teachers"]
    db.close()

    modules_avaliable_list = []
    for key in modules_dict.keys():
        if date.today() >= modules_dict[key].get_implementation_date() and modules_dict[key].get_module_code() + " " + modules_dict[key].get_module_name() == teachers_dict[session['account']].get_modules():
            module = modules_dict.get(key)
            modules_avaliable_list.append(module)

    modules_list = []
    for value in modules_avaliable_list:
        if module_search.upper() in value.get_module_name().upper() or module_search.upper() in value.get_module_code() or module_search.upper() in value.get_module_description().upper():
            modules_list.append(value)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        module_search = search_form.search_bar.data

        return redirect(url_for('retrieve_module_teacher_searches', module_search=module_search))
    return render_template('retrieveModuleTeacher.html', form=search_form, count=len(modules_list), modules_list=modules_list)
#
@app.route('/retrieveClassesTeacher/<module_code>/<class_search>', methods=['GET', 'POST'])
@login_check
def retrieve_teacher_module_classes_searches(module_code, class_search):
    modules_dict = {}
    db = shelve.open('module.db', 'r')
    modules_dict = db['Modules']
    db.close()
    classes_dict = {}
    db = shelve.open('class.db', 'r')
    classes_dict = db['Classes']
    db.close()

    module = modules_dict[module_code]

    classes_avaliable = []
    for j in classes_dict.values():
       if str(j.get_class_id()) + "." + j.get_class_name() in modules_dict[module_code].get_classes_assigned():
           classes_avaliable.append(j)

    classes_list = []
    for value in classes_avaliable:
        if class_search.upper() in value.get_class_name().upper() or class_search in str(value.get_class_id()) or class_search in str(value.get_implementation_date()) or class_search.upper() in value.get_class_description().upper():
            classes_list.append(value)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        class_search = search_form.search_bar.data

        return redirect(url_for('retrieve_teacher_module_classes_searches', module_code=module_code, class_search=class_search))
    return render_template('moduleClassesTeachers.html', form=search_form, count=len(classes_list), classes_list=classes_list, module=module)

@app.route('/retrieveClasses/<class_search>', methods=['GET', 'POST'])
@login_check
def retrieve_class_searches(class_search):
    classes_dict = {}
    db = shelve.open('class.db', 'r')
    classes_dict = db['Classes']
    db.close()

    classes_list = []
    for key in classes_dict.keys():
        if class_search in str(classes_dict[key].get_class_id()) or class_search.upper() in classes_dict[key].get_class_name().upper() or class_search in str(classes_dict[key].get_implementation_date()) or class_search.upper() in classes_dict[key].get_class_description().upper():
            classs = classes_dict.get(key)
            classes_list.append(classs)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        class_search = search_form.search_bar.data

        return redirect(url_for('retrieve_class_searches', class_search=class_search))
    return render_template('retrieveClasses.html', form=search_form, count=len(classes_list), classes_list=classes_list)

@app.route('/retrieveClassesInfo/<class_id>/<person_search>', methods=['GET', 'POST'])
@login_check
def retrieve_classes_information_searches(class_id, person_search):
    classes_dict = {}
    db = shelve.open('class.db', 'r')
    classes_dict = db['Classes']
    db.close()
    teachers_dict = {}
    db = shelve.open('Teachers.db', 'r')
    teachers_dict = db['Teachers']
    db.close()
    students_dict = {}
    db = shelve.open('Students.db', 'r')
    students_dict = db['Students']
    db.close()

    teachers_avaliable_list = []
    for k in teachers_dict.values():
        if k.get_adminNo() + "." + k.get_name() in classes_dict[int(class_id)].get_form_teachers():
            teachers_avaliable_list.append(k)

    students_avaliable_list = []
    for l in students_dict.values():
        if l.get_adminNo() + "." + l.get_name() in classes_dict[int(class_id)].get_student_names():
            students_avaliable_list.append(l)

    teachers_list = []
    for value in teachers_avaliable_list:
        if person_search.upper() in value.get_name().upper() or person_search.upper() in value.get_adminNo().upper() or person_search.upper() in value.get_gender().upper() or person_search.upper() in value.get_email().upper():
            teachers_list.append(value)

    students_list = []
    for value in students_avaliable_list:
        if person_search.upper() in value.get_name().upper() or person_search.upper() in value.get_adminNo().upper() or person_search.upper() in value.get_gender().upper() or person_search.upper() in value.get_email().upper():
            students_list.append(value)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        person_search = search_form.search_bar.data

        return redirect(url_for('retrieve_classes_information_searches', class_id=class_id, person_search=person_search))
    return render_template('retrieveClassesInformation.html', form=search_form, count=len(teachers_list) + len(students_list), teachers_list=teachers_list, students_list=students_list)

@app.route('/updateModule/<id>/', methods=['GET', 'POST'])
@login_check
def update_module(id):
    update_module_form = UpdateModuleForm(request.form)
    db = shelve.open("class.db", 'c')
    classes_dict = {}
    try:
        classes_dict = db["Classes"]
    except:
        db["Classes"] = classes_dict

    class_assigned_choices = ['']
    for i in list(classes_dict.keys()):
        class_assigned_choices.append(str(classes_dict[i].get_class_id()) + '.' + classes_dict[i].get_class_name())
    db.close()
    update_module_form.classes_assigned.choices = class_assigned_choices
    update_module_form.classes_assigned2.choices = class_assigned_choices
    update_module_form.classes_assigned3.choices = class_assigned_choices
    update_module_form.classes_assigned4.choices = class_assigned_choices
    update_module_form.classes_assigned5.choices = class_assigned_choices
    update_module_form.classes_assigned6.choices = class_assigned_choices
    update_module_form.classes_assigned7.choices = class_assigned_choices
    update_module_form.classes_assigned8.choices = class_assigned_choices
    if request.method == 'POST' and update_module_form.validate():
        modules_dict = {}
        db = shelve.open('module.db', 'w')
        modules_dict = db['Modules']
        filename = ''

        file = request.files['module_image']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save("static/img/" + filename)

        module = modules_dict.get(id)

        if filename == '':
            module.set_module_image(module.get_module_image())
        else:
            module.set_module_image(filename)

        classes_assigned = []
        classes_assigned.append(update_module_form.classes_assigned.data)
        if update_module_form.classes_assigned2.data != '' and update_module_form.classes_assigned2.data not in classes_assigned:
            classes_assigned.append(update_module_form.classes_assigned2.data)
        if update_module_form.classes_assigned3.data != '' and update_module_form.classes_assigned3.data not in classes_assigned:
            classes_assigned.append(update_module_form.classes_assigned3.data)
        if update_module_form.classes_assigned4.data != '' and update_module_form.classes_assigned4.data not in classes_assigned:
            classes_assigned.append(update_module_form.classes_assigned4.data)
        if update_module_form.classes_assigned5.data != '' and update_module_form.classes_assigned5.data not in classes_assigned:
            classes_assigned.append(update_module_form.classes_assigned5.data)
        if update_module_form.classes_assigned6.data != '' and update_module_form.classes_assigned6.data not in classes_assigned:
            classes_assigned.append(update_module_form.classes_assigned6.data)
        if update_module_form.classes_assigned7.data != '' and update_module_form.classes_assigned7.data not in classes_assigned:
            classes_assigned.append(update_module_form.classes_assigned7.data)
        if update_module_form.classes_assigned8.data != '' and update_module_form.classes_assigned8.data not in classes_assigned:
            classes_assigned.append(update_module_form.classes_assigned8.data)

        module.set_module_name(update_module_form.module_name.data)
        module.set_implementation_date(update_module_form.implementation_date.data)
        module.set_module_description(update_module_form.module_description.data)
        module.set_classes_assigned(classes_assigned)

        db['Modules'] = modules_dict
        db.close()

        session['module_updated'] = module.get_module_code() + " " + module.get_module_name()

        return redirect(url_for('retrieve_modules'))
    else:
        global module_name
        global module_id
        modules_dict = {}
        db = shelve.open('module.db', 'c')
        modules_dict = db['Modules']
        if module_name != '' and module_id in modules_dict:
            if modules_dict[module_id].get_module_name() == '':
                modules_dict[module_id].set_module_name(module_name)
                db['Modules'] = modules_dict
        db.close()

        module = modules_dict.get(id)
        update_module_form.module_code = module.get_module_code()
        update_module_form.previous_image = module.get_module_image()
        update_module_form.module_first_name = module.get_module_name()
        update_module_form.module_name.data = module.get_module_name()
        update_module_form.implementation_date.data = module.get_implementation_date()
        update_module_form.module_description.data = module.get_module_description()
        update_module_form.classes_assigned.data = module.get_classes_assigned()[0]
        if len(module.get_classes_assigned()) > 1:
            update_module_form.classes_assigned2.data = module.get_classes_assigned()[1]
        if len(module.get_classes_assigned()) > 2:
            update_module_form.classes_assigned3.data = module.get_classes_assigned()[2]
        if len(module.get_classes_assigned()) > 3:
            update_module_form.classes_assigned4.data = module.get_classes_assigned()[3]
        if len(module.get_classes_assigned()) > 4:
            update_module_form.classes_assigned5.data = module.get_classes_assigned()[4]
        if len(module.get_classes_assigned()) > 5:
            update_module_form.classes_assigned6.data = module.get_classes_assigned()[5]
        if len(module.get_classes_assigned()) > 6:
            update_module_form.classes_assigned7.data = module.get_classes_assigned()[6]
        if len(module.get_classes_assigned()) > 7:
            update_module_form.classes_assigned8.data = module.get_classes_assigned()[7]
        modules_dict = {}
        db = shelve.open("module.db", "c")
        try:
            modules_dict = db["Modules"]
        except:
            db["Modules"] = modules_dict

        module_name = modules_dict[id].get_module_name()
        module_id = id

        modules_dict[id].set_module_name('')
        db["Modules"] = modules_dict
        return render_template('updateModule.html', form=update_module_form)

@app.route('/updateClass/<int:id>/', methods=['GET', 'POST'])
@login_check
def update_Class(id):
    update_class_form = UpdateClassForm(request.form)
    db = shelve.open("Students.db", 'c')
    students_dict = {}
    try:
        students_dict = db["Students"]
    except:
        db["Students"] = students_dict
    db.close()

    db = shelve.open("Teachers.db", 'c')
    teachers_dict = {}
    try:
        teachers_dict = db["Teachers"]
    except:
        db["Teachers"] = teachers_dict
    db.close()

    students_choices = ['']
    for i in list(students_dict.keys()):
        students_choices.append(str(students_dict[i].get_adminNo()) + '.' + students_dict[i].get_name())
    update_class_form.student_names.choices = students_choices
    update_class_form.student_names2.choices = students_choices
    update_class_form.student_names3.choices = students_choices
    update_class_form.student_names4.choices = students_choices
    update_class_form.student_names5.choices = students_choices
    update_class_form.student_names6.choices = students_choices
    update_class_form.student_names7.choices = students_choices
    update_class_form.student_names8.choices = students_choices
    update_class_form.student_names9.choices = students_choices
    update_class_form.student_names10.choices = students_choices
    update_class_form.student_names11.choices = students_choices
    update_class_form.student_names12.choices = students_choices
    update_class_form.student_names13.choices = students_choices
    update_class_form.student_names14.choices = students_choices
    update_class_form.student_names15.choices = students_choices
    update_class_form.student_names16.choices = students_choices
    update_class_form.student_names17.choices = students_choices
    update_class_form.student_names18.choices = students_choices
    update_class_form.student_names19.choices = students_choices
    update_class_form.student_names20.choices = students_choices
    update_class_form.student_names21.choices = students_choices
    update_class_form.student_names22.choices = students_choices
    update_class_form.student_names23.choices = students_choices
    update_class_form.student_names24.choices = students_choices
    update_class_form.student_names25.choices = students_choices
    update_class_form.student_names26.choices = students_choices
    update_class_form.student_names27.choices = students_choices
    update_class_form.student_names28.choices = students_choices
    update_class_form.student_names29.choices = students_choices
    update_class_form.student_names30.choices = students_choices
    update_class_form.student_names31.choices = students_choices
    update_class_form.student_names32.choices = students_choices
    update_class_form.student_names33.choices = students_choices
    update_class_form.student_names34.choices = students_choices
    update_class_form.student_names35.choices = students_choices
    update_class_form.student_names36.choices = students_choices
    update_class_form.student_names37.choices = students_choices
    update_class_form.student_names38.choices = students_choices
    update_class_form.student_names39.choices = students_choices
    update_class_form.student_names40.choices = students_choices

    teacher_choices = ['']
    for i in list(teachers_dict.keys()):
        teacher_choices.append(str(teachers_dict[i].get_adminNo()) + '.' + teachers_dict[i].get_name())
    update_class_form.form_teachers.choices = teacher_choices
    update_class_form.form_teachers2.choices = teacher_choices
    update_class_form.form_teachers3.choices = teacher_choices
    update_class_form.form_teachers4.choices = teacher_choices

    if request.method == 'POST' and update_class_form.validate():
        classes_dict = {}
        db = shelve.open('class.db', 'w')
        classes_dict = db['Classes']

        student_names = []
        student_names.append(update_class_form.student_names.data)
        if update_class_form.student_names2.data != '' and update_class_form.student_names2.data not in student_names:
            student_names.append(update_class_form.student_names2.data)
        if update_class_form.student_names3.data != '' and update_class_form.student_names3.data not in student_names:
            student_names.append(update_class_form.student_names3.data)
        if update_class_form.student_names4.data != '' and update_class_form.student_names4.data not in student_names:
            student_names.append(update_class_form.student_names4.data)
        if update_class_form.student_names5.data != '' and update_class_form.student_names5.data not in student_names:
            student_names.append(update_class_form.student_names5.data)
        if update_class_form.student_names6.data != '' and update_class_form.student_names6.data not in student_names:
            student_names.append(update_class_form.student_names6.data)
        if update_class_form.student_names7.data != '' and update_class_form.student_names7.data not in student_names:
            student_names.append(update_class_form.student_names7.data)
        if update_class_form.student_names8.data != '' and update_class_form.student_names8.data not in student_names:
            student_names.append(update_class_form.student_names8.data)
        if update_class_form.student_names9.data != '' and update_class_form.student_names9.data not in student_names:
            student_names.append(update_class_form.student_names9.data)
        if update_class_form.student_names10.data != '' and update_class_form.student_names10.data not in student_names:
            student_names.append(update_class_form.student_names10.data)
        if update_class_form.student_names11.data != '' and update_class_form.student_names11.data not in student_names:
            student_names.append(update_class_form.student_names11.data)
        if update_class_form.student_names12.data != '' and update_class_form.student_names12.data not in student_names:
            student_names.append(update_class_form.student_names12.data)
        if update_class_form.student_names13.data != '' and update_class_form.student_names13.data not in student_names:
            student_names.append(update_class_form.student_names13.data)
        if update_class_form.student_names14.data != '' and update_class_form.student_names14.data not in student_names:
            student_names.append(update_class_form.student_names14.data)
        if update_class_form.student_names15.data != '' and update_class_form.student_names15.data not in student_names:
            student_names.append(update_class_form.student_names15.data)
        if update_class_form.student_names16.data != '' and update_class_form.student_names16.data not in student_names:
            student_names.append(update_class_form.student_names16.data)
        if update_class_form.student_names17.data != '' and update_class_form.student_names17.data not in student_names:
            student_names.append(update_class_form.student_names17.data)
        if update_class_form.student_names18.data != '' and update_class_form.student_names18.data not in student_names:
            student_names.append(update_class_form.student_names18.data)
        if update_class_form.student_names19.data != '' and update_class_form.student_names19.data not in student_names:
            student_names.append(update_class_form.student_names19.data)
        if update_class_form.student_names20.data != '' and update_class_form.student_names20.data not in student_names:
            student_names.append(update_class_form.student_names20.data)
        if update_class_form.student_names21.data != '' and update_class_form.student_names21.data not in student_names:
            student_names.append(update_class_form.student_names21.data)
        if update_class_form.student_names22.data != '' and update_class_form.student_names22.data not in student_names:
            student_names.append(update_class_form.student_names22.data)
        if update_class_form.student_names23.data != '' and update_class_form.student_names23.data not in student_names:
            student_names.append(update_class_form.student_names23.data)
        if update_class_form.student_names24.data != '' and update_class_form.student_names24.data not in student_names:
            student_names.append(update_class_form.student_names24.data)
        if update_class_form.student_names25.data != '' and update_class_form.student_names25.data not in student_names:
            student_names.append(update_class_form.student_names25.data)
        if update_class_form.student_names26.data != '' and update_class_form.student_names26.data not in student_names:
            student_names.append(update_class_form.student_names26.data)
        if update_class_form.student_names27.data != '' and update_class_form.student_names27.data not in student_names:
            student_names.append(update_class_form.student_names27.data)
        if update_class_form.student_names28.data != '' and update_class_form.student_names28.data not in student_names:
            student_names.append(update_class_form.student_names28.data)
        if update_class_form.student_names29.data != '' and update_class_form.student_names29.data not in student_names:
            student_names.append(update_class_form.student_names29.data)
        if update_class_form.student_names30.data != '' and update_class_form.student_names30.data not in student_names:
            student_names.append(update_class_form.student_names30.data)
        if update_class_form.student_names31.data != '' and update_class_form.student_names31.data not in student_names:
            student_names.append(update_class_form.student_names31.data)
        if update_class_form.student_names32.data != '' and update_class_form.student_names32.data not in student_names:
            student_names.append(update_class_form.student_names32.data)
        if update_class_form.student_names33.data != '' and update_class_form.student_names33.data not in student_names:
            student_names.append(update_class_form.student_names33.data)
        if update_class_form.student_names34.data != '' and update_class_form.student_names34.data not in student_names:
            student_names.append(update_class_form.student_names34.data)
        if update_class_form.student_names35.data != '' and update_class_form.student_names35.data not in student_names:
            student_names.append(update_class_form.student_names35.data)
        if update_class_form.student_names36.data != '' and update_class_form.student_names36.data not in student_names:
            student_names.append(update_class_form.student_names36.data)
        if update_class_form.student_names37.data != '' and update_class_form.student_names37.data not in student_names:
            student_names.append(update_class_form.student_names37.data)
        if update_class_form.student_names38.data != '' and update_class_form.student_names38.data not in student_names:
            student_names.append(update_class_form.student_names38.data)
        if update_class_form.student_names39.data != '' and update_class_form.student_names39.data not in student_names:
            student_names.append(update_class_form.student_names39.data)
        if update_class_form.student_names40.data != '' and update_class_form.student_names40.data not in student_names:
            student_names.append(update_class_form.student_names40.data)

        form_teachers = []
        form_teachers.append(update_class_form.form_teachers.data)
        if update_class_form.form_teachers2.data != '' and update_class_form.form_teachers2.data not in form_teachers:
            form_teachers.append(update_class_form.form_teachers2.data)
        if update_class_form.form_teachers3.data != '' and update_class_form.form_teachers3.data not in form_teachers:
            form_teachers.append(update_class_form.form_teachers3.data)
        if update_class_form.form_teachers4.data != '' and update_class_form.form_teachers4.data not in form_teachers:
            form_teachers.append(update_class_form.form_teachers4.data)

        classs = classes_dict.get(id)
        classs.set_implementation_date(update_class_form.implementation_date.data)
        classs.set_student_names(student_names)
        classs.set_form_teachers(form_teachers)
        classs.set_class_description(update_class_form.class_description.data)

        db['Classes'] = classes_dict
        db.close()

        session['class_updated'] = str(classs.get_class_id()) + "." + classs.get_class_name()

        return redirect(url_for('retrieve_classes'))
    else:
        global student_namess
        global teacher_names
        global class_id
        classes_dict = {}
        db = shelve.open('class.db', 'c')
        classes_dict = db['Classes']
        db.close()
        if student_namess != [] and class_id in classes_dict.keys():
            if classes_dict[class_id].get_student_names() == []:
                db = shelve.open('class.db', 'c')
                classes_dict = db['Classes']
                classes_dict[class_id].set_student_names(student_namess)
                db["Classes"] = classes_dict
                db.close()
        if teacher_names != [] and class_id in classes_dict.keys():
            if classes_dict[class_id].get_form_teachers() == []:
                db = shelve.open('class.db', 'c')
                classes_dict = db['Classes']
                classes_dict[class_id].set_form_teachers(teacher_names)
                db["Classes"] = classes_dict
                db.close()


        classs = classes_dict.get(id)
        update_class_form.class_name = classs.get_class_name()
        update_class_form.implementation_date.data = classs.get_implementation_date()
        update_class_form.student_names.data = classs.get_student_names()[0]
        if len(classs.get_student_names()) > 1:
            update_class_form.student_names2.data = classs.get_student_names()[1]
        if len(classs.get_student_names()) > 2:
            update_class_form.student_names3.data = classs.get_student_names()[2]
        if len(classs.get_student_names()) > 3:
            update_class_form.student_names4.data = classs.get_student_names()[3]
        if len(classs.get_student_names()) > 4:
            update_class_form.student_names5.data = classs.get_student_names()[4]
        if len(classs.get_student_names()) > 5:
            update_class_form.student_names6.data = classs.get_student_names()[5]
        if len(classs.get_student_names()) > 6:
            update_class_form.student_names7.data = classs.get_student_names()[6]
        if len(classs.get_student_names()) > 7:
            update_class_form.student_names8.data = classs.get_student_names()[7]
        if len(classs.get_student_names()) > 8:
            update_class_form.student_names9.data = classs.get_student_names()[8]
        if len(classs.get_student_names()) > 9:
            update_class_form.student_names10.data = classs.get_student_names()[9]
        if len(classs.get_student_names()) > 10:
            update_class_form.student_names11.data = classs.get_student_names()[10]
        if len(classs.get_student_names()) > 11:
            update_class_form.student_names12.data = classs.get_student_names()[11]
        if len(classs.get_student_names()) > 12:
            update_class_form.student_names13.data = classs.get_student_names()[12]
        if len(classs.get_student_names()) > 13:
            update_class_form.student_names14.data = classs.get_student_names()[13]
        if len(classs.get_student_names()) > 14:
            update_class_form.student_names15.data = classs.get_student_names()[14]
        if len(classs.get_student_names()) > 15:
            update_class_form.student_names16.data = classs.get_student_names()[15]
        if len(classs.get_student_names()) > 16:
            update_class_form.student_names17.data = classs.get_student_names()[16]
        if len(classs.get_student_names()) > 17:
            update_class_form.student_names18.data = classs.get_student_names()[17]
        if len(classs.get_student_names()) > 18:
            update_class_form.student_names19.data = classs.get_student_names()[18]
        if len(classs.get_student_names()) > 19:
            update_class_form.student_names20.data = classs.get_student_names()[19]
        if len(classs.get_student_names()) > 20:
            update_class_form.student_names21.data = classs.get_student_names()[20]
        if len(classs.get_student_names()) > 21:
            update_class_form.student_names22.data = classs.get_student_names()[21]
        if len(classs.get_student_names()) > 22:
            update_class_form.student_names23.data = classs.get_student_names()[22]
        if len(classs.get_student_names()) > 23:
            update_class_form.student_names24.data = classs.get_student_names()[23]
        if len(classs.get_student_names()) > 24:
            update_class_form.student_names25.data = classs.get_student_names()[24]
        if len(classs.get_student_names()) > 25:
            update_class_form.student_names26.data = classs.get_student_names()[25]
        if len(classs.get_student_names()) > 26:
            update_class_form.student_names27.data = classs.get_student_names()[26]
        if len(classs.get_student_names()) > 27:
            update_class_form.student_names28.data = classs.get_student_names()[27]
        if len(classs.get_student_names()) > 28:
            update_class_form.student_names29.data = classs.get_student_names()[28]
        if len(classs.get_student_names()) > 29:
            update_class_form.student_names30.data = classs.get_student_names()[29]
        if len(classs.get_student_names()) > 30:
            update_class_form.student_names31.data = classs.get_student_names()[30]
        if len(classs.get_student_names()) > 31:
            update_class_form.student_names32.data = classs.get_student_names()[31]
        if len(classs.get_student_names()) > 32:
            update_class_form.student_names33.data = classs.get_student_names()[32]
        if len(classs.get_student_names()) > 33:
            update_class_form.student_names34.data = classs.get_student_names()[33]
        if len(classs.get_student_names()) > 34:
            update_class_form.student_names35.data = classs.get_student_names()[34]
        if len(classs.get_student_names()) > 35:
            update_class_form.student_names36.data = classs.get_student_names()[35]
        if len(classs.get_student_names()) > 36:
            update_class_form.student_names37.data = classs.get_student_names()[36]
        if len(classs.get_student_names()) > 37:
            update_class_form.student_names38.data = classs.get_student_names()[37]
        if len(classs.get_student_names()) > 38:
            update_class_form.student_names39.data = classs.get_student_names()[38]
        if len(classs.get_student_names()) > 39:
            update_class_form.student_names40.data = classs.get_student_names()[39]

        update_class_form.form_teachers.data = classs.get_form_teachers()[0]
        if len(classs.get_form_teachers()) > 1:
            update_class_form.form_teachers2.data = classs.get_form_teachers()[1]
        if len(classs.get_form_teachers()) > 2:
            update_class_form.form_teachers3.data = classs.get_form_teachers()[2]
        if len(classs.get_form_teachers()) > 3:
            update_class_form.form_teachers4.data = classs.get_form_teachers()[3]

        update_class_form.class_description.data = classs.get_class_description()


        classes_dict = {}
        db = shelve.open("class.db", "c")
        try:
            classes_dict = db["Classes"]
        except:
            db["Classes"] = classes_dict

        student_namess = classes_dict[id].get_student_names()
        teacher_names = classes_dict[id].get_form_teachers()
        class_id = classs.get_class_id()

        classes_dict[id].set_student_names([])
        classes_dict[id].set_form_teachers([])
        db["Classes"] = classes_dict
        return render_template('updateClass.html', form=update_class_form)

@app.route('/deleteModule/<id>', methods=['POST'])
@login_check
def delete_module(id):
    modules_dict = {}
    db = shelve.open('module.db', 'w')
    modules_dict = db['Modules']

    module = modules_dict.pop(id)

    db['Modules'] = modules_dict
    db.close()

    session["module_deleted"] = module.get_module_code() + " " + module.get_module_name()

    return redirect(url_for('retrieve_modules'))

@app.route('/deleteClass/<int:id>', methods=['POST'])
@login_check
def delete_class(id):
    classes_dict = {}
    db = shelve.open('class.db', 'w')
    classes_dict = db['Classes']

    classs = classes_dict.pop(id)

    db['Classes'] = classes_dict
    db.close()

    session["class_deleted"] = str(classs.get_class_id()) + "." + classs.get_class_name()

    return redirect(url_for('retrieve_classes'))

# ==============================Eshton's work============================================

# Create Submission Based Off Assignment

@app.route('/createSubmission/<int:assignment_id>', methods=['GET', 'POST'])
@login_check
def create_submission_link(assignment_id):
    create_submission_form = CreateSubmissionForm(request.form)
    # Retrieve the assignments from the "Assignment" database
    assignment_dict = {}
    db = shelve.open('assignment.db', 'c')
    try:
        assignment_dict = db['Assignments']
    except:
        print("Error in retrieving Assignments from assignment.db.")

    # Create the select pairs using the retrieved assignments
    for assignment in assignment_dict.values():
        if assignment_id == assignment.get_FileID():
            moduleCode = assignment.get_module_code()
            create_submission_form.assignment.data = assignment.get_AssignmentName()
            fileID = assignment.get_FileID()
            student = session["account"]

    if request.method == 'POST' and create_submission_form.validate():
        submissions_dict = {}
        db = shelve.open('submission.db', 'c')

        try:
            submissions_dict = db['Submissions']
        except:
            print("Error in retrieving Submissions from submission.db.")

        file = request.files['file']

        if file.filename == '':
            redirect(url_for('create_submission'))

        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        try:
            submissions_dict = db['Submissions']
            submission_id = 1
            while True:
                if submission_id in submissions_dict.keys():
                    submission_id += 1

                else:
                    break

        except:
            print("Error in retrieving Submissions from submission.db")
            submission_id = 1

        submission = Submission.Submission(student,
                                           submission_id,
                                           fileID,
                                           create_submission_form.assignment.data,
                                           moduleCode,
                                           create_submission_form.submission_name.data,
                                           create_submission_form.details.data,
                                           create_submission_form.answers.data,
                                           filename)
        
        submissions_dict[submission.get_submission_id()] = submission
        db['Submissions'] = submissions_dict

        return redirect(url_for('retrieve_submissions'))
    return render_template('createSubmission.html', form = create_submission_form)

# Student Retrieve Submissions

@app.route('/retrieveSubmissions', methods = ['GET','POST'])
@login_check
def retrieve_submissions():
    submissions_dict = {}
    db = shelve.open('submission.db', 'c')
    try:
        submissions_dict = db['Submissions']
    except:
        submissions_dict = {}
    finally:
        db.close()

    submissions_list = []
    for key in submissions_dict:
        submission = submissions_dict.get(key)
        if session["account"] == submission.get_student_id():
            submissions_list.append(submission)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        submission_code = search_form.search_bar.data

        return redirect(url_for('retrieve_submission_searches', submission_search=submission_code))
    return render_template('retrieveSubmissions.html', count=len(submissions_list), submissions_list=submissions_list, form=search_form)

# Student's Search Bar

@app.route('/retrieveSubmissions/<submission_search>', methods=['GET', 'POST'])
@login_check
def retrieve_submission_searches(submission_search):
    submission_dict = {}
    db = shelve.open('submission.db', 'r')
    submission_dict = db['Submissions']
    db.close()

    submissions_list = []
    for key in submission_dict.keys():
        if str(submission_search) in str(submission_dict[key].get_submission_id()) or str(
                submission_search).upper() in str(submission_dict[key].get_submission_name()).upper() or str(
                submission_search).upper() in str(submission_dict[key].get_assignment_name()).upper():
            submissions = submission_dict.get(key)
            if session["account"] == submissions.get_student_id():
                submissions_list.append(submissions)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        submission_code = search_form.search_bar.data

        return redirect(url_for('retrieve_submission_searches', submission_search=submission_code))
    return render_template('retrieveSubmissions.html', form=search_form, count=len(submissions_list),
                           submissions_list=submissions_list)

# Student View Submissions From Assignment View

@app.route('/retrieveIndividualSubmissions/<int:assignment_id>')
@login_check
def retrieve_submissions_with_id(assignment_id):
    assignments_dict = {}
    db = shelve.open('assignment.db', 'c')
    try:
        assignments_dict = db['Assignments']
    except:
        assignments_dict = {}
    finally:
        db.close()

    submissions_dict = {}
    db = shelve.open('submission.db', 'c')
    try:
        submissions_dict = db['Submissions']
    except:
        submissions_dict = {}
    finally:
        db.close()

    submissions_list = []
    if assignment_id in assignments_dict:
        for key in submissions_dict:
            submission = submissions_dict.get(key)
            if session["account"] == submission.get_student_id():
                if submission.get_assignment_id() == assignment_id:
                    submissions_list.append(submission)


    return render_template('retrieveIndividualSubmissions.html', count=len(submissions_list), submissions_list=submissions_list)

# Student View Submissions From Assignment View

@app.route('/studentAdvancedSubmissionView/<int:submission_id>')
@login_check
def student_retrieve_submission_with_id(submission_id):
    submissions_dict = {}
    db = shelve.open('submission.db', 'c')
    try:
        submissions_dict = db['Submissions']
    except:
        submissions_dict = {}
    finally:
        db.close()

    submission = submissions_dict.get(submission_id)


    return render_template('studentAdvancedSubmissionView.html', submission = submission)

# Teacher View Submissions From Assignment

@app.route('/teacherRetrieveIndividualSubmissions/<int:assignment_id>')
@login_check
def teacher_retrieve_submissions_with_id(assignment_id):
    assignments_dict = {}
    db = shelve.open('assignment.db', 'c')
    try:
        assignments_dict = db['Assignments']
    except:
        assignments_dict = {}
    finally:
        db.close()

    submissions_dict = {}
    db = shelve.open('submission.db', 'c')
    try:
        submissions_dict = db['Submissions']
    except:
        submissions_dict = {}
    finally:
        db.close()

    submissions_list = []
    grades_list = []
    if assignment_id in assignments_dict:
        for key in submissions_dict:
            submission = submissions_dict.get(key)
            if submission.get_assignment_id() == assignment_id:
                submissions_list.append(submission)
                grades_list.append(submission.get_grades())
    
    labels = ['A', 'B', 'C', 'D', 'E', 'S', 'Ungraded' ,'U']
    colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA", "#ABCDEF", "#DDDDDD", "#ABCABC"]
    gradesCount = [0,0,0,0,0,0,0,0]
    for grade in grades_list:
        try:
            if int(grade) >= 70:
                temp = gradesCount[0]
                temp += 1
                gradesCount[0] = temp
            elif int(grade) >= 60:
                temp = gradesCount[1]
                temp += 1
                gradesCount[1] = temp
            elif int(grade) >= 55:
                temp = gradesCount[2]
                temp += 1
                gradesCount[2] = temp
            elif int(grade) >= 50:
                temp = gradesCount[3]
                temp += 1
                gradesCount[3] = temp
            elif int(grade) >= 45:
                temp = gradesCount[4]
                temp += 1
                gradesCount[4] = temp
            elif int(grade) >= 40:
                temp = gradesCount[5]
                temp += 1
                gradesCount[5] = temp                
            else:
                temp = gradesCount[7]
                temp += 1
                gradesCount[7] = temp
        except:
            temp = gradesCount[6]
            temp += 1
            gradesCount[6] = temp

    pie_labels = labels
    pie_values = gradesCount
    return render_template('teacherRetrieveIndividualSubmissions.html', count=len(submissions_list), submissions_list=submissions_list, max=17000, set=zip(gradesCount, labels, colors))

# Teacher View Submissions From Assignment View

@app.route('/teacherAdvancedSubmissionView/<int:submission_id>')
@login_check
def teacher_retrieve_submission_with_id(submission_id):
    submissions_dict = {}
    db = shelve.open('submission.db', 'c')
    try:
        submissions_dict = db['Submissions']
    except:
        submissions_dict = {}
    finally:
        db.close()

    submission = submissions_dict.get(submission_id)


    return render_template('teacherAdvancedSubmissionView.html', submission = submission)

# Teacher's Search Bar

@app.route('/teacherRetrieveSubmissions/<submission_search>', methods=['GET', 'POST'])
@login_check
def retrieve_teacher_submission_searches(submission_search):
    submission_dict = {}
    db = shelve.open('submission.db', 'c')
    submission_dict = db['Submissions']
    db.close()

    submissions_list = []
    for key in submission_dict.keys():
        if str(submission_search) in str(submission_dict[key].get_submission_id()) or str(
                submission_search).upper() in str(submission_dict[key].get_submission_name()).upper() or str(
                submission_search).upper() in str(submission_dict[key].get_assignment_name()).upper():
            submissions = submission_dict.get(key)
            submissions_list.append(submissions)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        submission_code = search_form.search_bar.data

        return redirect(url_for('retrieve_teacher_submission_searches', submission_search=submission_code))
    return render_template('teacherRetrieveSubmissions.html', form=search_form, count=len(submissions_list),
                           submissions_list=submissions_list)


# Teacher Retrieve Submissions View

@app.route('/teacherRetrieveSubmissions', methods=['GET', 'POST'])
@login_check
def teacher_retrieve_submissions():
    submissions_dict = {}
    db = shelve.open('submission.db', 'c')
    try:
        submissions_dict = db['Submissions']
    except:
        submissions_dict = {}

    db.close()

    teacher_dict = {}
    db = shelve.open('Teachers.db')
    teacher_dict = db['Teachers']
    db.close()
    moduleName = teacher_dict.get(session['account']).get_modules()


    modules_dict = {}
    db = shelve.open('module.db')
    modules_dict = db['Modules']
    db.close()
    for module in modules_dict:
        if modules_dict.get(module).get_module_name() == moduleName:
            modules = modules_dict.get(module)

    submissions_list = []
    for key in submissions_dict:
        if submissions_dict.get(key).get_module_code() == modules.get_module_name():
            submission = submissions_dict.get(key)
            submissions_list.append(submission)

    search_form = Search(request.form)
    if request.method == 'POST' and search_form.validate() and search_form.search_bar.data != '':
        submission_code = search_form.search_bar.data

        return redirect(url_for('retrieve_teacher_submission_searches', submission_search=submission_code))
    return render_template("teacherRetrieveSubmissions.html", form=search_form, count=len(submissions_list), submissions_list=submissions_list)

# Update Submission

@app.route('/updateSubmission/<int:submission_id>/', methods=['GET', 'POST'])
@login_check
def update_submission(submission_id):
    update_submission_form = UpdateSubmissionForm(request.form)
    if request.method == 'POST' and update_submission_form.validate():
        submissions_dict = {}
        db = shelve.open('submission.db', 'w')
        submissions_dict = db['Submissions']

        submission = submissions_dict.get(submission_id)
        submission.set_details(update_submission_form.details.data)

        file = request.files['file']
        # check if the post request has the file part
        if file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            os.remove("static/files/" + submission.get_filename())
            submission.set_filename(filename)

        db['Submissions'] = submissions_dict
        db.close()

        return redirect(url_for('retrieve_submissions'))
    else:
        submissions_dict = {}
        db = shelve.open('submission.db', 'r')
        submissions_dict = db['Submissions']
        db.close()

        submission = submissions_dict.get(submission_id)
        update_submission_form.details.data = submission.get_details()
        filename = submission.get_filename()

        return render_template('updateSubmissions.html', form=update_submission_form)

# Update Teacher Submission

@app.route('/updateTeacherSubmission/<int:submission_id>/', methods=['GET', 'POST'])
@login_check
def update_teacher_submission(submission_id):
    fileviewing = TeacherForm(request.form)
    if request.method == 'POST' and fileviewing.validate():
        submissions_dict = {}
        db = shelve.open('submission.db', 'w')
        submissions_dict = db['Submissions']

        submission = submissions_dict.get(submission_id)
        submission.set_status(fileviewing.status.data)
        submission.set_grades(fileviewing.grades.data)

        db['Submissions'] = submissions_dict
        db.close()

        return redirect(url_for('teacher_retrieve_submissions'))
    else:
        submissions_dict = {}
        db = shelve.open('submission.db', 'r')
        submissions_dict = db['Submissions']
        db.close()

        submission = submissions_dict.get(submission_id)
        fileviewing.status.data = submission.get_status()

        return render_template('updateTeacherSubmissions.html', form=fileviewing)

# Delete Submission

@app.route('/deleteSubmission/<int:id>', methods=['POST'])
@login_check
def delete_submission(id):
    submissions_dict = {}
    db = shelve.open('submission.db', 'w')
    submissions_dict = db['Submissions']
    submission = submissions_dict.get(id)
    filename = submission.get_filename()
    os.remove("static/files/" + filename)

    submissions_dict.pop(id)

    db['Submissions'] = submissions_dict
    db.close()

    return redirect(url_for('retrieve_submissions'))

# Delete Student Submission

@app.route('/deleteStudentSubmission/<int:id>', methods=['POST'])
@login_check
def delete_student_submission(id):
    submissions_dict = {}
    db = shelve.open('submission.db', 'w')
    submissions_dict = db['Submissions']
    submission = submissions_dict.get(id)
    filename = submission.get_filename()
    os.remove("static/files/" + filename)

    submissions_dict.pop(id)

    db['Submissions'] = submissions_dict
    db.close()

    return redirect(url_for('teacher_retrieve_submissions'))

# Download File

@app.route('/downloadFile/<string:filename>/', methods=['GET', 'POST'])
@login_check
def download_file(filename):
    return send_file("static/files/" + filename, as_attachment=True)

# Quote Generator

if __name__ == '__main__':
    app.run()

