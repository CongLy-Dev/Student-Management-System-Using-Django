import csv
import json
import os
import time
from .filters import StudentFilter, StaffFilter, SubFilter
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView, CreateView, ListView
from tablib import Dataset
from .forms import *
from .models import *
from django.forms import inlineformset_factory
from django.core.paginator import Paginator


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    total_department = Department.objects.all().count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name[:7])
        attendance_list.append(attendance_count)

    # Total Subjects and students in Each department
    department_all = Department.objects.all()
    department_name_list = []
    subject_count_list = []
    student_count_list_in_department = []

    for department in department_all:
        subjects = Subject.objects.filter(id=department.id).count()
        students = Student.objects.filter(admin_id=department.id).count()
        department_name_list.append(department.name)
        subject_count_list.append(subjects)
        student_count_list_in_department.append(students)
    
    subject_all = Subject.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        department = Department.objects.get(id=department.id)
        student_count = Student.objects.filter(admin_id=department.id).count()
        subject_list.append(subject.name)
        student_count_list_in_subject.append(student_count)


    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Student.objects.all()
    for student in students:
        
        attendance = AttendanceReport.objects.filter(student_id=student.admin_id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.admin_id, status=False).count()
        leave = LeaveReportStudent.objects.filter(student_id=student.admin_id, status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leave+absent)
        student_name_list.append(student.admin.first_name)

    context = {
        'page_title': "Phòng đào tạo",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_department': total_department,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list,
        'student_attendance_present_list': student_attendance_present_list,
        'student_attendance_leave_list': student_attendance_leave_list,
        "student_name_list": student_name_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "student_count_list_in_department": student_count_list_in_department,
        "department_name_list": department_name_list,

    }
    return render(request, 'hod_template/home_content.html', context)


def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Thêm giảng viên'}
    if request.method == 'POST':
        if form.is_valid():
            id = form.cleaned_data.get('id')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            gender = form.cleaned_data.get('gender')
            dob = form.cleaned_data.get('dob')
            pob = form.cleaned_data.get('pob')
            level = form.cleaned_data.get('level')
            number = form.cleaned_data.get('number')
            address = form.cleaned_data.get('address')
            major = form.cleaned_data.get('major')
            department = form.cleaned_data.get('department')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            profile_pic = request.FILES.get('profile_pic')
            try:
                user = CustomUser.objects.create_user(id=id,
                    email=email, password=password, user_type=2)
                user.staff.first_name = first_name
                user.staff.last_name = last_name
                user.staff.profile_pic = profile_pic
                user.staff.gender = gender
                user.staff.dob = dob
                user.staff.pob = pob
                user.staff.level = level
                user.staff.number = number
                user.staff.address = address
                user.staff.department = department
                user.staff.major = major
                user.save()
                messages.success(request, "Thêm thành công")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Không thể thêm: " + str(e))
        else:
            messages.error(request, "Không thể thêm")
    return render(request, 'hod_template/add_staff_template.html', context)


def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Thêm sinh viên'}
    if request.method == 'POST':
        if student_form.is_valid():
            id = student_form.cleaned_data.get('id')
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            gender = student_form.cleaned_data.get('gender')
            dob = student_form.cleaned_data.get('dob')
            pob = student_form.cleaned_data.get('pob')
            grade = student_form.cleaned_data.get('grade')
            number = student_form.cleaned_data.get('number')
            address = student_form.cleaned_data.get('address')
            major = student_form.cleaned_data.get('major')
            email = student_form.cleaned_data.get('email')
            password = student_form.cleaned_data.get('password')
            profile_pic = request.FILES.get('profile_pic')
            try:
                user = CustomUser.objects.create_user(id=id,
                    email=email, password=password, user_type=3)
                user.student.first_name = first_name
                user.student.last_name = last_name
                user.student.profile_pic = profile_pic
                user.student.gender = gender
                user.student.dob = dob
                user.student.pob = pob
                user.student.grade = grade
                user.student.number = number
                user.student.address = address
                user.student.major = major
                user.save()
                messages.success(request, "Thêm thành công")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "Không thể thêm: " + str(e))
        else:
            messages.error(request, "Không thể thêm")
    return render(request, 'hod_template/add_student_template.html', context)


