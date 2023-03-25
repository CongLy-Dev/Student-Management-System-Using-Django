import json
import math
from datetime import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum, ExpressionWrapper, F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from .models import *


def student_home(request):
    student = get_object_or_404(Student, admin=request.user)
    total_subject = Assign.objects.filter(grade__student=student).count()
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    total_present = AttendanceReport.objects.filter(student=student, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    subject_name = []
    data_present = []
    data_absent = []
    subjects = Assign.objects.filter(grade__student=student)
    for subject in subjects:
        attendance = Attendance.objects.filter(assign=subject)
        present_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=True, student=student).count()
        absent_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=False, student=student).count()
        subject_name.append(subject.subject.name)
        data_present.append(present_count)
        data_absent.append(absent_count)
    context = {
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_subject': total_subject,
        'subjects': subjects,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': subject_name,
        'page_title': 'Sinh viên'

    }
    return render(request, 'student_template/home_content.html', context)


@ csrf_exempt
def student_view_attendance(request):
    student = get_object_or_404(Student, admin=request.user)
    if request.method != 'POST':
        subjects = Assign.objects.filter(grade__student=student)
        context = {
            'subjects': subjects,
            'page_title': 'Xem điểm danh'
        }
        return render(request, 'student_template/student_view_attendance.html', context)
    else:
        subject_id = request.POST.get('subject')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            subject = get_object_or_404(Subject, id=subject_id)
            start_date = start
            end_date = end
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), subject=subject)
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, student=student)
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            return None


def student_apply_leave(request):
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStudent.objects.filter(student=student),
        'page_title': 'Xin nghỉ phép'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Gửi thành công!")
                return redirect(reverse('student_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Không thể gửi")
    return render(request, "student_template/student_apply_leave.html", context)


def student_feedback(request):
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStudent.objects.filter(student=student),
        'page_title': 'Đánh giá'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Gửi thành công!")
                return redirect(reverse('student_feedback'))
            except Exception:
                messages.error(request, "Không thể gửi")
        else:
            messages.error(request, "Không thể gửi")
    return render(request, "student_template/student_feedback.html", context)


def student_view_profile(request):
    student = get_object_or_404(Student, admin=request.user)
    form = ChangePassword(request.POST or None, request.FILES or None, instance=student)
    context = {'form': form}
    if request.method == 'POST':
        try:
            if form.is_valid():
                password = form.cleaned_data.get('password') or None
                admin = student.admin
                if password != None:
                    admin.set_password(password)
                admin.save()
                messages.success(request, "Cập nhật thành công!")
                return redirect(reverse('student_view_profile'))
            else:
                messages.error(request, "Không thể cập nhật")
        except Exception as e:
            messages.error(request, "Không thể cập nhật")
    return render(request, "student_template/student_view_profile.html", context)


@csrf_exempt
def student_fcmtoken(request):
    token = request.POST.get('token')
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        student_user.fcm_token = token
        student_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def student_view_notification(request):
    student = get_object_or_404(Student, admin=request.user)
    notifications = NotificationStudent.objects.filter(student=student).order_by('-created_at')
    context = {
        'notifications': notifications,
        'page_title': "Xem thông báo"
    }
    return render(request, "student_template/student_view_notification.html", context)


def student_view_fee(request):
    student = get_object_or_404(Student, admin=request.user)
    subjects = Assign.objects.filter(grade__student=student)
    subject = Subject.objects.all()
    sessions = Assign.objects.filter(subject__in=subject)
    context = {
        "sessions": sessions,
        "subjects": subjects,
        'page_title': "Thông tin học phí"
    }
    return render(request, "student_template/student_view_fee.html", context)


def student_view_result(request):
    student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.filter(student=student)
    s = Session.objects.all()
    sb = Subject.objects.filter(session_id__in=s)
    # sessions = Assign.objects.filter(subject__in=subject)
    query = StudentResult.objects.values('student_id') \
        .annotate(result=ExpressionWrapper(Sum(F('score_4') * F('subject__credit')) / Sum('subject__credit'),
                                           output_field=models.FloatField())).filter(student=student)
    context = {
        'query': query,
        # "sessions": sessions,
        'results': results,
        'page_title': "Kết quả học tập"
    }
    return render(request, "student_template/student_view_result.html", context)