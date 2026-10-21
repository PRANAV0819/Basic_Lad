
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
    - Full-width subject rows with published assessments, topic summaries, question count, and status.
    - Dynamic Overall Readiness Score card with circular SVG meter.
    - Search field across assessments, subjects, and topics.
    - Direct functional actions: Start Test, Continue Test, View Result, Retake Test.
    """
    student = request.student
    query = request.GET.get('q', '').strip()
    selected_module_code = request.GET.get('module', '').strip()
    now = timezone.now()

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

    # Fetch all student attempts and group by assignment_id
    all_student_attempts = Attempt.objects.filter(student=student).order_by('-started_at')
    attempts_by_assignment = {}
    for att in all_student_attempts:
        if att.assignment_id not in attempts_by_assignment:
            attempts_by_assignment[att.assignment_id] = []
        attempts_by_assignment[att.assignment_id].append(att)

    # Fetch all assessment ReadinessModules with their SubjectCategories
    # (Exclude CGPA & Academic Performance module, which is evaluated directly from student academic records)
    modules_qs = ReadinessModule.objects.exclude(code='ACADEMIC_CGPA').prefetch_related('subjects').order_by('order')
    if selected_module_code:
        modules_qs = modules_qs.filter(code=selected_module_code)

    modules_data = []
    total_published_count = 0
    total_completed_count = 0

    for mod in modules_qs:
        mod_assignments = [a for a in published_assignments_qs if a.module_id == mod.id]

        subject_rows = []
        mod_completed_count = 0
        mod_total_score = 0.0
        mod_max_score = 0

        for subj in mod.subjects.all():
            subj_assignments = [
                a for a in mod_assignments
                if a.subject_category_id == subj.id or (not a.subject_category_id and subj.name.lower() in a.subject.lower())
            ]

            assigned_items = []
            for asgn in subj_assignments:
                total_published_count += 1
                asgn_attempts = attempts_by_assignment.get(asgn.id, [])

                active_attempt = next((att for att in asgn_attempts if att.status == 'IN_PROGRESS'), None)
                completed_attempts = [
                    att for att in asgn_attempts
                    if att.status in ['SUBMITTED', 'AUTO_SUBMITTED', 'COMPLETED']
                ]
                latest_completed = completed_attempts[0] if completed_attempts else None
                attempts_count = len(completed_attempts)

                # Check availability dates
                is_upcoming = bool(asgn.start_date and now < asgn.start_date)
                is_expired = bool(asgn.end_date and now > asgn.end_date)

                can_start = False
                can_resume = False
                can_view_result = False
                can_retake = False

                if active_attempt:
                    status_label = "In Progress"
                    status_class = "status-in-progress"
                    can_resume = True
                elif latest_completed:
                    mod_completed_count += 1
                    total_completed_count += 1
                    mod_total_score += latest_completed.score
                    mod_max_score += asgn.total_marks
                    status_label = f"Score: {latest_completed.score}/{asgn.total_marks} ({round(latest_completed.percentage)}%)"
                    status_class = "status-completed"
                    can_view_result = True
                    if attempts_count < asgn.max_attempts and not is_expired:
                        can_retake = True
                elif is_upcoming:
                    status_label = "Upcoming"
                    status_class = "status-not-started"
                elif is_expired:
                    status_label = "Expired"
                    status_class = "status-not-started"
                else:
                    status_label = "Not Started"
                    status_class = "status-not-started"
                    can_start = True

                assigned_items.append({
                    'assignment': asgn,
                    'question_count': asgn.questions.count(),
                    'active_attempt': active_attempt,
                    'latest_completed': latest_completed,
                    'status_label': status_label,
                    'status_class': status_class,
                    'can_start': can_start,
                    'can_resume': can_resume,
                    'can_view_result': can_view_result,
                    'can_retake': can_retake,
                    'is_upcoming': is_upcoming,
                    'is_expired': is_expired,
                })

            # Check if query matches this subject
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
@require_http_methods(["GET"])
def student_instructions_view(request, assignment_id):
    """
    Step 1 & 2 of Test Workflow:
    Shows comprehensive test guidelines, instructions, rules, scoring criteria,
    and a confirmation prompt before the student initiates the attempt.
    """
    student = request.student
    assignment = get_object_or_404(Assignment, id=assignment_id, status='PUBLISHED')

    now = timezone.now()
    if assignment.start_date and now < assignment.start_date:
        messages.error(request, f"This assessment is not open yet. It begins on {assignment.start_date.strftime('%b %d, %Y at %H:%M')}.")
        return redirect('assignments:student_list')

    if assignment.end_date and now > assignment.end_date:
        messages.error(request, "This assessment deadline has passed and it is no longer open for attempts.")
        return redirect('assignments:student_list')

    # Existing attempts check
    asgn_attempts = Attempt.objects.filter(student=student, assignment=assignment).order_by('-started_at')
    active_attempt = asgn_attempts.filter(status='IN_PROGRESS').first()
    if active_attempt:
        messages.info(request, "You have an active in-progress test. Resuming your session.")
        return redirect('assignments:student_attempt', assignment_id=assignment.id)

    completed_count = asgn_attempts.filter(status__in=['SUBMITTED', 'AUTO_SUBMITTED', 'COMPLETED']).count()
    if completed_count >= assignment.max_attempts:
        messages.warning(request, f"You have reached the maximum allowed attempts ({assignment.max_attempts}) for this test.")
        return redirect('assignments:student_result', assignment_id=assignment.id)

    attempt_number = completed_count + 1

    context = {
        'student': student,
        'assignment': assignment,
        'attempt_number': attempt_number,
        'questions_count': assignment.questions.count(),
    }
    return render(request, 'assignments/student/instructions.html', context)


@student_required
@require_http_methods(["POST"])
def student_start_attempt_view(request, assignment_id):
    """
    Step 3 & 4 of Test Workflow:
    Student confirms starting the test. Creates the database Attempt record,
    sets the server-side started_at and strict deadline, and redirects to test workspace.
    """
    student = request.student
    assignment = get_object_or_404(Assignment, id=assignment_id, status='PUBLISHED')
    now = timezone.now()

    # Check active attempt
    active_attempt = Attempt.objects.filter(
        student=student,
        assignment=assignment,
        status='IN_PROGRESS'
    ).first()
    if active_attempt:
        return redirect('assignments:student_attempt', assignment_id=assignment.id)

    # Check attempt limit
    completed_count = Attempt.objects.filter(
        student=student,
        assignment=assignment,
        status__in=['SUBMITTED', 'AUTO_SUBMITTED', 'COMPLETED']
    ).count()

    if completed_count >= assignment.max_attempts:
        messages.warning(request, "You have completed the maximum permitted attempts.")
        return redirect('assignments:student_result', assignment_id=assignment.id)

    if assignment.questions.count() == 0:
        messages.error(request, "This test does not have any questions yet.")
        return redirect('assignments:student_list')

    # Create new attempt
    started_at = now
    deadline = started_at + timedelta(minutes=assignment.time_limit)
    attempt_number = completed_count + 1

    attempt = Attempt.objects.create(
        student=student,
        assignment=assignment,
        attempt_number=attempt_number,
        started_at=started_at,
        deadline=deadline,
        status='IN_PROGRESS'
    )

    return redirect('assignments:student_attempt', assignment_id=assignment.id)


@student_required
@require_http_methods(["GET"])
def student_attempt_view(request, assignment_id):
    """
    Step 5, 6, 7, 8 of Test Workflow:
    Renders the exam test-taking workspace:
    - Server-side deadline check (auto-submits if time has expired).
    - Countdown timer initialized with server-calculated remaining seconds.
    - Question stream with code snippets, MSQ/MCQ/Numerical inputs.
    - Question palette on right showing answered vs unanswered indicators.
    - Submission confirmation modal.
    """
    student = request.student
    assignment = get_object_or_404(Assignment, id=assignment_id, status='PUBLISHED')

    attempt = Attempt.objects.filter(
        student=student,
        assignment=assignment,
        status='IN_PROGRESS'
    ).first()

    if not attempt:
        # Check if student completed an attempt
        completed_att = Attempt.objects.filter(
            student=student,
            assignment=assignment,
            status__in=['SUBMITTED', 'AUTO_SUBMITTED', 'COMPLETED']
        ).first()
        if completed_att:
            return redirect('assignments:student_result', assignment_id=assignment.id)
        return redirect('assignments:student_instructions', assignment_id=assignment.id)

    # Server-side deadline check: enforce strictly on server
    now = timezone.now()
    if attempt.deadline and now >= attempt.deadline + timedelta(seconds=10):
        # Time expired: auto-submit and redirect to result
        evaluate_attempt(attempt, request.POST, auto_submitted=True)
        messages.warning(request, "Time expired! Your test was automatically submitted by the server.")
        return redirect('assignments:student_result', assignment_id=assignment.id)

    # Calculate remaining time in seconds
    remaining_seconds = 0
    if attempt.deadline:
        remaining_seconds = max(0, int((attempt.deadline - now).total_seconds()))
    else:
        duration_seconds = assignment.time_limit * 60
        elapsed_seconds = int((now - attempt.started_at).total_seconds())
        remaining_seconds = max(0, duration_seconds - elapsed_seconds)

    questions = assignment.questions.prefetch_related('options').order_by('order', 'id')

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
    Step 9 & 10 of Test Workflow:
    Processes the student's test submission:
    - Enforces deadline check (marks auto-submitted if post-deadline).
    - Runs server-side evaluation algorithm.
    - Records score, counts, time taken, and pass/fail.
    - Redirects directly to the result page.
    """
    student = request.student
    assignment = get_object_or_404(Assignment, id=assignment_id)

    attempt = Attempt.objects.filter(
        student=student,
        assignment=assignment,
        status='IN_PROGRESS'
    ).first()

    if not attempt:
        return redirect('assignments:student_list')

    # Check if submission is past server deadline
    now = timezone.now()
    is_auto = False
    if attempt.deadline and now > attempt.deadline + timedelta(seconds=15):
        is_auto = True

    # Evaluate attempt
    evaluate_attempt(attempt, request.POST, auto_submitted=is_auto)

    if is_auto:
        messages.warning(request, "Deadline passed. Your answers were auto-submitted.")
    else:
        messages.success(request, "Test submitted and evaluated successfully!")

    return redirect('assignments:student_result', assignment_id=assignment.id)


