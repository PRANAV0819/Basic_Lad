# core/urls.py
#
# WHAT: This file defines the URL patterns (routes) that belong
#       specifically to the "core" app.
#
# WHY:  Django encourages keeping URL patterns modular — each app
#       owns its own urls.py. This keeps things organised and makes
#       the app reusable. The project-level config/urls.py then
#       "includes" this file rather than defining every URL in one place.
#
# WHERE: This file lives at core/urls.py.
#        Django does NOT auto-discover it — you must include it
#        explicitly from config/urls.py using include().
#
# HOW Django uses it:
#       1. config/urls.py has: path('', include('core.urls'))
#       2. Django loads this file and checks its urlpatterns list
#       3. If a request URL matches a pattern here, Django calls
#          the associated view function


from django.urls import path
from . import views          # import views from the same app (core)

# `app_name` sets the "namespace" for this app's URLs.
# Later, you can refer to this URL as 'core:home' in templates
# using {% url 'core:home' %} — much cleaner than hardcoding '/'.
app_name = 'core'

urlpatterns = [
    # path('', view_function, name='route_name')
    #
    # '' means the root URL: http://localhost:8000/
    # views.home_view is the function to call when this URL is matched
    # name='home' lets us refer to this URL by name in templates
    path('', views.home_view, name='home'),
]