def add_department(request):
    form = DepartmentForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Thêm bộ môn'
    }
    if request.method == 'POST':
        if form.is_valid():
            id = form.cleaned_data.get('id')
            name = form.cleaned_data.get('name')
            try:
                department = Department()
                department.id = id
                department.name = name
                department.save()
                messages.success(request, "Thêm thành công")
                return redirect(reverse('add_department'))
            except:
                messages.error(request, "Không thể thêm")
        else:
            messages.error(request, "Không thể thêm")
    return render(request, 'hod_template/add_department_template.html', context)


def add_major(request):
    form = MajorForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Thêm ngành'
    }
    if request.method == 'POST':
        if form.is_valid():
            id = form.cleaned_data.get('id')
            name = form.cleaned_data.get('name')
            department = form.cleaned_data.get('department')
            try:
                major = Major()
                major.id = id
                major.name = name
                major.department = department
                major.save()
                messages.success(request, "Thêm thành công!")
                return redirect(reverse('add_major'))
            except:
                messages.error(request, "Không thể thêm")
        else:
            messages.error(request, "Không thể thêm")
    return render(request, 'hod_template/add_major_template.html', context)


def add_grade(request):
    form = GradeForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Thêm lớp'
    }
    if request.method == 'POST':
        if form.is_valid():
            id = form.cleaned_data.get('id')
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            major = form.cleaned_data.get('major')
            try:
                grade = Grade()
                grade.id = id
                grade.name = name
                grade.course = course
                grade.major = major
                grade.save()
                messages.success(request, "Thêm thành công")
                return redirect(reverse('add_grade'))
            except:
                messages.error(request, "Không thể thêm")
        else:
            messages.error(request, "Không thể thêm")
    return render(request, 'hod_template/add_grade_template.html', context)


def add_room(request):
    form = RoomForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Thêm phòng'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            dimension = form.cleaned_data.get('dimension')
            try:
                room = Room()
                room.name = name
                room.dimension = dimension
                room.save()
                messages.success(request, "Thêm thành công")
                return redirect(reverse('add_room'))
            except:
                messages.error(request, "Không thể thêm")
        else:
            messages.error(request, "Không thể thêm")
    return render(request, 'hod_template/add_room_template.html', context)


