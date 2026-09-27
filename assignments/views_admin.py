# assignments/views_admin.py
#
# WHAT: Admin controllers for managing assignments, questions, and viewing scores.
#
# WHY:  Admins must be able to:
#       1. List all assignments (filtered by Final vs Subject-wise Exam, and Status).
#       2. Create new assignments in DRAFT status.
#       3. Add MCQ / MSQ questions with options and designated correct choices.
#       4. Publish or Close assignments.
#       5. View class performance and individual student submissions.

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Count, Avg

from assignments.models import Assignment, Question, QuestionOption, Attempt
from assignments.logic.security import admin_required


@admin_required
@require_http_methods(["GET"])
def admin_assignment_list_view(request):
    """
    Displays the catalog of all assignments created by the Admin,
    with filter options (Final vs Subject-wise, Status) and metrics.
    """
    exam_filter = request.GET.get('exam_type', 'ALL')
    status_filter = request.GET.get('status', 'ALL')

    assignments = Assignment.objects.annotate(
        num_questions=Count('questions', distinct=True),
        num_attempts=Count('attempts', distinct=True)
    )

    if exam_filter in ['FINAL', 'SUBJECT']:
        assignments = assignments.filter(exam_type=exam_filter)

    if status_filter in ['DRAFT', 'PUBLISHED', 'CLOSED']:
        assignments = assignments.filter(status=status_filter)

    # Summary metrics for quick glance
    total_count = Assignment.objects.count()
    published_count = Assignment.objects.filter(status='PUBLISHED').count()
    draft_count = Assignment.objects.filter(status='DRAFT').count()
    total_attempts = Attempt.objects.filter(status='COMPLETED').count()

    context = {
        'assignments': assignments,
        'exam_filter': exam_filter,
        'status_filter': status_filter,
        'total_count': total_count,
        'published_count': published_count,
        'draft_count': draft_count,
        'total_attempts': total_attempts,
    }
    return render(request, 'assignments/admin/list.html', context)


@admin_required
@require_http_methods(["GET", "POST"])
def admin_assignment_create_view(request):
    """
    Creates a new Assignment record in DRAFT mode.
    On success, redirects directly to question authoring.
    """
    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        exam_type = request.POST.get('exam_type', 'SUBJECT')
        subject = request.POST.get('subject', '').strip()
        topic = request.POST.get('topic', '').strip()
        time_limit_str = request.POST.get('time_limit', '30').strip()
        description = request.POST.get('description', '').strip()

        # Validation
        errors = []
        if not title:
            errors.append("Assignment title is required.")
        if not subject:
            errors.append("Subject name is required.")
        try:
            time_limit = int(time_limit_str)
            if time_limit < 1:
                errors.append("Time limit must be at least 1 minute.")
        except ValueError:
            errors.append("Time limit must be a valid integer.")
            time_limit = 30

        if errors:
            return render(request, 'assignments/admin/create.html', {
                'errors': errors,
                'form_data': request.POST
            })

        assignment = Assignment.objects.create(
            title=title,
            exam_type=exam_type,
            subject=subject,
            topic=topic,
            time_limit=time_limit,
            description=description,
            status='DRAFT'
        )

        return redirect('assignments:admin_questions', assignment_id=assignment.id)

    return render(request, 'assignments/admin/create.html')


@admin_required
@require_http_methods(["GET", "POST"])
def admin_assignment_edit_view(request, assignment_id):
    """
    Allows editing an existing assignment's metadata.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        exam_type = request.POST.get('exam_type', 'SUBJECT')
        subject = request.POST.get('subject', '').strip()
        topic = request.POST.get('topic', '').strip()
        time_limit_str = request.POST.get('time_limit', '30').strip()
        description = request.POST.get('description', '').strip()

        errors = []
        if not title:
            errors.append("Assignment title is required.")
        if not subject:
            errors.append("Subject name is required.")
        try:
            time_limit = int(time_limit_str)
            if time_limit < 1:
                errors.append("Time limit must be at least 1 minute.")
        except ValueError:
            errors.append("Time limit must be a valid integer.")
            time_limit = 30

        if errors:
            return render(request, 'assignments/admin/edit.html', {
                'assignment': assignment,
                'errors': errors,
            })

        assignment.title = title
        assignment.exam_type = exam_type
        assignment.subject = subject
        assignment.topic = topic
        assignment.time_limit = time_limit
        assignment.description = description
        assignment.save()

        return redirect('assignments:admin_list')

    return render(request, 'assignments/admin/edit.html', {'assignment': assignment})


@admin_required
@require_http_methods(["POST"])
def admin_assignment_status_toggle_view(request, assignment_id):
    """
    Toggles assignment status between DRAFT, PUBLISHED, and CLOSED.
    Validates that an assignment has questions before publishing.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    new_status = request.POST.get('status')

    if new_status in ['DRAFT', 'PUBLISHED', 'CLOSED']:
        if new_status == 'PUBLISHED' and assignment.questions.count() == 0:
            messages.error(request, "Cannot publish an assignment with zero questions. Please add questions first.")
        else:
            assignment.status = new_status
            assignment.save()
            messages.success(request, f"Assignment status updated to {assignment.get_status_display()}.")

    return redirect(request.META.get('HTTP_REFERER', 'assignments:admin_list'))


