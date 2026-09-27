# assignments/logic/scoring.py
#
# WHAT: Evaluation and scoring algorithm for Assignment attempts.
#
# WHY:  Evaluates submitted student answers against correct options for both:
#       1. MCQ (Single Choice)
#       2. MSQ (Multiple Select) - STRICT ALL-OR-NOTHING MARKING
#
# COLLEGE REQUIREMENT:
#       - Pure Python logic using set comparisons:
#         Full marks if and only if: selected_options == correct_options
#         Zero marks for partial selections or any incorrect selection.
#       - Atomic transaction guarantees database consistency.

from django.db import transaction
from django.utils import timezone
from assignments.models import Attempt, StudentAnswer, SelectedOptionRecord, QuestionOption


def evaluate_attempt(attempt: Attempt, post_data) -> Attempt:
    """
    Evaluates all submitted answers for an attempt and computes:
    - score (total marks obtained)
    - percentage (score / total_marks * 100)
    - correct_count
    - wrong_count
    - unattempted_count
    - records detailed StudentAnswer and SelectedOptionRecord rows.

    Parameters:
    - attempt: In-progress Attempt instance
    - post_data: Django request.POST QueryDict containing question responses
                 formatted as 'q_<question_id>' -> list of option IDs

    Returns:
    - Saved Attempt instance marked as COMPLETED.
    """
    assignment = attempt.assignment
    questions = assignment.questions.prefetch_related('options').all()

    total_score = 0
    correct_count = 0
    wrong_count = 0
    unattempted_count = 0

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
                marks_obtained = 0
                unattempted_count += 1
            else:
                # Student submitted answers
                # For both MCQ and MSQ: Set equality guarantees exact match!
                # - For MCQ: Exactly 1 option must be selected and match the 1 correct option.
                # - For MSQ: All correct options must be selected, and NO incorrect option selected.
                if selected_ids == correct_ids:
                    is_correct = True
                    marks_obtained = question.marks
                    total_score += marks_obtained
                    correct_count += 1
                else:
                    # Incorrect answer (or partial answer in MSQ -> 0 marks)
                    is_correct = False
                    marks_obtained = 0
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

        # Compute percentage
        total_possible = assignment.total_marks
        if total_possible <= 0:
            total_possible = sum(q.marks for q in questions)
        
        percentage = 0.0
        if total_possible > 0:
            percentage = round((total_score / total_possible) * 100.0, 2)

        # Update attempt fields
        attempt.score = total_score
        attempt.percentage = percentage
        attempt.correct_count = correct_count
        attempt.wrong_count = wrong_count
        attempt.unattempted_count = unattempted_count
        attempt.status = 'COMPLETED'
        attempt.submitted_at = timezone.now()
        attempt.save()

    return attempt
