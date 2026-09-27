# assignments/urls.py
#
# WHAT: URL routing for the Assignment Module (Admin & Student endpoints).
#
# WHY:  Maps browser HTTP requests to the corresponding views in:
#       - assignments/views_admin.py
#       - assignments/views_student.py

from django.urls import path
from . import views_admin, views_student

app_name = 'assignments'

urlpatterns = [
    # ==================== ADMIN ENDPOINTS ====================
    path('admin/', views_admin.admin_assignment_list_view, name='admin_list'),
    path('admin/create/', views_admin.admin_assignment_create_view, name='admin_create'),
    path('admin/<int:assignment_id>/edit/', views_admin.admin_assignment_edit_view, name='admin_edit'),
    path('admin/<int:assignment_id>/status/', views_admin.admin_assignment_status_toggle_view, name='admin_status_toggle'),
    path('admin/<int:assignment_id>/questions/', views_admin.admin_assignment_questions_view, name='admin_questions'),
    path('admin/<int:assignment_id>/questions/<int:question_id>/delete/', views_admin.admin_question_delete_view, name='admin_question_delete'),
    path('admin/<int:assignment_id>/submissions/', views_admin.admin_assignment_submissions_view, name='admin_submissions'),

    # ==================== STUDENT ENDPOINTS ====================
    path('', views_student.student_assignment_list_view, name='root'),
    path('student/', views_student.student_assignment_list_view, name='student_list'),
    path('student/<int:assignment_id>/start/', views_student.student_start_attempt_view, name='student_start'),
    path('student/<int:assignment_id>/attempt/', views_student.student_attempt_view, name='student_attempt'),
    path('student/<int:assignment_id>/submit/', views_student.student_submit_attempt_view, name='student_submit'),
    path('student/<int:assignment_id>/result/', views_student.student_result_view, name='student_result'),
    path('results/', views_student.student_results_list_view, name='results_alias'),
    path('student/results/', views_student.student_results_list_view, name='student_results_list'),
]
