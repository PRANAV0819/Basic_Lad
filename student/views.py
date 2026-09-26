# student/views.py
#
# WHAT: Views for Student Signup, Login, Dashboard, Profile, and Logout.
#
# WHY:  Handles incoming HTTP requests for student functionality,
#       interfaces with our manual validation & authentication logic,
#       and renders clean templates or manages redirects.

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from adminpanel.logic.password import generate_salt, hash_password
from student.models import Student
from .logic.validation import (
    validate_student_signup,
    validate_student_profile,
)
from .logic.authentication import (
    authenticate_student,
    login_student,
    logout_student,
    is_student_logged_in,
    get_logged_in_student,
)


@require_http_methods(["GET", "POST"])
def student_signup_view(request):
    """
    Handles Student Registration.

    GET:
    - If already logged in, redirect directly to Student Dashboard.
    - Otherwise, render signup form.

    POST:
    - Validate name, email, password matching, and duplicate email.
    - If validation fails, return clear error message with input retained.
    - If valid, generate random salt, hash password using custom algorithm,
      save to MySQL, and redirect to Student Login with a success notice.
    """
    if is_student_logged_in(request):
        return redirect('student:dashboard')

    context = {
        'error': None,
        'form_data': {},
    }

    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        department = request.POST.get('department', '')
        year = request.POST.get('year', '')

        is_valid, error_msg, cleaned_data = validate_student_signup(
            name, email, password, confirm_password, department, year
        )

        if not is_valid:
            context['error'] = error_msg
            context['form_data'] = cleaned_data
            return render(request, 'student/signup.html', context)

        # Generate salt using reused standard library secrets generator
        salt = generate_salt()

        # Compute hash using our reused custom teaching algorithm
        password_hash = hash_password(cleaned_data['password'], salt)

        # Save student record to MySQL
        try:
            Student.objects.create(
                name=cleaned_data['name'],
                email=cleaned_data['email'],
                password_hash=password_hash,
                salt=salt,
                department=cleaned_data['department'],
                year=cleaned_data['year'],
            )
            # Redirect to login with success flag
            return redirect('/signin/student/?registered=1')
        except Exception as e:
            context['error'] = "Failed to create account due to a database error. Please try again."
            context['form_data'] = cleaned_data
            return render(request, 'student/signup.html', context)

    return render(request, 'student/signup.html', context)


@require_http_methods(["GET", "POST"])
def student_login_view(request):
    """
    Handles Student Login.

    GET:
    - If already logged in, redirect to Student Dashboard.
    - Displays success banner if redirected from successful signup (?registered=1).
    - Otherwise renders login form.

    POST:
    - Validates email & password using custom authentication logic.
    - If authenticated, establishes student session and redirects to dashboard.
    - If incorrect, displays generic 'Invalid email or password' error.
    """
    if is_student_logged_in(request):
        return redirect('student:dashboard')

    context = {
        'error': None,
        'success': None,
        'email': '',
    }

    if request.GET.get('registered') == '1':
        context['success'] = "Account created successfully! Please log in with your credentials."

    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        is_auth, error_msg, student = authenticate_student(email, password)

        if is_auth:
            login_student(request, student)
            return redirect('student:dashboard')
        else:
            context['error'] = error_msg
            context['email'] = email.strip()

    return render(request, 'student/login.html', context)


import datetime


def student_dashboard_view(request):
    """
    Protected Student Dashboard view.

    ACCESS CONTROL:
    - Checks whether 'is_student_logged_in(request)' is True.
    - If not, redirects to the student login page.
    """
    if not is_student_logged_in(request):
        return redirect('signin_student')

    student = get_logged_in_student(request)
    if not student:
        logout_student(request)
        return redirect('signin_student')

    now = datetime.datetime.now()
    first_name = student.name.strip().split()[0] if student.name.strip() else "Student"
    initial = student.name.strip()[0].upper() if student.name.strip() else "S"

    context = {
        'student': student,
        'first_name': first_name,
        'initial': initial,
        'current_date': now.strftime('%d %B %Y'),
        'current_day': now.strftime('%A'),
        'total_assignments': 8,
        'completed_assignments': 5,
        'avg_score': 72,
        'readiness_score': 68,
        'rank': 32,
        'total_students': 128,
    }
    return render(request, 'student/dashboard.html', context)


@require_http_methods(["GET", "POST"])
def student_profile_view(request):
    """
    Student Profile View: view and update Name, Department, and Year.
    Email is displayed as readonly.
    """
    if not is_student_logged_in(request):
        return redirect('signin_student')

    student = get_logged_in_student(request)
    if not student:
        logout_student(request)
        return redirect('signin_student')

    context = {
        'student': student,
        'error': None,
        'success': None,
    }

    if request.method == 'POST':
        name = request.POST.get('name', '')
        department = request.POST.get('department', '')
        year = request.POST.get('year', '')

        is_valid, error_msg, cleaned_data = validate_student_profile(name, department, year)

        if not is_valid:
            context['error'] = error_msg
        else:
            student.name = cleaned_data['name']
            student.department = cleaned_data['department']
            student.year = cleaned_data['year']
            student.save()

            # Update session stored name
            request.session['student_name'] = student.name
            context['success'] = "Profile updated successfully!"

    return render(request, 'student/profile.html', context)


def student_logout_view(request):
    """
    Logs out the Student by clearing session keys.
    Redirects back to the public landing page ('core:home').
    """
    logout_student(request)
    return redirect('core:home')
