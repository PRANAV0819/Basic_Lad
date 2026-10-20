# assignments/views_admin.py
#
# WHAT: Admin controllers for managing assignments, questions, and viewing scores.
#
# WHY:  Admins must be able to:
#       1. List all assignments (filtered by Module, Subject, Exam Type, Status, and Search).
#       2. Create new assignments in DRAFT or PUBLISHED status with full module & subject assignment.
#       3. Add MCQ / MSQ / Code Tracing questions with code snippets, options, and designated correct choices.
#       4. Publish or Close assignments.
#       5. View class performance and individual student submissions.

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.db import transaction

from assignments.models import (
    Assignment,
    Question,
    QuestionOption,
    Attempt,
    ReadinessModule,
    SubjectCategory,
)
from assignments.logic.security import admin_required


@admin_required
@require_http_methods(["GET"])
def admin_assignment_list_view(request):
    """
    Displays the catalog of all assignments created by the Admin,
    with filter options (Module, Subject, Final vs Subject-wise, Status, Search) and metrics.
    """
    exam_filter = request.GET.get('exam_type', 'ALL')
    status_filter = request.GET.get('status', 'ALL')
    module_filter = request.GET.get('module_id', 'ALL')
    subject_filter = request.GET.get('subject_category_id', 'ALL')
    search_query = request.GET.get('q', '').strip()

    assignments = Assignment.objects.select_related('module', 'subject_category').annotate(
        num_questions=Count('questions', distinct=True),
        num_attempts=Count('attempts', distinct=True)
    )

    if exam_filter in ['FINAL', 'SUBJECT']:
        assignments = assignments.filter(exam_type=exam_filter)

    if status_filter in ['DRAFT', 'PUBLISHED', 'CLOSED']:
        assignments = assignments.filter(status=status_filter)

    if module_filter != 'ALL' and module_filter.isdigit():
        assignments = assignments.filter(module_id=int(module_filter))

    if subject_filter != 'ALL' and subject_filter.isdigit():
        assignments = assignments.filter(subject_category_id=int(subject_filter))

    if search_query:
        assignments = assignments.filter(
            Q(title__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(topic__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    # Summary metrics for quick glance
    total_count = Assignment.objects.count()
    published_count = Assignment.objects.filter(status='PUBLISHED').count()
    draft_count = Assignment.objects.filter(status='DRAFT').count()
    total_attempts = Attempt.objects.filter(status='COMPLETED').count()

    modules = ReadinessModule.objects.all().prefetch_related('subjects')

    context = {
        'assignments': assignments,
        'modules': modules,
        'exam_filter': exam_filter,
        'status_filter': status_filter,
        'module_filter': module_filter,
        'subject_filter': subject_filter,
        'search_query': search_query,
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
    Creates a new Assignment record in DRAFT mode with module and subject mapping.
    On success, redirects directly to question authoring.
    """
    modules = ReadinessModule.objects.all().prefetch_related('subjects')
    subject_categories = SubjectCategory.objects.all().select_related('module')

    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        exam_type = request.POST.get('exam_type', 'SUBJECT')
        module_id = request.POST.get('module_id', '').strip()
        subject_category_id = request.POST.get('subject_category_id', '').strip()
        subject = request.POST.get('subject', '').strip()
        topic = request.POST.get('topic', '').strip()
        difficulty = request.POST.get('difficulty', 'MEDIUM').strip()
        time_limit_str = request.POST.get('time_limit', '30').strip()
        negative_marking_str = request.POST.get('negative_marking', '0.0').strip()
        max_attempts_str = request.POST.get('max_attempts', '1').strip()
        tags = request.POST.get('tags', '').strip()
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', 'DRAFT').strip()
        shuffle_questions = bool(request.POST.get('shuffle_questions'))
        show_solutions = bool(request.POST.get('show_solutions_after_submission', True))

        # Resolve subject from category if not provided
        selected_module = None
        selected_category = None

        if module_id and module_id.isdigit():
            selected_module = ReadinessModule.objects.filter(id=int(module_id)).first()

        if subject_category_id and subject_category_id.isdigit():
            selected_category = SubjectCategory.objects.filter(id=int(subject_category_id)).first()
            if selected_category:
                if not subject:
                    subject = selected_category.name
                if not selected_module:
                    selected_module = selected_category.module

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

        try:
            negative_marking = float(negative_marking_str)
            if negative_marking < 0:
                errors.append("Negative marking cannot be less than 0.")
        except ValueError:
            negative_marking = 0.0

        try:
            max_attempts = int(max_attempts_str)
            if max_attempts < 1:
                max_attempts = 1
        except ValueError:
            max_attempts = 1

        if errors:
            return render(request, 'assignments/admin/create.html', {
                'errors': errors,
                'modules': modules,
                'subject_categories': subject_categories,
                'form_data': request.POST,
            })

        assignment = Assignment.objects.create(
            title=title,
            module=selected_module,
            subject_category=selected_category,
            exam_type=exam_type,
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            time_limit=time_limit,
            negative_marking=negative_marking,
            shuffle_questions=shuffle_questions,
            show_solutions_after_submission=show_solutions,
            max_attempts=max_attempts,
            tags=tags,
            description=description,
            status='DRAFT' if status not in ['DRAFT', 'PUBLISHED'] else status,
        )

        messages.success(request, f"Assessment '{assignment.title}' created! Now add your questions.")
        return redirect('assignments:admin_questions', assignment_id=assignment.id)

    return render(request, 'assignments/admin/create.html', {
        'modules': modules,
        'subject_categories': subject_categories,
    })


@admin_required
@require_http_methods(["GET", "POST"])
def admin_assignment_edit_view(request, assignment_id):
    """
    Allows editing an existing assignment's metadata.
    Protects historical attempts and results with database transactions and warnings.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    modules = ReadinessModule.objects.all().prefetch_related('subjects')
    subject_categories = SubjectCategory.objects.all().select_related('module')
    completed_attempts_count = assignment.attempts.filter(status='COMPLETED').count()

    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        exam_type = request.POST.get('exam_type', 'SUBJECT')
        module_id = request.POST.get('module_id', '').strip()
        subject_category_id = request.POST.get('subject_category_id', '').strip()
        subject = request.POST.get('subject', '').strip()
        topic = request.POST.get('topic', '').strip()
        difficulty = request.POST.get('difficulty', 'MEDIUM').strip()
        time_limit_str = request.POST.get('time_limit', '30').strip()
        negative_marking_str = request.POST.get('negative_marking', '0.0').strip()
        max_attempts_str = request.POST.get('max_attempts', '1').strip()
        tags = request.POST.get('tags', '').strip()
        description = request.POST.get('description', '').strip()
        shuffle_questions = bool(request.POST.get('shuffle_questions'))
        show_solutions = bool(request.POST.get('show_solutions_after_submission', True))

        selected_module = None
        selected_category = None

        if module_id and module_id.isdigit():
            selected_module = ReadinessModule.objects.filter(id=int(module_id)).first()

        if subject_category_id and subject_category_id.isdigit():
            selected_category = SubjectCategory.objects.filter(id=int(subject_category_id)).first()
            if selected_category:
                if not subject:
                    subject = selected_category.name
                if not selected_module:
                    selected_module = selected_category.module

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

        try:
            negative_marking = float(negative_marking_str)
        except ValueError:
            negative_marking = 0.0

        try:
            max_attempts = int(max_attempts_str)
            if max_attempts < 1:
                max_attempts = 1
        except ValueError:
            max_attempts = 1

        if errors:
            return render(request, 'assignments/admin/edit.html', {
                'assignment': assignment,
                'modules': modules,
                'subject_categories': subject_categories,
                'completed_attempts_count': completed_attempts_count,
                'errors': errors,
            })

        with transaction.atomic():
            assignment.title = title
            assignment.module = selected_module
            assignment.subject_category = selected_category
            assignment.exam_type = exam_type
            assignment.subject = subject
            assignment.topic = topic
            assignment.difficulty = difficulty
            assignment.time_limit = time_limit
            assignment.negative_marking = negative_marking
            assignment.shuffle_questions = shuffle_questions
            assignment.show_solutions_after_submission = show_solutions
            assignment.max_attempts = max_attempts
            assignment.tags = tags
            assignment.description = description
            assignment.save()

        messages.success(request, f"Assessment '{assignment.title}' updated successfully.")
        return redirect('assignments:admin_list')

    return render(request, 'assignments/admin/edit.html', {
        'assignment': assignment,
        'modules': modules,
        'subject_categories': subject_categories,
        'completed_attempts_count': completed_attempts_count,
    })


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
            messages.error(request, "Cannot publish an assessment with zero questions. Please add questions first.")
        else:
            assignment.status = new_status
            assignment.save()
            messages.success(request, f"Assessment status updated to {assignment.get_status_display()}.")

    return redirect(request.META.get('HTTP_REFERER', 'assignments:admin_list'))


@admin_required
@require_http_methods(["GET", "POST"])
def admin_assignment_questions_view(request, assignment_id):
    """
    Manages questions and options for a specific assignment:
    - Lists existing questions with options, code snippets, and correct indicators.
    - POST: Adds a new MCQ, MSQ, or Code Tracing question with options A, B, C, D.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    questions = assignment.questions.prefetch_related('options').all()

    errors = []
    if request.method == "POST":
        question_text = request.POST.get('question_text', '').strip()
        code_snippet = request.POST.get('code_snippet', '').strip()
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
        elif question_type in ['MCQ', 'CODE'] and len(correct_options) > 1:
            errors.append("Single Choice (MCQ) & Code Tracing questions can only have ONE correct option.")

        if not errors:
            next_order = (assignment.questions.count() or 0) + 1
            question = Question.objects.create(
                assignment=assignment,
                question_text=question_text,
                code_snippet=code_snippet,
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
