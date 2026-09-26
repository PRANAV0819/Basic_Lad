# config/urls.py
#
# WHAT: Root URL configuration for the entire project.
#
# WHY:  Acts as the master router. Directs requests to:
#       - /signin/admin/        -> Admin login view directly
#       - /adminpanel/          -> Handled by adminpanel/urls.py
#       - /                     -> Handled by core/urls.py

from django.contrib import admin
from django.urls import path, include
from adminpanel import views as admin_views

urlpatterns = [
    # Built-in Django admin (standard)
    path('admin/', admin.site.urls),

    # Direct URL requested: /signin/admin/ -> Admin Login Page
    path('signin/admin/', admin_views.admin_login_view, name='signin_admin'),

    # Admin Panel routes: /adminpanel/login/, /adminpanel/dashboard/, /adminpanel/logout/
    path('adminpanel/', include('adminpanel.urls')),

    # Core landing page routes
    path('', include('core.urls')),
]
