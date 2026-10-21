# assignments/views_admin.py
#
# WHAT: Admin controllers for managing assignments, subject categories, questions,
#       and inspecting student attempt records.
#
# WHY:  Admins must be able to:
#       1. List all assessments (filtered by Module, Subject, Type, Status, Creator, Search, Pagination).
#       2. Inspect comprehensive student attempt records (ID, PRN/email, started/submitted timestamps,
#          deadlines, time taken, marks, percentage, attempt status).
#       3. Create & edit assessments with full module & subject assignment, test rules, and safeguards.
#       4. Dynamically manage subjects and curriculum topics through the admin interface.
#       5. Author MCQ, MSQ, Code Tracing, and Numerical questions, and reorder questions.
#       6. Publish, Close, or Archive assessments.

from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Count, Avg, Q, Sum
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

from assignments.models import (
    Assignment,
    Question,
    QuestionOption,
    Attempt,
    ReadinessModule,
    SubjectCategory,
)
from adminpanel.models import Admin
from assignments.logic.security import admin_required


@admin_required
@require_http_methods(["GET"])
def admin_assignment_list_view(request):
    """
    Unified Admin Assessment Management Dashboard:
    - Tab 'assessments': Complete table of tests with search, category/subject filters, pagination.
    - Tab 'attempts': Complete table of student test attempts with real-time status and marks.
    """
    active_tab = request.GET.get('tab', 'assessments')
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'ALL')
    module_filter = request.GET.get('module_id', 'ALL')
    subject_filter = request.GET.get('subject_category_id', 'ALL')
    type_filter = request.GET.get('assessment_type', 'ALL')
    page_number = request.GET.get('page', 1)

    modules = ReadinessModule.objects.all().prefetch_related('subjects')
    all_subject_categories = SubjectCategory.objects.all().select_related('module')

    # Summary metrics
    total_count = Assignment.objects.count()
    published_count = Assignment.objects.filter(status='PUBLISHED').count()
    draft_count = Assignment.objects.filter(status='DRAFT').count()
    archived_count = Assignment.objects.filter(status__in=['ARCHIVED', 'CLOSED']).count()
    total_attempts_count = Attempt.objects.count()
    completed_attempts_count = Attempt.objects.filter(
        status__in=['SUBMITTED', 'AUTO_SUBMITTED', 'COMPLETED']
    ).count()

    if active_tab == 'attempts':
        # Student Attempt Records View
        attempts_qs = Attempt.objects.select_related(
            'student',
            'assignment',
            'assignment__module',
            'assignment__subject_category'
        ).order_by('-started_at')

        if search_query:
            attempts_qs = attempts_qs.filter(
                Q(student__name__icontains=search_query) |
                Q(student__email__icontains=search_query) |
                Q(student__prn__icontains=search_query) |
                Q(assignment__title__icontains=search_query) |
                Q(assignment__subject__icontains=search_query)
            )

        if status_filter != 'ALL':
            attempts_qs = attempts_qs.filter(status=status_filter)

        if module_filter != 'ALL' and module_filter.isdigit():
            attempts_qs = attempts_qs.filter(assignment__module_id=int(module_filter))

        if subject_filter != 'ALL' and subject_filter.isdigit():
            attempts_qs = attempts_qs.filter(assignment__subject_category_id=int(subject_filter))

        # Pagination: 15 records per page
        paginator = Paginator(attempts_qs, 15)
        try:
            attempts_page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            attempts_page = paginator.page(1)

        context = {
            'active_tab': 'attempts',
            'attempts_page': attempts_page,
            'modules': modules,
            'all_subject_categories': all_subject_categories,
            'search_query': search_query,
            'status_filter': status_filter,
            'module_filter': module_filter,
            'subject_filter': subject_filter,
            'type_filter': type_filter,
            'total_count': total_count,
            'published_count': published_count,
            'draft_count': draft_count,
            'archived_count': archived_count,
            'total_attempts_count': total_attempts_count,
            'completed_attempts_count': completed_attempts_count,
        }
        return render(request, 'assignments/admin/list.html', context)

    else:
        # Assessments Catalog View
        assignments_qs = Assignment.objects.select_related(
            'module',
            'subject_category',
            'created_by'
        ).annotate(
            num_questions=Count('questions', distinct=True),
            num_attempts=Count('attempts', distinct=True)
        ).order_by('-created_at')

        if search_query:
            assignments_qs = assignments_qs.filter(
                Q(title__icontains=search_query) |
                Q(subject__icontains=search_query) |
                Q(topic__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(tags__icontains=search_query) |
                Q(created_by_name__icontains=search_query)
            )

        if status_filter != 'ALL':
            if status_filter == 'ARCHIVED':
                assignments_qs = assignments_qs.filter(status__in=['ARCHIVED', 'CLOSED'])
            else:
                assignments_qs = assignments_qs.filter(status=status_filter)

        if module_filter != 'ALL' and module_filter.isdigit():
            assignments_qs = assignments_qs.filter(module_id=int(module_filter))

        if subject_filter != 'ALL' and subject_filter.isdigit():
            assignments_qs = assignments_qs.filter(subject_category_id=int(subject_filter))

        if type_filter != 'ALL':
            assignments_qs = assignments_qs.filter(assessment_type=type_filter)

        # Pagination: 12 tests per page
        paginator = Paginator(assignments_qs, 12)
        try:
            assignments_page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            assignments_page = paginator.page(1)

        context = {
            'active_tab': 'assessments',
            'assignments_page': assignments_page,
            'modules': modules,
            'all_subject_categories': all_subject_categories,
            'search_query': search_query,
            'status_filter': status_filter,
            'module_filter': module_filter,
            'subject_filter': subject_filter,
            'type_filter': type_filter,
            'total_count': total_count,
            'published_count': published_count,
            'draft_count': draft_count,
            'archived_count': archived_count,
            'total_attempts_count': total_attempts_count,
            'completed_attempts_count': completed_attempts_count,
        }
        return render(request, 'assignments/admin/list.html', context)


@admin_required
@require_http_methods(["GET", "POST"])
def admin_assignment_create_view(request):
    """
    Creates a new Assignment record with module, subject, difficulty, test configuration,
    and server-side validation. Redirects to question authoring on success.
    """
    modules = ReadinessModule.objects.all().prefetch_related('subjects')
    subject_categories = SubjectCategory.objects.all().select_related('module')

    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        assessment_type = request.POST.get('assessment_type', 'SUBJECT').strip()
        exam_type = 'FINAL' if assessment_type == 'MOCK' else 'SUBJECT'
        module_id = request.POST.get('module_id', '').strip()
        subject_category_id = request.POST.get('subject_category_id', '').strip()
        subject = request.POST.get('subject', '').strip()
        topic = request.POST.get('topic', '').strip()
        difficulty = request.POST.get('difficulty', 'MEDIUM').strip()
        time_limit_str = request.POST.get('time_limit', '30').strip()
        passing_percentage_str = request.POST.get('passing_percentage', '40').strip()
        negative_marking_str = request.POST.get('negative_marking', '0.0').strip()
        max_attempts_str = request.POST.get('max_attempts', '1').strip()
        start_date_str = request.POST.get('start_date', '').strip()
        end_date_str = request.POST.get('end_date', '').strip()
        tags = request.POST.get('tags', '').strip()
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', 'DRAFT').strip()
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

        # Server-side validation
        errors = []
        if not title:
            errors.append("Assessment title is required.")
        if not subject:
            errors.append("Subject name is required.")

        try:
            time_limit = int(time_limit_str)
            if time_limit < 1:
                errors.append("Duration must be at least 1 minute.")
        except ValueError:
            errors.append("Duration must be a valid integer.")
            time_limit = 30

        try:
            passing_percentage = int(passing_percentage_str)
            if passing_percentage < 0 or passing_percentage > 100:
                errors.append("Passing percentage must be between 0 and 100.")
        except ValueError:
            passing_percentage = 40

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

        # Date parsing
        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str)
            except ValueError:
                pass
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str)
            except ValueError:
                pass

        if start_date and end_date and start_date > end_date:
            errors.append("Start date cannot be after end availability date.")

        if errors:
            return render(request, 'assignments/admin/create.html', {
                'errors': errors,
                'modules': modules,
                'subject_categories': subject_categories,
                'form_data': request.POST,
            })

        # Creator resolution
        admin_id = request.session.get('admin_id')
        admin_user = Admin.objects.filter(id=admin_id).first() if admin_id else None
        created_by_name = request.session.get('admin_username', 'Administrator')

        assignment = Assignment.objects.create(
            title=title,
            module=selected_module,
            subject_category=selected_category,
            assessment_type=assessment_type,
            exam_type=exam_type,
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            time_limit=time_limit,
            passing_percentage=passing_percentage,
            negative_marking=negative_marking,
            shuffle_questions=shuffle_questions,
            show_solutions_after_submission=show_solutions,
            max_attempts=max_attempts,
            start_date=start_date,
            end_date=end_date,
            tags=tags,
            description=description,
            status='DRAFT' if status not in ['DRAFT', 'PUBLISHED', 'ARCHIVED'] else status,
            created_by=admin_user,
            created_by_name=created_by_name,
        )

        messages.success(request, f"Assessment '{assignment.title}' created! Now add questions to your test.")
        return redirect('assignments:admin_questions', assignment_id=assignment.id)

    return render(request, 'assignments/admin/create.html', {
        'modules': modules,
        'subject_categories': subject_categories,
    })