def add_subject(request):
    form = SubjectForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Thêm học phần'
    }
    if request.method == 'POST':
        if form.is_valid():
            id = form.cleaned_data.get('id')
            name = form.cleaned_data.get('name')
            credit = form.cleaned_data.get('credit')
            type = form.cleaned_data.get('type')
            major = form.cleaned_data.get('major')
            staff = form.cleaned_data.get('staff')
            session = form.cleaned_data.get('session')
            try:
                subject = Subject()
                subject.id = id
                subject.name = name
                subject.major = major
                subject.credit = credit
                subject.type = type
                subject.staff = staff
                subject.session = session
                subject.save()
                messages.success(request, "Thêm thành công!")
                return redirect(reverse('add_subject'))

            except Exception as e:
                messages.error(request, "Không thể thêm: " + str(e))
        else:
            messages.error(request, "Không thể thêm")

    return render(request, 'hod_template/add_subject_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    t = Staff.objects.filter(admin_id__in=allStaff)
    filter = StaffFilter(request.GET, queryset=t)
    t = filter.qs
    context = {
        't': t,
        'filter': filter,
        'allStaff': allStaff,
        'page_title': 'Quản lý giảng viên'
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    students = CustomUser.objects.filter(user_type=3)
    s = Student.objects.filter(admin_id__in=students)
    filter = StudentFilter(request.GET, queryset=s)
    s = filter.qs
    context = {
        'filter': filter,
        's': s,
        'students': students,
        'page_title': 'Quản lý sinh viên'
    }
    return render(request, "hod_template/manage_student.html", context)


def manage_department(request):
    departments = Department.objects.all()
    context = {
        'departments': departments,
        'page_title': 'Quản lý bộ môn'
    }
    return render(request, "hod_template/manage_department.html", context)


def manage_major(request):
    majors = Major.objects.all()
    context = {
        'majors': majors,
        'page_title': 'Quản lý ngành'
    }
    return render(request, "hod_template/manage_major.html", context)


def manage_grade(request):
    grades = Grade.objects.all()
    context = {
        'grades': grades,
        'page_title': 'Quản lý lớp'
    }
    return render(request, "hod_template/manage_grade.html", context)


def list_student(request, grade_id):
    grades = Grade.objects.filter(id=grade_id)
    students = Student.objects.filter(grade_id=grade_id).order_by('admin_id')
    context = {
        'grades': grades,
        'students': students,
        'page_title': 'Danh sách lớp'
    }
    return render(request, "hod_template/list.html", context)


def manage_subject(request):
    subjects = Subject.objects.all()
    filter = SubFilter(request.GET, queryset=subjects)
    subjects = filter.qs
    context = {
        'filter': filter,
        'subjects': subjects,
        'page_title': 'Quản lý học phần'
    }
    return render(request, "hod_template/manage_subject.html", context)


def manage_room(request):
    rooms = Room.objects.all()
    context = {
        'rooms': rooms,
        'page_title': 'Quản lý phòng học'
    }
    return render(request, "hod_template/manage_room.html", context)


def edit_staff(request, admin_id):
    staff = get_object_or_404(Staff, admin_id=admin_id)
    form = StaffEditForm(request.POST or None, request.FILES or None, instance=staff)
    context = {
        'form': form,
        'admin_id': admin_id,
        'page_title': 'Cập nhật giảng viên'
    }
    if request.method == 'POST':
        if form.is_valid():
            id = form.cleaned_data.get('id')
            username = form.cleaned_data.get('username')
            last_name = form.cleaned_data.get('last_name')
            first_name = form.cleaned_data.get('first_name')
            gender = form.cleaned_data.get('gender')
            dob = form.cleaned_data.get('dob')
            pob = form.cleaned_data.get('pob')
            level = form.cleaned_data.get('level')
            number = form.cleaned_data.get('number')
            address = form.cleaned_data.get('address')
            major = form.cleaned_data.get('major')
            department = form.cleaned_data.get('department')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password') or None
            profile_pic = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if profile_pic != None:
                    user.staff.profile_pic = profile_pic
                user.staff.first_name = first_name
                user.staff.last_name = last_name
                user.staff.gender = gender
                user.staff.dob = dob
                user.staff.pob = pob
                user.staff.level = level
                user.staff.number = number
                user.staff.address = address
                user.staff.major = major
                user.staff.department = department
                user.save()
                staff.save()
                messages.success(request, "Cập nhật thành công!")
                return redirect(reverse('edit_staff', args=[admin_id]))
            except Exception as e:
                messages.error(request, "Không thể cập nhật: " + str(e))
        else:
            messages.error(request, "Không thể cập nhật")
    else:
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, admin_id):
    student = get_object_or_404(Student, admin_id=admin_id)
    form = StudentEditForm(request.POST or None, request.FILES or None, instance=student)
    context = {
        'form': form,
        'admin_id': admin_id,
        'page_title': 'Cập nhật sinh viên'
    }
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            last_name = form.cleaned_data.get('last_name')
            first_name = form.cleaned_data.get('first_name')
            gender = form.cleaned_data.get('gender')
            dob = form.cleaned_data.get('dob')
            pob = form.cleaned_data.get('pob')
            grade = form.cleaned_data.get('grade')
            number = form.cleaned_data.get('number')
            address = form.cleaned_data.get('address')
            major = form.cleaned_data.get('major')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password') or None
            profile_pic = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if profile_pic != None:
                    user.student.profile_pic = profile_pic
                user.student.first_name = first_name
                user.student.last_name = last_name
                user.student.gender = gender
                user.student.dob = dob
                user.student.pob = pob
                user.student.grade = grade
                user.student.number = number
                user.student.address = address
                user.student.major = major
                user.save()
                student.save()
                messages.success(request, "Cập nhật thành công!")
                return redirect(reverse('edit_student', args=[admin_id]))
            except Exception as e:
                messages.error(request, "Không thể cập nhật")
                return render(request, "hod_template/edit_student_template.html", context)
        else:
            messages.error(request, "Không thể cập nhật")
    else:
        return render(request, "hod_template/edit_student_template.html", context)


def edit_department(request, department_id):
    instance = get_object_or_404(Department, id=department_id)
    form = DepartmentForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'department_id': department_id,
        'page_title': 'Cập nhật bộ môn'
    }
    if request.method == 'POST':
        if form.is_valid():
            id = form.cleaned_data.get('id')
            name = form.cleaned_data.get('name')
            try:
                department = Department.objects.get(id=department_id)
                department.id = id
                department.name = name
                department.save()
                messages.success(request, "Cập nhật thành công!")
            except:
                messages.error(request, "Không thể cập nhật")
        else:
            messages.error(request, "Không thể cập nhật")

    return render(request, 'hod_template/edit_department_template.html', context)


