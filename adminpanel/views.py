# adminpanel/views.py
#
# WHAT: View functions for the Admin panel: Login, Dashboard, and Logout.
#
# WHY:  Views receive the incoming HttpRequest, call our custom authentication
#       and session logic, and return appropriate HttpResponses (render template or redirect).
#
# WHERE: adminpanel/views.py
#
# HOW IT COMMUNICATES:
#       Browser (POST form)
#       → config/urls.py
#       → adminpanel/urls.py
#       → admin_login_view()
#       → adminpanel/logic/authentication.py (validates and checks password against MySQL)
#       → sets session in request.session
#       → redirect to admin_dashboard_view()
#       → renders dashboard.html

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .logic.authentication import (
    authenticate_admin,
    login_admin,
    logout_admin,
    is_admin_logged_in,
    get_logged_in_admin_username,
)


@require_http_methods(["GET", "POST"])
def admin_login_view(request):
    """
    Handles displaying the Admin Login page (GET) and processing
    the submitted credentials (POST).

    GET:
    - If already logged in, redirects directly to the dashboard.
    - Otherwise, renders the clean login template.

    POST:
    - Extracts username and password from request.POST.
    - Calls our custom authenticate_admin() algorithm.
    - On success: establishes session and redirects to dashboard.
    - On failure: re-renders login template with error message.
    """
    # If the admin is already logged in, don't show the login form again
    if is_admin_logged_in(request):
        return redirect('adminpanel:dashboard')

    context = {
        'error': None,
        'username': '',
    }

    if request.method == 'POST':
        # Retrieve form data submitted by HTML form
        username_input = request.POST.get('username', '')
        password_input = request.POST.get('password', '')

        # Execute our manual authentication logic
        is_authenticated, error_message, admin_instance = authenticate_admin(
            username_input, password_input
        )

        if is_authenticated:
            # Create our custom login state in the session
            login_admin(request, admin_instance)
            # Redirect to the Admin Dashboard URL
            return redirect('adminpanel:dashboard')
        else:
            # Login failed: provide generic error message and retain username for convenience
            context['error'] = error_message
            context['username'] = username_input.strip()

    return render(request, 'adminpanel/login.html', context)


import datetime


def admin_dashboard_view(request):
    """
    Protected Admin Dashboard view.

    ACCESS CONTROL:
    - Checks whether 'is_admin_logged_in(request)' is True.
    - If NOT authenticated: immediately redirects to the Admin Login page.
      This prevents unauthorized access to '/adminpanel/dashboard/'.
    - If authenticated: retrieves the admin username from session and renders the dashboard.
    """
    if not is_admin_logged_in(request):
        # Unauthorized attempt: redirect to login
        return redirect('adminpanel:login')

    username = get_logged_in_admin_username(request)
    now = datetime.datetime.now()

    context = {
        'username': username,
        'current_date': now.strftime('%d %B %Y'),
        'current_day': now.strftime('%A'),
        'total_students': 128,
        'total_assignments': 15,
        'total_submissions': 342,
        'avg_readiness_score': 68,
    }
    return render(request, 'adminpanel/dashboard.html', context)


def admin_logout_view(request):
    logout_admin(request)
    return redirect('core:home')