@admin_required
@require_http_methods(["GET", "POST"])
def admin_assignment_edit_view(request, assignment_id):
    """
    Updates an existing assignment's metadata, rules, and configuration.
    Safeguards completed attempts with transactions and warnings.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    modules = ReadinessModule.objects.all().prefetch_related('subjects')
    subject_categories = SubjectCategory.objects.all().select_related('module')
    completed_attempts_count = assignment.attempts.filter(
        status__in=['SUBMITTED', 'AUTO_SUBMITTED', 'COMPLETED']
    ).count()

    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        assessment_type = request.POST.get('assessment_type', 'SUBJECT').strip()
        exam_type = 'FINAL' if assessment_type == 'MOCK' else 'SUBJECT'
        module_id = request.POST.get('module_id', '').strip()
        subject_category_id = request.POST.get('subject_category_id', '').strip()
        subject = request.POST.get('subject', '').strip()
        topic = request.POST.get('topic', '').strip()
        difficulty = request.POST.get('difficulty', 'MEDIUM').strip()
        time_limit_str = request.POST.get('time_limit', '30').strip()
        passing_percentage_str = request.POST.get('passing_percentage', '40').strip()
        negative_marking_str = request.POST.get('negative_marking', '0.0').strip()
        max_attempts_str = request.POST.get('max_attempts', '1').strip()
        start_date_str = request.POST.get('start_date', '').strip()
        end_date_str = request.POST.get('end_date', '').strip()
        tags = request.POST.get('tags', '').strip()
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', assignment.status).strip()
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
            errors.append("Assessment title is required.")
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
            passing_percentage = int(passing_percentage_str)
            if passing_percentage < 0 or passing_percentage > 100:
                errors.append("Passing percentage must be between 0 and 100.")
        except ValueError:
            passing_percentage = 40

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

        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str)
            except ValueError:
                pass
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str)
            except ValueError:
                pass

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
            assignment.assessment_type = assessment_type
            assignment.exam_type = exam_type
            assignment.subject = subject
            assignment.topic = topic
            assignment.difficulty = difficulty
            assignment.time_limit = time_limit
            assignment.passing_percentage = passing_percentage
            assignment.negative_marking = negative_marking
            assignment.shuffle_questions = shuffle_questions
            assignment.show_solutions_after_submission = show_solutions
            assignment.max_attempts = max_attempts
            assignment.start_date = start_date
            assignment.end_date = end_date
            assignment.tags = tags
            assignment.description = description
            if status in ['DRAFT', 'PUBLISHED', 'ARCHIVED', 'CLOSED']:
                assignment.status = status
            assignment.save()

            # Ensure total marks agree with question marks
            assignment.recalculate_total_marks()

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
    Toggles assignment status between DRAFT, PUBLISHED, and ARCHIVED.
    Validates question count and verifies total marks consistency before publishing.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    new_status = request.POST.get('status')

    if new_status in ['DRAFT', 'PUBLISHED', 'ARCHIVED', 'CLOSED']:
        if new_status == 'PUBLISHED':
            if assignment.questions.count() == 0:
                messages.error(request, "Cannot publish an assessment with zero questions. Please add questions first.")
                return redirect(request.META.get('HTTP_REFERER', 'assignments:admin_list'))
            # Recalculate total marks so it agrees with question marks
            assignment.recalculate_total_marks()

        assignment.status = new_status
        assignment.save()
        messages.success(request, f"Assessment status updated to {assignment.get_status_display()}.")

    return redirect(request.META.get('HTTP_REFERER', 'assignments:admin_list'))


@admin_required
@require_http_methods(["GET", "POST"])
def admin_assignment_questions_view(request, assignment_id):
    """
    Manages questions and options for an assessment:
    - Lists all questions with code snippets, options, correct flags, and marks.
    - POST: Adds a new MCQ, MSQ, CODE, or NUMERICAL question.
    - Automatically updates assignment total_marks to keep them in agreement.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    questions = assignment.questions.prefetch_related('options').order_by('order', 'id')

    errors = []
    if request.method == "POST":
        question_text = request.POST.get('question_text', '').strip()
        code_snippet = request.POST.get('code_snippet', '').strip()
        question_type = request.POST.get('question_type', 'MCQ').strip()
        marks_str = request.POST.get('marks', '1').strip()
        solution = request.POST.get('solution', '').strip()

        opt_a = request.POST.get('opt_a', '').strip()
        opt_b = request.POST.get('opt_b', '').strip()
        opt_c = request.POST.get('opt_c', '').strip()
        opt_d = request.POST.get('opt_d', '').strip()
        correct_options = request.POST.getlist('correct_options')

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
            errors.append("At least Option A and Option B are required.")

        if not correct_options:
            errors.append("Please designate at least one option as the correct answer.")

        if question_type in ['MCQ', 'CODE', 'NUMERICAL'] and len(correct_options) > 1:
            errors.append(f"{question_type} format accepts exactly ONE correct option. For multi-answers, select MSQ.")

        if not errors:
            with transaction.atomic():
                next_order = assignment.questions.count() + 1
                q = Question.objects.create(
                    assignment=assignment,
                    question_text=question_text,
                    code_snippet=code_snippet,
                    question_type=question_type,
                    marks=marks,
                    solution=solution,
                    order=next_order,
                )

                options_payload = [
                    ('A', opt_a, 'A' in correct_options),
                    ('B', opt_b, 'B' in correct_options),
                ]
                if opt_c:
                    options_payload.append(('C', opt_c, 'C' in correct_options))
                if opt_d:
                    options_payload.append(('D', opt_d, 'D' in correct_options))

                for label, text, is_corr in options_payload:
                    QuestionOption.objects.create(
                        question=q,
                        option_label=label,
                        option_text=text,
                        is_correct=is_corr,
                    )

                # Re-calculate assignment total marks to strictly agree
                assignment.recalculate_total_marks()

            messages.success(request, f"Question {q.order} added successfully!")
            return redirect('assignments:admin_questions', assignment_id=assignment.id)

    return render(request, 'assignments/admin/questions.html', {
        'assignment': assignment,
        'questions': questions,
        'errors': errors,
        'form_data': request.POST if request.method == "POST" else {},
    })


