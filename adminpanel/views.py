

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
from django.db.models import Avg, Count
from student.models import Student
from assignments.models import Assignment, Attempt
from student.logic.analytics import (
    calculate_placement_readiness,
    get_all_student_rankings,
    get_student_rank,
    get_student_subject_performance,
    generate_improvement_plan,
)


def admin_dashboard_view(request):
    """
    CHECKPOINT 20: Dynamic Admin Dashboard View.

    Replaces mock numbers with real MySQL metrics:
    - total_students: Actual registered students
    - total_assignments: Total assessments created
    - total_submissions: Total completed student attempts
    - avg_readiness_score: College-wide average placement readiness
    - department_stats: Live department-wise student distribution & readiness
    - upcoming_assignments: Published assignments list
    """
    if not is_admin_logged_in(request):
        return redirect('adminpanel:login')

    username = get_logged_in_admin_username(request)
    now = datetime.datetime.now()

    total_students = Student.objects.count()
    total_assignments = Assignment.objects.count()
    completed_attempts = Attempt.objects.filter(status='COMPLETED')
    total_submissions = completed_attempts.count()

    rankings = get_all_student_rankings()
    if rankings:
        avg_readiness = int(round(sum(r['readiness_score'] for r in rankings) / len(rankings)))
    else:
        avg_readiness = 0

    # Department statistics
    dept_map = {}
    for r in rankings:
        dept = r['department'] or "General / Unassigned"
        if dept not in dept_map:
            dept_map[dept] = {'students': 0, 'total_score': 0}
        dept_map[dept]['students'] += 1
        dept_map[dept]['total_score'] += r['readiness_score']

    dept_stats = []
    for d_name, d_val in dept_map.items():
        avg_s = int(round(d_val['total_score'] / d_val['students'])) if d_val['students'] > 0 else 0
        dept_stats.append({
            'department': d_name,
            'students_count': d_val['students'],
            'avg_score': avg_s,
        })
    dept_stats.sort(key=lambda x: x['avg_score'], reverse=True)

    # Active / published assignments
    upcoming_assignments = Assignment.objects.all().order_by('-created_at')[:4]

    context = {
        'username': username,
        'current_date': now.strftime('%d %B %Y'),
        'current_day': now.strftime('%A'),
        'total_students': total_students,
        'total_assignments': total_assignments,
        'total_submissions': total_submissions,
        'avg_readiness_score': avg_readiness,
        'dept_stats': dept_stats,
        'upcoming_assignments': upcoming_assignments,
    }
    return render(request, 'adminpanel/dashboard.html', context)


def admin_students_view(request):
    """
    CHECKPOINT 21: Student Management View for Admin.
    Lists all students with their PRN, email, department, year, CGPA,
    profile completion %, readiness score, and rank.
    Includes search functionality.
    """
    if not is_admin_logged_in(request):
        return redirect('adminpanel:login')

    search_query = request.GET.get('q', '').strip()
    rankings = get_all_student_rankings()

    if search_query:
        q_lower = search_query.lower()
        rankings = [
            r for r in rankings
            if q_lower in r['name'].lower()
            or q_lower in r['email'].lower()
            or q_lower in r['department'].lower()
        ]

    context = {
        'rankings': rankings,
        'search_query': search_query,
        'total_count': len(rankings),
    }
    return render(request, 'adminpanel/students.html', context)


def admin_student_detail_view(request, student_id: int):
    """
    CHECKPOINT 21: Detailed Student Profile & Performance Inspector.
    """
    if not is_admin_logged_in(request):
        return redirect('adminpanel:login')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return redirect('adminpanel:students')

    readiness = calculate_placement_readiness(student)
    rank_info = get_student_rank(student)
    subject_perf = get_student_subject_performance(student)
    improvement_plan = generate_improvement_plan(student)
    attempts = Attempt.objects.filter(student=student).select_related('assignment').order_by('-started_at')

    context = {
        'student': student,
        'readiness': readiness,
        'rank_info': rank_info,
        'subject_perf': subject_perf,
        'improvement_plan': improvement_plan,
        'attempts': attempts,
    }
    return render(request, 'adminpanel/student_detail.html', context)


def admin_scores_view(request):
    """
    CHECKPOINT 21: Student Assessment Submissions and Scores Inspector.
    """
    if not is_admin_logged_in(request):
        return redirect('adminpanel:login')

    attempts = Attempt.objects.filter(status='COMPLETED').select_related('student', 'assignment').order_by('-submitted_at')

    context = {
        'attempts': attempts,
        'total_attempts': attempts.count(),
    }
    return render(request, 'adminpanel/scores.html', context)


def admin_reports_view(request):
    """
    CHECKPOINT 21: Placement Readiness & TPO Analytics Report.
    """
    if not is_admin_logged_in(request):
        return redirect('adminpanel:login')

    rankings = get_all_student_rankings()
    total_students = len(rankings)

    # Readiness bands
    high_ready = [r for r in rankings if r['readiness_score'] >= 80]
    mod_ready = [r for r in rankings if 60 <= r['readiness_score'] < 80]
    low_ready = [r for r in rankings if r['readiness_score'] < 60]

    # Eligible for Placement Drives (Score >= 70 and CGPA >= 7.0)
    eligible_students = [
        r for r in rankings
        if r['readiness_score'] >= 70 and r['cgpa'] and float(r['cgpa']) >= 7.0
    ]

    context = {
        'total_students': total_students,
        'high_ready_count': len(high_ready),
        'mod_ready_count': len(mod_ready),
        'low_ready_count': len(low_ready),
        'eligible_students': eligible_students,
        'rankings': rankings,
    }
    return render(request, 'adminpanel/reports.html', context)


def admin_logout_view(request):
    logout_admin(request)
    return redirect('core:home')

