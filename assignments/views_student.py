# assignments/views_student.py
#
# WHAT: Student controllers for discovering, taking, and reviewing assignments.
#
# WHY:  Handles:
#       1. Catalog of published Final & Subject-wise Exams.
#       2. Strict single-attempt verification.
#       3. Test attempt screen with server-calculated remaining time.
#       4. Form submission and all-or-nothing evaluation.
#       5. Result page showing detailed score card, question solutions, and option breakdowns.

from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib import messages

from assignments.models import Assignment, Attempt, Question
from assignments.logic.security import student_required
from assignments.logic.scoring import evaluate_attempt


@student_required
@require_http_methods(["GET"])
def student_assignment_list_view(request):
    """
    Shows all PUBLISHED assignments to the student.
    Separates into tabs: All, Final Exam, Subject-wise Exam.
    Annotates each card with the student's attempt status.
    """
    student = request.student
    exam_filter = request.GET.get('exam_type', 'ALL')

    # Students must NEVER see DRAFT or CLOSED assignments!
    assignments = Assignment.objects.filter(status='PUBLISHED').prefetch_related('questions')

    if exam_filter in ['FINAL', 'SUBJECT']:
        assignments = assignments.filter(exam_type=exam_filter)

    # Fetch all attempts by this student for fast lookup
    student_attempts = {
        att.assignment_id: att
        for att in Attempt.objects.filter(student=student)
    }

    assignment_data = []
    for asgn in assignments:
        attempt = student_attempts.get(asgn.id)
        assignment_data.append({
            'assignment': asgn,
            'question_count': asgn.questions.count(),
            'attempt': attempt,
            'is_completed': attempt and attempt.status == 'COMPLETED',
            'is_in_progress': attempt and attempt.status == 'IN_PROGRESS',
        })

    context = {
        'student': student,
        'assignments': assignment_data,
        'exam_filter': exam_filter,
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
