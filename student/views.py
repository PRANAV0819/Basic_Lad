# student/views.py
#
# WHAT: Views for Student Signup, Login, Dashboard, Profile, and Logout.
#
# WHY:  Handles incoming HTTP requests for student functionality,
#       interfaces with our manual validation & authentication logic,
#       and renders clean templates or manages redirects.

import datetime
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


from .logic.analytics import (
    calculate_placement_readiness,
    get_student_rank,
    get_student_subject_performance,
    get_all_student_rankings,
    generate_improvement_plan,
)
from assignments.models import Assignment, Attempt


def student_dashboard_view(request):
    """
    CHECKPOINT 19: Dynamic Student Dashboard View.

    Replaces all mock values with live aggregated data from MySQL:
    - total_assignments: Live count of published assignments
    - completed_assignments: Count of student's completed attempts
    - avg_score: Real average score percentage across student's attempts
    - readiness_score: Computed using the transparent weighted algorithm
    - rank: Live rank calculated dynamically among all students
    - subject_performance: Live subject-wise scores for bar chart
    - upcoming_assignments: Real unattempted assignments
    - recent_scores: Real recent attempts for the table
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

    # Aggregated queries from MySQL
    published_assignments = Assignment.objects.filter(status='PUBLISHED').order_by('-created_at')
    total_assignments = published_assignments.count()

    completed_attempts = Attempt.objects.filter(
        student=student,
        status='COMPLETED'
    ).select_related('assignment').order_by('-submitted_at')

    completed_count = completed_attempts.count()

    if completed_count > 0:
        avg_score = round(sum(a.percentage for a in completed_attempts) / completed_count, 1)
    else:
        avg_score = 0.0

    # Analytics computations
    readiness_data = calculate_placement_readiness(student)
    rank_data = get_student_rank(student)
    subject_perf = get_student_subject_performance(student)

    # Completed assignment IDs
    completed_ids = completed_attempts.values_list('assignment_id', flat=True)

    # Upcoming / Unattempted assignments (up to 4)
    upcoming_assignments = published_assignments.exclude(id__in=completed_ids)[:4]

    # Recent completed attempts (up to 5)
    recent_scores = completed_attempts[:5]

    context = {
        'student': student,
        'first_name': first_name,
        'initial': initial,
        'current_date': now.strftime('%d %B %Y'),
        'current_day': now.strftime('%A'),
        'total_assignments': total_assignments,
        'completed_assignments': completed_count,
        'avg_score': avg_score,
        'readiness_score': readiness_data['readiness_score'],
        'readiness_band': readiness_data['band'],
        'rank': rank_data['rank'],
        'total_students': rank_data['total_students'],
        'subject_perf': subject_perf,
        'upcoming_assignments': upcoming_assignments,
        'recent_scores': recent_scores,
    }
    return render(request, 'student/dashboard.html', context)


def student_readiness_view(request):
    """
    CHECKPOINTS 14-16, 18: Comprehensive Placement Readiness View.
    Displays detailed mathematical score breakdown, weak area alerts,
    and actionable improvement roadmap.
    """
    if not is_student_logged_in(request):
        return redirect('signin_student')

    student = get_logged_in_student(request)
    if not student:
        logout_student(request)
        return redirect('signin_student')

    readiness = calculate_placement_readiness(student)
    rank_info = get_student_rank(student)
    subject_perf = get_student_subject_performance(student)
    improvement_plan = generate_improvement_plan(student)

    context = {
        'student': student,
        'readiness': readiness,
        'rank_info': rank_info,
        'subject_perf': subject_perf,
        'improvement_plan': improvement_plan,
    }
    return render(request, 'student/readiness.html', context)


def student_rankings_view(request):
    """
    CHECKPOINT 17: College-wide Placement Leaderboard.
    Displays ranked list of students based on Placement Readiness Score.
    """
    if not is_student_logged_in(request):
        return redirect('signin_student')

    student = get_logged_in_student(request)
    if not student:
        logout_student(request)
        return redirect('signin_student')

    rankings = get_all_student_rankings()
    current_rank_info = get_student_rank(student)

    context = {
        'student': student,
        'rankings': rankings,
        'current_rank': current_rank_info['rank'],
        'total_students': current_rank_info['total_students'],
    }
    return render(request, 'student/rankings.html', context)


@require_http_methods(["GET", "POST"])
def student_profile_view(request):
    """
    Student Profile View: view and update personal, academic, and technical details.
    Email is displayed as readonly.
    Includes profile completion percentage breakdown.
    """
    if not is_student_logged_in(request):
        return redirect('signin_student')

    student = get_logged_in_student(request)
    if not student:
        logout_student(request)
        return redirect('signin_student')

    context = {
        'student': student,
        'completion_percentage': student.profile_completion_percentage,
        'error': None,
        'success': None,
    }

    if request.method == 'POST':
        name = request.POST.get('name', '')
        department = request.POST.get('department', '')
        year = request.POST.get('year', '')
        prn = request.POST.get('prn', '')
        cgpa_raw = request.POST.get('cgpa', '')
        skills = request.POST.get('skills', '')
        certifications = request.POST.get('certifications', '')
        projects = request.POST.get('projects', '')
        resume_link = request.POST.get('resume_link', '')
        linkedin_url = request.POST.get('linkedin_url', '')
        github_url = request.POST.get('github_url', '')

        is_valid, error_msg, cleaned_data = validate_student_profile(
            name=name,
            department=department,
            year=year,
            prn=prn,
            cgpa_raw=cgpa_raw,
            skills=skills,
            certifications=certifications,
            projects=projects,
            resume_link=resume_link,
            linkedin_url=linkedin_url,
            github_url=github_url,
        )

        if not is_valid:
            context['error'] = error_msg
        else:
            student.name = cleaned_data['name']
            student.department = cleaned_data['department']
            student.year = cleaned_data['year']
            student.prn = cleaned_data['prn']
            student.cgpa = cleaned_data['cgpa']
            student.skills = cleaned_data['skills']
            student.certifications = cleaned_data['certifications']
            student.projects = cleaned_data['projects']
            student.resume_link = cleaned_data['resume_link']
            student.linkedin_url = cleaned_data['linkedin_url']
            student.github_url = cleaned_data['github_url']
            student.save()

            # Update session stored name
            request.session['student_name'] = student.name
            context['completion_percentage'] = student.profile_completion_percentage
            context['success'] = f"Profile updated successfully! Profile completion is now {student.profile_completion_percentage}%."

    return render(request, 'student/profile.html', context)


def student_logout_view(request):
    """
    Logs out the Student by clearing session keys.
    Redirects back to the public landing page ('core:home').
    """
    logout_student(request)
    return redirect('core:home')