@admin_required
@require_http_methods(["POST"])
def admin_question_delete_view(request, assignment_id, question_id):
    """
    Deletes a question and re-normalizes sequence order and assignment total marks.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    question = get_object_or_404(Question, id=question_id, assignment=assignment)

    with transaction.atomic():
        question.delete()
        # Re-number remaining questions
        for idx, q in enumerate(assignment.questions.order_by('order', 'id'), start=1):
            if q.order != idx:
                q.order = idx
                q.save(update_fields=['order'])
        assignment.recalculate_total_marks()

    messages.success(request, "Question deleted and total marks re-balanced.")
    return redirect('assignments:admin_questions', assignment_id=assignment.id)


@admin_required
@require_http_methods(["POST"])
def admin_question_reorder_view(request, assignment_id, question_id):
    """
    Moves a question UP or DOWN in the test sequence.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    question = get_object_or_404(Question, id=question_id, assignment=assignment)
    direction = request.POST.get('direction', 'up')

    questions_list = list(assignment.questions.order_by('order', 'id'))
    curr_idx = questions_list.index(question)

    if direction == 'up' and curr_idx > 0:
        other_q = questions_list[curr_idx - 1]
        question.order, other_q.order = other_q.order, question.order
        question.save(update_fields=['order'])
        other_q.save(update_fields=['order'])
        messages.success(request, f"Moved Question {question.id} up.")
    elif direction == 'down' and curr_idx < len(questions_list) - 1:
        other_q = questions_list[curr_idx + 1]
        question.order, other_q.order = other_q.order, question.order
        question.save(update_fields=['order'])
        other_q.save(update_fields=['order'])
        messages.success(request, f"Moved Question {question.id} down.")

    return redirect('assignments:admin_questions', assignment_id=assignment.id)


