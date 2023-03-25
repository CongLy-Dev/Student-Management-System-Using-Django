"""college_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from main_app.EditResultView import EditResultView

from . import hod_views, staff_views, student_views, views


urlpatterns = [
    path("", views.login_page, name='login_page'),
    path("get_attendance", views.get_attendance, name='get_attendance'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    path("doLogin/", views.doLogin, name='user_login'),
    path("logout_user/", views.logout_user, name='user_logout'),
    path("admin/home/", hod_views.admin_home, name='admin_home'),
    path("staff/add", hod_views.add_staff, name='add_staff'),
    path("department/add", hod_views.add_department, name='add_department'),
    path("major/add", hod_views.add_major, name='add_major'),
    path("grade/add", hod_views.add_grade, name='add_grade'),
    path("room/add", hod_views.add_room, name='add_room'),
    path("send_student_notification/", hod_views.send_student_notification,
         name='send_student_notification'),
    path("send_staff_notification/", hod_views.send_staff_notification,
         name='send_staff_notification'),
    path("add_session/", hod_views.add_session, name='add_session'),
    path("admin_notify_student", hod_views.admin_notify_student,
         name='admin_notify_student'),
    path("admin_notify_staff", hod_views.admin_notify_staff,
         name='admin_notify_staff'),
    path("admin_view_profile", hod_views.admin_view_profile,
         name='admin_view_profile'),
    path("check_email_availability", hod_views.check_email_availability,
         name="check_email_availability"),
    path("session/manage/", hod_views.manage_session, name='manage_session'),
    path("session/edit/<int:session_id>",
         hod_views.edit_session, name='edit_session'),
    path("student/view/feedback/", hod_views.student_feedback_message,
         name="student_feedback_message",),
    path("staff/view/feedback/", hod_views.staff_feedback_message,
         name="staff_feedback_message",),
    path("student/view/leave/", hod_views.view_student_leave,
         name="view_student_leave",),
    path("staff/view/leave/", hod_views.view_staff_leave, name="view_staff_leave",),
    path("attendance/view/", hod_views.admin_view_attendance,
         name="admin_view_attendance",),
    path("attendance/fetch/", hod_views.get_admin_attendance,
         name='get_admin_attendance'),
    path("student/add/", hod_views.add_student, name='add_student'),
    path("subject/add/", hod_views.add_subject, name='add_subject'),
    path("staff/manage/", hod_views.manage_staff, name='manage_staff'),
    path("student/manage/", hod_views.manage_student, name='manage_student'),
    path("department/manage/", hod_views.manage_department, name='manage_department'),
    path("major/manage/", hod_views.manage_major, name='manage_major'),
    path("grade/manage/", hod_views.manage_grade, name='manage_grade'),
    path("grade/list/<grade_id>", hod_views.list_student, name='list_student'),
    path("subject/manage/", hod_views.manage_subject, name='manage_subject'),
    path("room/manage/", hod_views.manage_room, name='manage_room'),

    path("staff/edit/<admin_id>",
         hod_views.edit_staff, name='edit_staff'),
    path("staff/delete/<admin_id>",
         hod_views.delete_staff, name='delete_staff'),

    path("student/delete/<admin_id>",
         hod_views.delete_student, name='delete_student'),
    path("student/edit/<admin_id>",
         hod_views.edit_student, name='edit_student'),

    path("department/delete/<department_id>",
         hod_views.delete_department, name='delete_department'),

    path("major/delete/<major_id>",
         hod_views.delete_major, name='delete_major'),

    path("grade/delete/<grade_id>",
         hod_views.delete_grade, name='delete_grade'),

    path("subject/delete/<subject_id>",
         hod_views.delete_subject, name='delete_subject'),

    path("room/delete/<room_id>",
         hod_views.delete_room, name='delete_room'),

    path("session/delete/<session_id>",
         hod_views.delete_session, name='delete_session'),

    path("department/edit/<department_id>",
         hod_views.edit_department, name='edit_department'),
    path("major/edit/<major_id>",
         hod_views.edit_major, name='edit_major'),
    path("grade/edit/<grade_id>",
         hod_views.edit_grade, name='edit_grade'),
    path("subject/edit/<subject_id>",
         hod_views.edit_subject, name='edit_subject'),
    path("room/edit/<room_id>",
         hod_views.edit_room, name='edit_room'),

    path("upload/csv/student", hod_views.upload_file_view, name='upload_view'),
    path("upload/csv/staff", hod_views.upload_file_staff, name='upload_staff'),
    path("upload/csv/sub", hod_views.upload_file_view_sub, name='upload_sub'),


    #Asign
    path("assign/manage/", hod_views.manage_assign, name='manage_assign'),
    path("assign/delete/<assign_id>", hod_views.delete_assign, name='delete_assign'),
    path('assign/add/', hod_views.add_assign, name='add_assign'),
    path('assign/edit/<assign_id>/', hod_views.edit_assign, name='edit_assign'),


    # Staff
    path("staff/home/", staff_views.staff_home, name='staff_home'),
    path("staff/apply/leave/", staff_views.staff_apply_leave,
         name='staff_apply_leave'),
    path("staff/feedback/", staff_views.staff_feedback, name='staff_feedback'),
    path("staff/view/profile/", staff_views.staff_view_profile,
         name='staff_view_profile'),
    path("staff/attendance/take/", staff_views.staff_take_attendance,
         name='staff_take_attendance'),
    path("staff/attendance/update/", staff_views.staff_update_attendance,
         name='staff_update_attendance'),
    path("staff/get_students/", staff_views.get_students, name='get_students'),
    path("staff/attendance/fetch/", staff_views.get_student_attendance,
         name='get_student_attendance'),
    path("staff/attendance/save/",
         staff_views.save_attendance, name='save_attendance'),
    path("staff/attendance/update/",
         staff_views.update_attendance, name='update_attendance'),
    path("staff/fcmtoken/", staff_views.staff_fcmtoken, name='staff_fcmtoken'),
    path("staff/view/notification/", staff_views.staff_view_notification,
         name="staff_view_notification"),
    path("staff/result/add/", staff_views.staff_add_result, name='staff_add_result'),
    path("staff/result/edit/", EditResultView.as_view(),
         name='edit_student_result'),
    path('staff/result/fetch/', staff_views.fetch_student_result,
         name='fetch_student_result'),



    # Student
    path("student/home/", student_views.student_home, name='student_home'),
    path("student/view/attendance/", student_views.student_view_attendance,
         name='student_view_attendance'),
    path("student/apply/leave/", student_views.student_apply_leave,
         name='student_apply_leave'),
    path("student/feedback/", student_views.student_feedback,
         name='student_feedback'),
    path("student/view/profile/", student_views.student_view_profile,
         name='student_view_profile'),
    path("student/fcmtoken/", student_views.student_fcmtoken,
         name='student_fcmtoken'),
    path("student/view/notification/", student_views.student_view_notification,
         name="student_view_notification"),
    path('student/view/result/', student_views.student_view_result,
         name='student_view_result'),
    path('student/view/fee/', student_views.student_view_fee,
         name='student_view_fee'),

]