def edit_major(request, major_id):
    instance = get_object_or_404(Major, id=major_id)
    form = MajorForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'major_id': major_id,
        'page_title': 'Cập nhật ngành'
    }
    if request.method == 'POST':
        if form.is_valid():
            id = form.cleaned_data.get('id')
            name = form.cleaned_data.get('name')
            department = form.cleaned_data.get('department')
            try:
                major = Major.objects.get(id=major_id)
                major.id = id
                major.name = name
                major.department = department
                major.save()
                messages.success(request, "Cập nhật thành công")
            except:
                messages.error(request, "Không thể cập nhật")
        else:
            messages.error(request, "Không thể cập nhật")

    return render(request, 'hod_template/edit_major_template.html', context)


def edit_grade(request, grade_id):
    instance = get_object_or_404(Grade, id=grade_id)
    form = GradeForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'grade_id': grade_id,
        'page_title': 'Cập nhật lớp'
    }
    if request.method == 'POST':
        if form.is_valid():
            id = form.cleaned_data.get('id')
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            major = form.cleaned_data.get('major')
            try:
                grade = Grade.objects.get(id=grade_id)
                grade.id = id
                grade.name = name
                grade.course = course
                grade.major = major
                grade.save()
                messages.success(request, "Cập nhật thành công")
            except:
                messages.error(request, "Không thể cập nhật")
        else:
            messages.error(request, "Không thể cập nhậte")

    return render(request, 'hod_template/edit_grade_template.html', context)


