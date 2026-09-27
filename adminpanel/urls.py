# adminpanel/urls.py
#
# WHAT: App-level URL configuration for adminpanel.
#
# WHY:  Keeps routing modular. Every route related to adminpanel
#       is named under the 'adminpanel' namespace:
#       - 'adminpanel:login'
#       - 'adminpanel:dashboard'
#       - 'adminpanel:logout'

from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # /adminpanel/login/
    path('login/', views.admin_login_view, name='login'),

    # /adminpanel/dashboard/
    path('dashboard/', views.admin_dashboard_view, name='dashboard'),

    # /adminpanel/students/
    path('students/', views.admin_students_view, name='students'),

    # /adminpanel/students/<student_id>/
    path('students/<int:student_id>/', views.admin_student_detail_view, name='student_detail'),

    # /adminpanel/scores/
    path('scores/', views.admin_scores_view, name='student_scores'),

    # /adminpanel/reports/
    path('reports/', views.admin_reports_view, name='reports'),

    # /adminpanel/logout/
    path('logout/', views.admin_logout_view, name='logout'),
]
