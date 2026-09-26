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

    # /adminpanel/logout/
    path('logout/', views.admin_logout_view, name='logout'),
]