@admin_required
@require_http_methods(["GET"])
def admin_subject_manage_view(request):
    """
    Admin interface to view and create additional subjects and topics dynamically.
    Fulfills the prompt requirement to allow administrators to add subjects beyond the initial catalogue.
    """
    modules = ReadinessModule.objects.all().prefetch_related('subjects')
    return render(request, 'assignments/admin/subjects.html', {
        'modules': modules,
    })


@admin_required
@require_http_methods(["POST"])
def admin_subject_create_view(request):
    """
    POST endpoint: Creates a new SubjectCategory under a designated ReadinessModule.
    """
    module_id = request.POST.get('module_id')
    name = request.POST.get('name', '').strip()
    topics = request.POST.get('topics', '').strip()
    description = request.POST.get('description', '').strip()

    if not name or not module_id:
        messages.error(request, "Subject name and parent category are required.")
        return redirect('assignments:admin_subjects')

    module = get_object_or_404(ReadinessModule, id=module_id)
    order = module.subjects.count() + 1

    subj, created = SubjectCategory.objects.get_or_create(
        module=module,
        name=name,
        defaults={
            'topics': topics,
            'description': description or f"Assessments for {name}.",
            'order': order,
        }
    )

    if created:
        messages.success(request, f"New Subject '{subj.name}' created under {module.name}!")
    else:
        messages.info(request, f"Subject '{subj.name}' already exists.")

    return redirect(request.META.get('HTTP_REFERER', 'assignments:admin_subjects'))


@admin_required
@require_http_methods(["POST"])
def admin_subject_delete_view(request, subject_id):
    """
    Deletes an unused SubjectCategory. Prevents deletion if tests are attached.
    """
    subject = get_object_or_404(SubjectCategory, id=subject_id)
    if subject.assignments.count() > 0:
        messages.error(request, f"Cannot delete '{subject.name}' because {subject.assignments.count()} assessment(s) are linked to it.")
    else:
        name = subject.name
        subject.delete()
        messages.success(request, f"Subject '{name}' deleted successfully.")

    return redirect('assignments:admin_subjects')


@admin_required
@require_http_methods(["GET"])
def admin_assignment_submissions_view(request, assignment_id):
    """
    Displays all student attempts for a single specific assignment.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    attempts = assignment.attempts.select_related('student').order_by('-started_at')

    context = {
        'assignment': assignment,
        'attempts': attempts,
        'attempts_count': attempts.count(),
        'avg_score': attempts.aggregate(Avg('score'))['score__avg'] or 0.0,
    }
    return render(request, 'assignments/admin/submissions.html', context)
