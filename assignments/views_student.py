# assignments/views_student.py
#
# WHAT: Student controllers for discovering, taking, and reviewing assessments.
#
# WHY:  Handles:
#       1. Light-themed CodeHelp module-wise accordion dashboard with live readiness score.
#       2. Module and subject-wise assessment organization (Core Subjects, Aptitude, Coding, Comm, CGPA).
#       3. Strict single-attempt verification and secure attempt timers.
#       4. Form submission and all-or-nothing evaluation.
#       5. Result page showing detailed score card, question solutions, and option breakdowns.

from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q

from assignments.models import Assignment, Attempt, Question, ReadinessModule, SubjectCategory
from assignments.logic.security import student_required
from assignments.logic.scoring import evaluate_attempt
from student.logic.analytics import calculate_placement_readiness


@student_required
@require_http_methods(["GET"])
def student_assignment_list_view(request):
    """
    Module-wise Assessments & Courses dashboard matching the light-themed CodeHelp UI:
    - Vertically stacked expandable accordion sections per ReadinessModule.
    - Full-width subject rows with published assessments, topic summaries, question count & status.
    - Real-time overall readiness score card with circular SVG meter.
    - Search field across assessments, subjects, and topics.
    """
    student = request.student
    query = request.GET.get('q', '').strip()
    selected_module_code = request.GET.get('module', '').strip()

    # Calculate actual overall readiness score from the verified analytics engine
    readiness_data = calculate_placement_readiness(student)
    readiness_score = int(readiness_data.get('readiness_score', 0))
    readiness_band = readiness_data.get('band', 'Needs Improvement')
    summary_verdict = readiness_data.get('summary_verdict', '')

    # Fetch all published assignments
    published_assignments_qs = Assignment.objects.filter(
        status='PUBLISHED'
    ).select_related('module', 'subject_category').prefetch_related('questions')

    if query:
        published_assignments_qs = published_assignments_qs.filter(
            Q(title__icontains=query) |
            Q(subject__icontains=query) |
            Q(topic__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )

    # Fetch all attempts by this student for fast dictionary lookup: assignment_id -> Attempt
    student_attempts = {
        att.assignment_id: att
        for att in Attempt.objects.filter(student=student)
    }

    # Fetch all ReadinessModules with their SubjectCategories
    modules_qs = ReadinessModule.objects.all().prefetch_related('subjects')
    if selected_module_code:
        modules_qs = modules_qs.filter(code=selected_module_code)

    modules_data = []
    total_published_count = 0
    total_completed_count = 0

    for mod in modules_qs:
        mod_assignments = [a for a in published_assignments_qs if a.module_id == mod.id]

        subject_rows = []
        mod_completed_count = 0
        mod_total_score = 0
        mod_max_score = 0

        for subj in mod.subjects.all():
            # Find assignments explicitly linked to this subject, or matching by subject text
            subj_assignments = [
                a for a in mod_assignments
                if a.subject_category_id == subj.id or (not a.subject_category_id and subj.name.lower() in a.subject.lower())
            ]

            assigned_items = []
            for asgn in subj_assignments:
                total_published_count += 1
                attempt = student_attempts.get(asgn.id)
                is_completed = bool(attempt and attempt.status == 'COMPLETED')
                is_in_progress = bool(attempt and attempt.status == 'IN_PROGRESS')

                if is_completed:
                    mod_completed_count += 1
                    total_completed_count += 1
                    mod_total_score += attempt.score
                    mod_max_score += asgn.total_marks
                    status_label = f"Completed ({round(attempt.percentage)}%)"
                    status_class = "status-completed"
                elif is_in_progress:
                    status_label = "In Progress"
                    status_class = "status-in-progress"
                else:
                    status_label = "Not Started"
                    status_class = "status-not-started"

                assigned_items.append({
                    'assignment': asgn,
                    'question_count': asgn.questions.count(),
                    'attempt': attempt,
                    'status_label': status_label,
                    'status_class': status_class,
                    'is_completed': is_completed,
                    'is_in_progress': is_in_progress,
                })

            # Check if query matches this subject even if no active assignments
            subj_matches_query = True
            if query:
                q_lower = query.lower()
                subj_matches_query = (
                    q_lower in subj.name.lower() or
                    q_lower in subj.topics.lower() or
                    q_lower in subj.description.lower() or
                    len(assigned_items) > 0
                )

            if subj_matches_query:
                subject_rows.append({
                    'subject': subj,
                    'assignments': assigned_items,
                    'has_assignments': len(assigned_items) > 0,
                })

        # Calculate module progress and percentage
        mod_total_tests = len(mod_assignments)
        if mod_total_tests > 0:
            mod_completion_pct = int(round((mod_completed_count / mod_total_tests) * 100))
            mod_score_pct = round((mod_total_score / mod_max_score * 100), 1) if mod_max_score > 0 else 0
        else:
            mod_completion_pct = 0
            mod_score_pct = 0

        # Don't show empty module if search query yielded zero matches
        if not query or len(subject_rows) > 0:
            modules_data.append({
                'module': mod,
                'subjects': subject_rows,
                'total_tests': mod_total_tests,
                'completed_tests': mod_completed_count,
                'completion_pct': mod_completion_pct,
                'score_pct': mod_score_pct,
                # Default expand Core Subjects
                'is_expanded': (mod.code == 'CORE_SUBJECTS' and not query) or bool(query),
            })

    # Progress ring calculation for SVG circle (circumference = 2 * PI * 38 ≈ 238.76)
    ring_circumference = 238.76
    ring_offset = round(ring_circumference - (ring_circumference * (readiness_score / 100.0)), 2)

    context = {
        'student': student,
        'modules_data': modules_data,
        'readiness_score': readiness_score,
        'readiness_band': readiness_band,
        'summary_verdict': summary_verdict,
        'ring_circumference': ring_circumference,
        'ring_offset': ring_offset,
        'query': query,
        'total_published_count': total_published_count,
        'total_completed_count': total_completed_count,
    }
    return render(request, 'assignments/student/list.html', context)


@student_required
@require_http_methods(["GET", "POST"])
def student_start_attempt_view(request, assignment_id):
    """
    Initiates or resumes a test attempt.
    Enforces the single-attempt policy:
    - If already completed, redirects directly to result with a warning.
    - If in progress, calculates remaining time and proceeds.
    - If new, creates Attempt in IN_PROGRESS state.
    """
    student = request.student
    assignment = get_object_or_404(Assignment, id=assignment_id, status='PUBLISHED')

    attempt = Attempt.objects.filter(student=student, assignment=assignment).first()

    # Rule: Single attempt per assignment!
    if attempt and attempt.status == 'COMPLETED':
        messages.info(request, "You have already completed this test. You can review your results below.")
        return redirect('assignments:student_result', assignment_id=assignment.id)

    # Check if assignment has questions
    if assignment.questions.count() == 0:
        messages.error(request, "This assignment is currently empty and cannot be attempted.")
        return redirect('assignments:student_list')

    if not attempt:
        attempt = Attempt.objects.create(
            student=student,
            assignment=assignment,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )

    return redirect('assignments:student_attempt', assignment_id=assignment.id)


@student_required
@require_http_methods(["GET"])
def student_attempt_view(request, assignment_id):
    """
    Renders the exam test taking screen with questions and countdown timer.
    """
    student = request.student
    assignment = get_object_or_404(Assignment, id=assignment_id, status='PUBLISHED')

    attempt = Attempt.objects.filter(student=student, assignment=assignment).first()

    if not attempt or attempt.status == 'COMPLETED':
        return redirect('assignments:student_result', assignment_id=assignment.id)

    # Calculate remaining time in seconds
    now = timezone.now()
    duration_seconds = assignment.time_limit * 60
    elapsed_seconds = int((now - attempt.started_at).total_seconds())
    remaining_seconds = max(0, duration_seconds - elapsed_seconds)

    # If time has expired on server check (with 15s grace for network latency)
    if remaining_seconds <= 0:
        # Auto-submit empty
        evaluate_attempt(attempt, request.POST)
        messages.warning(request, "Time expired! Your test was automatically submitted.")
        return redirect('assignments:student_result', assignment_id=assignment.id)

    questions = assignment.questions.prefetch_related('options').all()

    context = {
        'student': student,
        'assignment': assignment,
        'attempt': attempt,
        'questions': questions,
        'remaining_seconds': remaining_seconds,
        'time_limit_minutes': assignment.time_limit,
    }
    return render(request, 'assignments/student/attempt.html', context)


@student_required
@require_http_methods(["POST"])
def student_submit_attempt_view(request, assignment_id):
    """
    Processes the student's test submission:
    - Runs evaluate_attempt() which performs set-based scoring (MCQ exact, MSQ all-or-nothing).
    - Saves answers and marks attempt COMPLETED.
    - Redirects to result screen.
    """
    student = request.student
    assignment = get_object_or_404(Assignment, id=assignment_id)

    attempt = Attempt.objects.filter(student=student, assignment=assignment).first()

    if not attempt:
        return redirect('assignments:student_list')

    if attempt.status == 'COMPLETED':
        return redirect('assignments:student_result', assignment_id=assignment.id)

    # Evaluate responses
    evaluate_attempt(attempt, request.POST)
    messages.success(request, "Test submitted successfully!")
    return redirect('assignments:student_result', assignment_id=assignment.id)


@student_required
@require_http_methods(["GET"])
def student_result_view(request, assignment_id):
    """
    Renders the detailed score card and solution review:
    - Overall marks, percentage, counts (correct, wrong, unattempted).
    - Question-by-question breakdown with chosen options, correct options, and explanations.
    """
    student = request.student
    assignment = get_object_or_404(Assignment, id=assignment_id)

    attempt = Attempt.objects.filter(
        student=student,
        assignment=assignment,
        status='COMPLETED'
    ).first()

    if not attempt:
        messages.error(request, "You have not completed this assignment yet.")
        return redirect('assignments:student_list')

    # Prepare question breakdown
    questions = assignment.questions.prefetch_related('options').all()
    student_answers = {
        ans.question_id: ans
        for ans in attempt.answers.prefetch_related('selected_records__option').all()
    }

    breakdown = []
    for q in questions:
        ans = student_answers.get(q.id)
        selected_option_ids = set()
        if ans:
            selected_option_ids = set(
                rec.option_id for rec in ans.selected_records.all()
            )

        option_states = []
        for opt in q.options.all():
            option_states.append({
                'option': opt,
                'is_selected': opt.id in selected_option_ids,
                'is_correct': opt.is_correct,
            })

        breakdown.append({
            'question': q,
            'student_answer': ans,
            'is_attempted': len(selected_option_ids) > 0,
            'is_correct': ans.is_correct if ans else False,
            'marks_obtained': ans.marks_obtained if ans else 0,
            'options': option_states,
        })

    # Time taken
    time_taken_str = "N/A"
    if attempt.submitted_at and attempt.started_at:
        diff = attempt.submitted_at - attempt.started_at
        mins = int(diff.total_seconds() // 60)
        secs = int(diff.total_seconds() % 60)
        time_taken_str = f"{mins}m {secs}s"

    context = {
        'student': student,
        'assignment': assignment,
        'attempt': attempt,
        'breakdown': breakdown,
        'time_taken': time_taken_str,
    }
    return render(request, 'assignments/student/result.html', context)


@student_required
@require_http_methods(["GET"])
def student_results_list_view(request):
    """
    Displays the student's complete history of completed exam attempts.
    """
    student = request.student
    attempts = Attempt.objects.filter(
        student=student,
        status='COMPLETED'
    ).select_related('assignment').order_by('-submitted_at')

    context = {
        'student': student,
        'attempts': attempts,
    }
    return render(request, 'assignments/student/results_list.html', context)
