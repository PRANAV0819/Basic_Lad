# assignments/logic/scoring.py
#
# WHAT: Evaluation and scoring algorithm for Assignment attempts.
#
# WHY:  Evaluates submitted student answers against correct options for:
#       1. MCQ (Single Choice)
#       2. MSQ (Multiple Select) - STRICT ALL-OR-NOTHING MARKING
#       3. CODE (Code Output / Tracing)
#       4. NUMERICAL (Numerical Questions)
#
# COLLEGE REQUIREMENT:
#       - Pure Python logic using set comparisons:
#         Full marks if and only if: selected_options == correct_options
#         Zero marks for partial selections or any incorrect selection.
#       - Server-side deadline enforcement and auto-submission handling.
#       - Atomic transaction guarantees database consistency.

from django.db import transaction
from django.utils import timezone
from assignments.models import Attempt, StudentAnswer, SelectedOptionRecord, QuestionOption


def evaluate_attempt(attempt: Attempt, post_data, auto_submitted: bool = False) -> Attempt:
    """
    Evaluates all submitted answers for an attempt and computes:
    - score (total marks obtained, accounting for negative marking penalty if configured)
    - percentage (score / total_marks * 100)
    - is_passed (percentage >= assignment.passing_percentage)
    - correct_count
    - wrong_count
    - unattempted_count
    - time_taken_seconds
    - records detailed StudentAnswer and SelectedOptionRecord rows.

    Parameters:
    - attempt: In-progress Attempt instance
    - post_data: Django request.POST QueryDict containing question responses
                 formatted as 'q_<question_id>' -> list of option IDs
    - auto_submitted: bool, True if triggered by server timer expiry

    Returns:
    - Saved Attempt instance marked as SUBMITTED or AUTO_SUBMITTED.
    """
    assignment = attempt.assignment
    questions = assignment.questions.prefetch_related('options').all()

    total_score = 0.0
    correct_count = 0
    wrong_count = 0
    unattempted_count = 0

    now = timezone.now()

    with transaction.atomic():
        # Clean up any partial answers if previously created
        attempt.answers.all().delete()

        for question in questions:
            field_name = f"q_{question.id}"
            if hasattr(post_data, 'getlist'):
                raw_selected = post_data.getlist(field_name)
            else:
                val = post_data.get(field_name, [])
                raw_selected = val if isinstance(val, (list, tuple, set)) else [val] if val else []

            # Convert selected option strings to set of integers
            selected_ids = set()
            for opt_val in raw_selected:
                try:
                    selected_ids.add(int(opt_val))
                except (ValueError, TypeError):
                    continue

            # Query the correct option IDs for this question
            correct_ids = set(
                opt.id for opt in question.options.all() if opt.is_correct
            )

            # Evaluation logic
            if not selected_ids:
                # Student did not select any option for this question
                is_correct = False
                marks_obtained = 0.0
                unattempted_count += 1
            else:
                # Student submitted answers
                # Set equality: For MCQ, CODE, NUMERICAL (1 option) or MSQ (all correct options)
                if selected_ids == correct_ids:
                    is_correct = True
                    marks_obtained = float(question.marks)
                    total_score += marks_obtained
                    correct_count += 1
                else:
                    # Incorrect answer (or partial answer in MSQ -> penalty/0 marks)
                    is_correct = False
                    penalty = float(assignment.negative_marking or 0.0)
                    marks_obtained = -penalty if penalty > 0 else 0.0
                    total_score += marks_obtained
                    wrong_count += 1

            # Save the StudentAnswer record
            student_answer = StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                is_correct=is_correct,
                marks_obtained=marks_obtained
            )

            # Save each selected option record (for student review breakdown)
            valid_options = QuestionOption.objects.filter(
                id__in=selected_ids,
                question=question
            )
            for opt in valid_options:
                SelectedOptionRecord.objects.create(
                    student_answer=student_answer,
                    option=opt
                )

        total_score = max(0.0, round(total_score, 2))

        # Compute percentage
        total_possible = assignment.total_marks
        if total_possible <= 0:
            total_possible = sum(q.marks for q in questions)

        percentage = 0.0
        if total_possible > 0:
            percentage = round((total_score / total_possible) * 100.0, 2)

        # Time taken calculation
        time_taken_seconds = 0
        if attempt.started_at:
            time_taken_seconds = max(1, int((now - attempt.started_at).total_seconds()))

        passing_threshold = assignment.passing_percentage or 40
        is_passed = (percentage >= passing_threshold)

        # Update attempt fields
        attempt.score = total_score
        attempt.percentage = percentage
        attempt.is_passed = is_passed
        attempt.correct_count = correct_count
        attempt.wrong_count = wrong_count
        attempt.unattempted_count = unattempted_count
        attempt.time_taken_seconds = time_taken_seconds
        attempt.status = 'AUTO_SUBMITTED' if auto_submitted else 'SUBMITTED'
        attempt.submitted_at = now
        attempt.save()

    return attempt