@admin_required
@require_http_methods(["GET", "POST"])
def admin_assignment_questions_view(request, assignment_id):
    """
    Manages questions and options for a specific assignment:
    - Lists existing questions with options and correct indicators.
    - POST: Adds a new MCQ or MSQ question with options A, B, C, D.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    questions = assignment.questions.prefetch_related('options').all()

    errors = []
    if request.method == "POST":
        question_text = request.POST.get('question_text', '').strip()
        question_type = request.POST.get('question_type', 'MCQ')
        marks_str = request.POST.get('marks', '1').strip()
        solution = request.POST.get('solution', '').strip()

        # Options A, B, C, D
        opt_a = request.POST.get('opt_a', '').strip()
        opt_b = request.POST.get('opt_b', '').strip()
        opt_c = request.POST.get('opt_c', '').strip()
        opt_d = request.POST.get('opt_d', '').strip()

        correct_options = request.POST.getlist('correct_options')  # list of 'A', 'B', etc.

        # Validation
        if not question_text:
            errors.append("Question statement is required.")
        try:
            marks = int(marks_str)
            if marks < 1:
                errors.append("Marks must be at least 1.")
        except ValueError:
            errors.append("Marks must be a positive integer.")
            marks = 1

        if not opt_a or not opt_b:
            errors.append("At least Option A and Option B must be provided.")

        if not correct_options:
            errors.append("Please designate at least one correct option.")
        elif question_type == 'MCQ' and len(correct_options) > 1:
            errors.append("MCQ (Single Choice) questions can only have ONE correct option.")

        if not errors:
            next_order = (assignment.questions.count() or 0) + 1
            question = Question.objects.create(
                assignment=assignment,
                question_text=question_text,
                question_type=question_type,
                marks=marks,
                solution=solution,
                order=next_order
            )

            # Create options
            options_data = [
                ('A', opt_a, 'A' in correct_options),
                ('B', opt_b, 'B' in correct_options),
            ]
            if opt_c:
                options_data.append(('C', opt_c, 'C' in correct_options))
            if opt_d:
                options_data.append(('D', opt_d, 'D' in correct_options))

            for label, text, is_corr in options_data:
                QuestionOption.objects.create(
                    question=question,
                    option_label=label,
                    option_text=text,
                    is_correct=is_corr
                )

            # Recalculate assignment total marks
            assignment.recalculate_total_marks()
            messages.success(request, f"Question Q{question.order} added successfully!")
            return redirect('assignments:admin_questions', assignment_id=assignment.id)

    return render(request, 'assignments/admin/questions.html', {
        'assignment': assignment,
        'questions': questions,
        'errors': errors,
        'form_data': request.POST if request.method == "POST" else None
    })


@admin_required
@require_http_methods(["POST"])
def admin_question_delete_view(request, assignment_id, question_id):
    """
    Deletes a specific question and updates assignment total marks.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    question = get_object_or_404(Question, id=question_id, assignment=assignment)
    question.delete()

    # Re-order remaining questions
    for idx, q in enumerate(assignment.questions.all(), start=1):
        q.order = idx
        q.save(update_fields=['order'])

    assignment.recalculate_total_marks()
    messages.success(request, "Question deleted successfully.")
    return redirect('assignments:admin_questions', assignment_id=assignment.id)


@admin_required
@require_http_methods(["GET"])
def admin_assignment_submissions_view(request, assignment_id):
    """
    Displays all student attempts and scores for a specific assignment.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    attempts = Attempt.objects.filter(assignment=assignment).select_related('student').order_by('-score', '-submitted_at')

    # Aggregates
    completed_attempts = attempts.filter(status='COMPLETED')
    avg_score = completed_attempts.aggregate(Avg('score'))['score__avg'] or 0.0
    avg_percentage = completed_attempts.aggregate(Avg('percentage'))['percentage__avg'] or 0.0

    return render(request, 'assignments/admin/submissions.html', {
        'assignment': assignment,
        'attempts': attempts,
        'completed_count': completed_attempts.count(),
        'avg_score': round(avg_score, 1),
        'avg_percentage': round(avg_percentage, 1),
    })
