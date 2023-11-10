from django.urls import path

from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("local_recent/", views.show_recent_data, name="show_recent_data"),
    path("filter/", views.filter_page, name="filters"),
    path("filtered/", views.day_wise_stud_per_course, name="day_wise_stud_per_course"),
    path("remote_recent/", views.show_remote_recent_data, name="show_remote_recent_data"),
    path("course_percentage/", views.course_wise_percentage, name="course_wise_percentage"),
    path("course_per_less_x/", views.course_per_less_x, name="course_wise_students_whose_attendance_is_less_than_x"),
    path("update_registration/",views.update_reg, name="update_course_registration"),
    path("course_registration/",views.view_reg, name="view_course_registration"),
    path("individual_student/",views.individual_student_performance, name="individual_student_performance"),
]