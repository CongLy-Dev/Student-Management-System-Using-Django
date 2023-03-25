import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import datetime
from .forms import *
from .models import *


def staff_home(request):
    staff = get_object_or_404(Staff, admin_id=request.user)
    total_students = Student.objects.filter(major=staff.major).count()
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    subjects = Assign.objects.filter(staff=staff)
    total_subject = subjects.count()
    sbj = Subject.objects.filter(assign__in=subjects)
    attendance_list = Attendance.objects.filter(subject__in=sbj)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in sbj:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.id + " " + subject.name)
        attendance_list.append(attendance_count)
    context = {
        'page_title': str(staff.last_name) + " " + str(staff.first_name) +' ('+ str(staff.major) + ')',
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list
    }
    return render(request, 'staff_template/home_content.html', context)


@csrf_exempt
def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Assign.objects.filter(staff_id=staff)
    # assign = Assign.objects.get(staff_id=staff)
    # subjects = Subject.objects.filter(id=assign.subject.id)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Điểm danh'
    }

    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        # subjects = get_object_or_404(Subject, id=subject_id)
        # session = get_object_or_404(Session, id=session_id)
        subject = Subject.objects.get(id=subject_id, session_id=session_id)
        assign = Assign.objects.get(subject_id=subject)
        students = Student.objects.filter(grade_id=assign.grade.id)
        student_data = []
        for student in students:
            data = {
                    "id": student.admin.id,
                    "name": student.last_name + " " + student.first_name
                    }
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def save_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    students = json.loads(student_data)
    try:
        session = get_object_or_404(Session, id=session_id)
        subject = get_object_or_404(Subject, id=subject_id)
        attendance = Attendance(session=session, subject=subject, date=date)
        attendance.save()

        for student_dict in students:
            student = get_object_or_404(Student, admin_id=student_dict.get('id'))
            attendance_report = AttendanceReport(student=student, attendance=attendance, status=student_dict.get('status'))
            attendance_report.save()
    except Exception as e:
        return e

    return HttpResponse("OK")


@csrf_exempt
def staff_update_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Assign.objects.filter(staff_id=staff)
    # assign = Assign.objects.get(staff_id=staff)
    # subjects = Subject.objects.filter(id=assign.subject.id)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Cập nhật điểm danh'
    }

    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []
        for attendance in attendance_data:
            data = {"id": attendance.student.admin_id,
                    "name": attendance.student.last_name + " " + attendance.student.first_name,
                    "status": attendance.status}
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for student_dict in students:
            student = get_object_or_404(
                Student, admin_id=student_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            attendance_report.status = student_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return e

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Nộp đơn xin nghỉ phép'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Gửi thành công")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Không thể gửi")
        else:
            messages.error(request, "Không thể gửi")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Đánh giá'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Gửi thành công")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Không thể gửi")
        else:
            messages.error(request, "Không thể gửi")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = ChangePassword(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form}
    if request.method == 'POST':
        try:
            if form.is_valid():
                password = form.cleaned_data.get('password') or None
                admin = staff.admin
                if password != None:
                    admin.set_password(password)
                admin.save()
                messages.success(request, "Cập nhật thành công!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Không thể cập nhật")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Không thể cập nhật")
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "Xem thông báo"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Assign.objects.filter(staff_id=staff)

    # subject = Subject.objects.all()
    # subjects = Assign.objects.filter(staff_id=staff, subject_id__in=subject)

    sessions = Session.objects.all()
    context = {
        'page_title': 'Nhập điểm',
        'subjects': subjects,
        'sessions': sessions
    }
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_list')
            subject_id = request.POST.get('subject')
            exam = request.POST.get('exam')
            student = get_object_or_404(Student, admin_id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            try:
                data = StudentResult.objects.get(student=student, subject=subject)
                data.exam = exam
                data.save()
                messages.success(request, "Cập nhật thành công")
            except:
                result = StudentResult(student=student, subject=subject, exam=exam)
                result.save()
                messages.success(request, "Nhập điểm thành công")
        except Exception as e:
            messages.warning(request, "Không thể nhập" + str(e))
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
    try:
        subject_id = request.POST.get('subject')
        student_id = request.POST.get('student')
        student = get_object_or_404(Student, admin_id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        result = StudentResult.objects.get(student=student, subject=subject)
        result_data = {
            'exam': result.exam
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')