@student_required
@require_http_methods(["GET"])
def student_result_view(request, assignment_id):
    """
    Step 11 of Test Workflow:
    Renders detailed score card, pass/fail status, topic breakdown, and solution review:
    - Score, percentage, pass/fail threshold indication.
    - Correct, incorrect, unattempted counts and time taken.
    - Topic-wise performance breakdown.
    - Review of answers and explanations according to administrator's solution-release setting.
    - If retakes are permitted by max_attempts, renders a "Retake Test" action.
    """
    student = request.student
    assignment = get_object_or_404(Assignment, id=assignment_id)

    attempt_id = request.GET.get('attempt_id')
    if attempt_id and attempt_id.isdigit():
        attempt = Attempt.objects.filter(
            id=int(attempt_id),
            student=student,
            assignment=assignment
        ).first()
    else:
        attempt = Attempt.objects.filter(
            student=student,
            assignment=assignment,
            status__in=['SUBMITTED', 'AUTO_SUBMITTED', 'COMPLETED']
        ).order_by('-started_at').first()

    if not attempt:
        messages.error(request, "You have not completed this assessment yet.")
        return redirect('assignments:student_list')

    # Retake policy check
    completed_count = Attempt.objects.filter(
        student=student,
        assignment=assignment,
        status__in=['SUBMITTED', 'AUTO_SUBMITTED', 'COMPLETED']
    ).count()
    can_retake = (completed_count < assignment.max_attempts)

    # Question breakdown
    questions = assignment.questions.prefetch_related('options').order_by('order', 'id')
    student_answers = {
        ans.question_id: ans
        for ans in attempt.answers.prefetch_related('selected_records__option').all()
    }

    breakdown = []
    topic_stats = {}

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

        is_correct = ans.is_correct if ans else False
        marks_obtained = ans.marks_obtained if ans else 0.0

        breakdown.append({
            'question': q,
            'student_answer': ans,
            'is_attempted': len(selected_option_ids) > 0,
            'is_correct': is_correct,
            'marks_obtained': marks_obtained,
            'options': option_states,
        })

        # Topic aggregation
        topic_key = assignment.topic or assignment.subject or "Core Concepts"
        if topic_key not in topic_stats:
            topic_stats[topic_key] = {'total': 0, 'correct': 0, 'marks': 0, 'max_marks': 0}
        topic_stats[topic_key]['total'] += 1
        topic_stats[topic_key]['max_marks'] += q.marks
        if is_correct:
            topic_stats[topic_key]['correct'] += 1
            topic_stats[topic_key]['marks'] += q.marks

    # Topic performance summary
    topic_breakdown = []
    for top_name, stats in topic_stats.items():
        pct = round((stats['marks'] / stats['max_marks'] * 100.0), 1) if stats['max_marks'] > 0 else 0.0
        topic_breakdown.append({
            'name': top_name,
            'total_q': stats['total'],
            'correct_q': stats['correct'],
            'score': stats['marks'],
            'max_score': stats['max_marks'],
            'percentage': pct,
            'is_proficient': pct >= 60.0,
        })

    context = {
        'student': student,
        'assignment': assignment,
        'attempt': attempt,
        'breakdown': breakdown,
        'topic_breakdown': topic_breakdown,
        'time_taken_str': attempt.time_taken_formatted,
        'can_retake': can_retake,
        'completed_count': completed_count,
        'show_solutions': assignment.show_solutions_after_submission,
    }
    return render(request, 'assignments/student/result.html', context)


@student_required
@require_http_methods(["GET"])
def student_results_list_view(request):
    """
    Displays the student's complete historical record of completed tests.
    """
    student = request.student
    attempts = Attempt.objects.filter(
        student=student,
        status__in=['SUBMITTED', 'AUTO_SUBMITTED', 'COMPLETED']
    ).select_related('assignment', 'assignment__module').order_by('-submitted_at')

    context = {
        'student': student,
        'attempts': attempts,
    }
    return render(request, 'assignments/student/results_list.html', context)