def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Cập nhật học phần'
    }
    if request.method == 'POST':
        if form.is_valid():
            id = form.cleaned_data.get('id')
            name = form.cleaned_data.get('name')
            credit = form.cleaned_data.get('credit')
            type = form.cleaned_data.get('type')
            major = form.cleaned_data.get('major')
            session = form.cleaned_data.get('session')

            try:
                subject = Subject.objects.get(id=subject_id)
                subject.id = id
                subject.name = name
                subject.credit = credit
                subject.type = type
                subject.major = major
                subject.session = session
                subject.save()
                messages.success(request, "Cập nhật thành công!")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Không thể cập nhật " + str(e))
        else:
            messages.error(request, "Không thể cập nhật")
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_room(request, room_id):
    instance = get_object_or_404(Room, id=room_id)
    form = RoomForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'room_id': room_id,
        'page_title': 'Cập nhật phòng học'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            dimension = form.cleaned_data.get('dimension')
            try:
                room = Room.objects.get(id=room_id)
                room.name = name
                room.dimension = dimension
                room.save()
                messages.success(request, "Cập nhật thành công")
            except:
                messages.error(request, "Không thể cập nhật")
        else:
            messages.error(request, "Không thể cập nhậte")

    return render(request, 'hod_template/edit_room_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Thêm học kỳ'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Thêm thành công!")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Không thể thêm ' + str(e))
        else:
            messages.error(request, 'Không thể thêm')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Quản lý học kỳ'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Cập nhật học kỳ'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cập nhật thành công")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Không thể cập nhật " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Không thể cập nhật ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


def add_assign(request):
    assign_form = AssignForm(request.POST or None)
    context = {'form': assign_form, 'page_title': 'Phân công giảng dạy'}
    if request.method == 'POST':
        if assign_form.is_valid():
            subject = assign_form.cleaned_data.get('subject')
            group = assign_form.cleaned_data.get('group')
            room = assign_form.cleaned_data.get('room')
            grade = assign_form.cleaned_data.get('grade')
            staff = assign_form.cleaned_data.get('staff')
            period = assign_form.cleaned_data.get('period')
            day = assign_form.cleaned_data.get('day')
            try:
                assign = Assign()
                assign.subject = subject
                assign.group = group
                assign.room = room
                assign.grade = grade
                assign.staff = staff
                assign.period = period
                assign.day = day
                assign.save()
                messages.success(request, "Thêm thành công")
                return redirect(reverse('add_assign'))
            except Exception as e:
                messages.error(request, "Không thể thêm: " + str(e))
        else:
            messages.error(request, "Không thể thêm")
    return render(request, 'hod_template/add_assign_template.html', context)


def manage_assign(request):
    assigns = Assign.objects.all()
    context = {
        'assigns': assigns,
        'page_title': 'Quản lý giảng dạy'
    }
    return render(request, "hod_template/manage_assign.html", context)


def edit_assign(request, assign_id):
    assign = get_object_or_404(Assign, id=assign_id)
    form = AssignForm(request.POST or None, instance=assign)
    context = {
        'form': form,
        'assign_id': assign_id,
        'page_title': 'Cập nhật giảng dạy'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cập nhật thành công")
                return redirect(reverse('edit_assign', args=[assign_id]))
            except Exception as e:
                messages.error(
                    request, "Không thể cập nhật " + str(e))
                return render(request, "hod_template/edit_assign_template.html", context)
        else:
            messages.error(request, "Không thể cập nhật ")
            return render(request, "hod_template/edit_assign_template.html", context)
    else:
        return render(request, "hod_template/edit_assign_template.html", context)


def delete_assign(request, assign_id):
    assign = get_object_or_404(Assign, id=assign_id)
    assign.delete()
    messages.success(request, "Xóa thành công!")
    return redirect(reverse('manage_assign'))


# class AssignList(ListView):
#     model = Assign
#     template_name = "hod_template/manage_assign.html"

#
# class AssignCreate(CreateView):
#     model = Assign
#     fields = ['subject', 'room', 'grade', 'staff']
#     template_name = "hod_template/add_assign_template.html"
#
#     def get_context_data(self):
#         context = super().get_context_data()
#         if self.request.POST:
#             context['assign_time'] = AssignTimeFormset(self.request.POST)
#         else:
#             context['assign_time'] = AssignTimeFormset()
#         return context
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         assign_time = context['assign_time']
#         with transaction.atomic():
#             self.object = form.save()
#             if assign_time.is_valid():
#                 assign_time.instance = self.object
#                 assign_time.save()
#         return redirect(reverse('add_assign'))

# def add_assign(request):
#     if request.method == "POST":
#         assign = AssignForm(request.POST, instance=Assign())
#         assign_time = [AssignTimeForm(request.POST, prefix=str(x), instance=AssignTime()) for x in range(0, 3)]
#         if assign.is_valid() and all([at.is_valid() for at in assign_time]):
#             new_assign = assign.save()
#             for at in assign_time:
#                 new_assign_time = at.save(commit=False)
#                 new_assign_time.assign = new_assign
#                 new_assign_time.save()
#             return redirect(reverse('add_assign'))
#     else:
#         assign = AssignForm(instance=Assign())
#         assign_time = [AssignTimeForm(prefix=str(x), instance=AssignTime()) for x in range(0, 3)]
#     return render(request, "hod_template/add_assign_template.html", {'assign': assign, 'assign_time': assign_time})


# def edit_assign(request, assign_id):
#     instance = get_object_or_404(Assign, id=assign_id)
#     form = AssignForm(request.POST or None, instance=instance)
#     context = {
#         'form': form,
#         'major_id': assign_id,
#         'page_title': 'Cập nhật giảng dạy'
#     }
#     if request.method == 'POST':
#         if form.is_valid():
#             subject = form.cleaned_data.get('subject')
#             room = form.cleaned_data.get('room')
#             grade = form.cleaned_data.get('grade')
#             staff = form.cleaned_data.get('staff')
#             try:
#                 assign = Assign.objects.get(id=assign_id)
#                 assign.subject = subject
#                 assign.room = room
#                 assign.grade = grade
#                 assign.staff = staff
#                 assign.save()
#                 messages.success(request, "Cập nhật thành công")
#             except:
#                 messages.error(request, "Không thể cập nhật")
#         else:
#             messages.error(request, "Không thể cập nhật")
#
#     return render(request, 'hod_template/edit_assign_template.html', context)


# def add_assign(request, pk):
#     AssignFormSet = inlineformset_factory(Assign, AssignTime, fields=('period', 'day'))
#     assign = Assign.objects.get(id=pk)
#     formset = AssignFormSet(instance=assign)
#     if request.method == 'POST':
#         form = AssignForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('add_assign')
#     context = {'formset': formset}
#     return render(request, "hod_template/add_assign_template.html", context)


# def edit_assign(request, pk):
#     assign = Assign.objects.get(id=pk)
#     form = AssignForm(instance=assign)
#     if request.method == 'POST':
#         form = AssignForm(request.POST, instance=assign)
#
#         if form.is_valid():
#             form.save()
#             return redirect('edit_assign')
#     context = {'form': form}
#     return render(request, "hod_template/edit_assign_template.html", context)
#
#
# def manage_assign(request):
#     assigns = Assign.objects.filter()
#     assign_times = AssignTime.objects.filter()
#     context = {
#         'assigns': assigns,
#         'assign_times': assign_times,
#         'page_title': 'Quản lý giảng dạy'
#     }
#     return render(request, "hod_template/manage_assign.html", context)


# def delete_assign(request, assign_id):
#     assign = get_object_or_404(Assign, id=assign_id)
#     assign.delete()
#     messages.success(request, "Xóa thành công!")
#     return redirect(reverse('manage_assign'))

# class AssignInline():
#     form_class = AssignForm
#     model = Assign
#     template_name = "hod_template/add_assign_template.html"
#
#     def form_valid(self, form):
#         named_formsets = self.get_named_formsets()
#         if not all((x.is_valid() for x in named_formsets.values())):
#             return self.render_to_response(self.get_context_data(form=form))
#
#         self.object = form.save()
#
#         # for every formset, attempt to find a specific formset save function
#         # otherwise, just save.
#         for name, formset in named_formsets.items():
#             formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
#             if formset_save_func is not None:
#                 formset_save_func(formset)
#             else:
#                 formset.save()
#         return redirect('add_assign')
#
#     def formset_assign_time_valid(self, formset):
#         """
#         Hook for custom formset saving.Useful if you have multiple formsets
#         """
#         assign_times = formset.save(commit=False)  # self.save_formset(formset, contact)
#         # add this 2 lines, if you have can_delete=True parameter
#         # set in inlineformset_factory func
#         for obj in formset.deleted_objects:
#             obj.delete()
#         for assign_time in assign_times:
#             assign_time.assign = self.object
#             assign_time.save()
#
#
# class AddAssign(AssignInline, CreateView):
#
#     def get_context_data(self, **kwargs):
#         ctx = super(AddAssign, self).get_context_data(**kwargs)
#         ctx['named_formsets'] = self.get_named_formsets()
#         return ctx
#
#     def get_named_formsets(self):
#         if self.request.method == "GET":
#             return {
#                 'assign_times': AssignFormSet(prefix='assign_times'),
#             }
#         else:
#             return {
#                 'assign_times': AssignFormSet(self.request.POST or None, self.request.FILES or None, prefix='assign_times'),
#             }
#
#
# class EditAssign(AssignInline, UpdateView):
#
#     def get_context_data(self, **kwargs):
#         ctx = super(EditAssign, self).get_context_data(**kwargs)
#         ctx['named_formsets'] = self.get_named_formsets()
#         return ctx
#
#     def get_named_formsets(self):
#         return {
#             'assign_times': AssignFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='assign_times'),
#         }


# def manage_assign(request):
#     assigns = Assign.objects.all()
#     assign_times = AssignTime.objects.all()
#     context = {
#         'assigns': assigns,
#         'assign_times': assign_times
#     }
#     return render(request, 'hod_template/manage_assign.html', context)





# def delete_assign_time(request, pk):
#     try:
#         assign_time = AssignTime.objects.get(id=pk)
#     except AssignTime.DoesNotExist:
#         messages.success(
#             request, 'Không tồn tại'
#             )
#         return redirect('edit_assign', pk=assign_time.assign.id)
#
#     assign_time.delete()
#     messages.success(
#             request, 'Xóa thành công'
#             )
#     return redirect('edit_assign', pk=assign_time.assign.id)


def upload_file_view(request):
    form = CsvForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Import dữ liệu'}
    if form.is_valid():
        form.save()
        obj = Csv.objects.get(activated=False)
        with open(obj.file_name.path, 'r', encoding="utf8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    pass
                else:
                    grade = Grade.objects.get(name=row[6])
                    major = Major.objects.get(name=row[9])
                    user = CustomUser.objects.create_user(
                        id=row[0],
                        email=row[10],
                        password=row[11],
                        user_type=3,
                    )
                    user.student.last_name = row[1]
                    user.student.first_name = row[2]
                    user.student.gender = row[3]
                    user.student.dob = row[4]
                    user.student.pob = row[5]
                    user.student.grade = grade
                    user.student.number = row[7]
                    user.student.address = row[8]
                    user.student.major = major
                    user.student.profile_pic = row[12]
                    user.save()
            obj.activated = True
            obj.save()
        messages.success(request, "Import thành công")
        return redirect(reverse('manage_student'))
    return render(request, 'hod_template/upload_csv.html', context)



def upload_file_staff(request):
    form = CsvForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Import dữ liệu'}
    if form.is_valid():
        form.save()
        obj = Csv.objects.get(activated=False)
        with open(obj.file_name.path, 'r', encoding="utf8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    pass
                else:
                    department = Department.objects.get(name=row[10])
                    major = Major.objects.get(name=row[9])
                    user = CustomUser.objects.create_user(
                        id=row[0],
                        email=row[11],
                        password=row[12],
                        user_type=2,
                    )
                    user.staff.last_name = row[1]
                    user.staff.first_name = row[2]
                    user.staff.gender = row[3]
                    user.staff.dob = row[4]
                    user.staff.pob = row[5]
                    user.staff.level = row[6]
                    user.staff.department = department
                    user.staff.number = row[7]
                    user.staff.address = row[8]
                    user.staff.major = major
                    user.staff.profile_pic = row[13]
                    user.save()
            obj.activated = True
            obj.save()
        messages.success(request, "Import thành công")
        return redirect(reverse('manage_staff'))
    return render(request, 'hod_template/upload_csv.html', context)




def upload_file_view_staff(request):
    form = CsvForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Import dữ liệu'}
    if form.is_valid():
        form.save()
        obj = Csv.objects.get(activated=False)
        with open(obj.file_name.path, 'r', encoding="utf8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    pass
                else:
                    grade = Grade.objects.get(name=row[6])
                    major = Major.objects.get(name=row[9])
                    user = CustomUser.objects.create_user(
                        id=row[0],
                        email=row[10],
                        password=row[11],
                        user_type=3,
                    )
                    user.student.last_name = row[1]
                    user.student.first_name = row[2]
                    user.student.gender = row[3]
                    user.student.dob = row[4]
                    user.student.pob = row[5]
                    user.student.grade = grade
                    user.student.number = row[7]
                    user.student.address = row[8]
                    user.student.major = major
                    user.student.profile_pic = row[12]
                    user.save()
            obj.activated = True
            obj.save()
        messages.success(request, "Import thành công")
        return redirect(reverse('manage_student'))
    return render(request, 'hod_template/upload_csv.html', context)



def upload_file_view_sub(request):
    form = CsvForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Import dữ liệu'}
    if form.is_valid():
        form.save()
        obj = Csv.objects.get(activated=False)
        with open(obj.file_name.path, 'r', encoding="utf8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    pass
                else:
                    maj = Major.objects.get(name=row[5])
                    ses = Session.objects.get(name=row[6])
                    sub = Subject.objects.create(id=row[0], name=row[1], credit=row[2],
                                                 type=row[3], fee=row[4], major=maj, session=ses)
                    sub.save()
            obj.activated = True
            obj.save()
        messages.success(request, "Import thành công")
        return redirect(reverse('manage_subject'))
    return render(request, 'hod_template/upload_csv.html', context)




@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def student_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Đánh giá từ Sinh viên'
        }
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def staff_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Đánh giá từ Giảng viên'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Đơn xin nghỉ phép của giảng viên'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_student_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Đơn xin nghỉ phép của sinh viên'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    subjects = Subject.objects.all()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Xem điểm danh'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = ChangePassword(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'Đổi mật khẩu'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                # first_name = form.cleaned_data.get('first_name')
                # last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                # passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                # if passport != None:
                #     fs = FileSystemStorage()
                #     filename = fs.save(passport.name, passport)
                #     passport_url = fs.url(filename)
                #     custom_user.profile_pic = passport_url
                # custom_user.first_name = first_name
                # custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Cập nhật thành công!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Không thể cập nhật")
        except Exception as e:
            messages.error(
                request, "Không thể cập nhật: " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Gửi thông báo",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_student(request):
    students = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Gửi thông báo",
        'students': students
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
def send_student_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Hệ thống Quản lý sinh viên",
                'body': message,
                'click_action': reverse('student_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': student.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Hệ thống Quản lý sinh viên",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': staff.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, admin_id):
    staff = get_object_or_404(CustomUser, id=admin_id)
    staff.delete()
    messages.success(request, "Xóa thành công!")
    return redirect(reverse('manage_staff'))


def delete_student(request, admin_id):
    student = get_object_or_404(CustomUser, id=admin_id)
    student.delete()
    messages.success(request, "Xóa thành công!")
    return redirect(reverse('manage_student'))


def delete_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    try:
        department.delete()
        messages.success(request, "Xóa thành công!")
    except Exception:
        messages.error(
            request, "Xin lỗi, một số ngành đã được chỉ định vào khoa này rồi. Vui lòng thay đổi bộ phận ngành bị ảnh hưởng và thử lại")
    return redirect(reverse('manage_department'))


def delete_major(request, major_id):
    major = get_object_or_404(Major, id=major_id)
    try:
        major.delete()
        messages.success(request, "Xóa thành công!")
    except Exception:
        messages.error(
            request, "Xin lỗi, một số lớp đã được chỉ định vào ngành này rồi. Vui lòng thay đổi lớp bị ảnh hưởng và thử lại")
    return redirect(reverse('manage_major'))


def delete_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    try:
        grade.delete()
        messages.success(request, "Xóa thành công!")
    except Exception:
        messages.error(
            request, "Xin lỗi, một số sinh viên đã được chỉ định vào lớp này rồi. Vui lòng thay đổi bộ phận sinh viên bị ảnh hưởng và thử lại")
    return redirect(reverse('manage_grade'))


def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Xóa thành công")
    return redirect(reverse('manage_subject'))


def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    messages.success(request, "Xóa thành công")
    return redirect(reverse('manage_room'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Xóa thành công")
    except Exception:
        messages.error(
            request, "Vui lòng thay đổi các học phần bị ảnh hưởng")
    return redirect(reverse('manage_session'))
