# student/urls.py
#
# WHAT: App-level URL configuration for student module.
#
# WHY:  Keeps routes namespaced under 'student':
#       - student:signup
#       - student:dashboard
#       - student:profile
#       - student:logout

from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    # /student/signup/
    path('signup/', views.student_signup_view, name='signup'),

    # /student/dashboard/
    path('dashboard/', views.student_dashboard_view, name='dashboard'),

    # /student/profile/
    path('profile/', views.student_profile_view, name='profile'),

    # /student/readiness/
    path('readiness/', views.student_readiness_view, name='readiness'),

    # /student/rankings/
    path('rankings/', views.student_rankings_view, name='rankings'),

    # /student/logout/
    path('logout/', views.student_logout_view, name='logout'),
]
