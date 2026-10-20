# config/urls.py
#
# WHAT: Root URL configuration for the entire project.
#
# WHY:  Acts as the master router. Directs requests to:
#       - /signin/admin/        -> Admin login view directly
#       - /signin/student/      -> Student login view directly
#       - /adminpanel/          -> Handled by adminpanel/urls.py
#       - /student/             -> Handled by student/urls.py
#       - /                     -> Handled by core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from adminpanel import views as admin_views
from student import views as student_views

urlpatterns = [
    
    # Core landing page routes
    path('', include('core.urls')), 

    # Direct Sign-in shortcuts
    path('signin/admin/', admin_views.admin_login_view, name='signin_admin'),
    path('signin/student/', student_views.student_login_view, name='signin_student'),

    # Admin Panel routes
    path('adminpanel/', include('adminpanel.urls')),

    # Student routes
    path('student/', include('student.urls')),

    # Assignment Module routes
    path('assignments/', include('assignments.urls')),

    # My Portfolio routes
    path('portfolio/', include('myportfolio.urls')),
]

# Serve user uploaded media files (certificates, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
