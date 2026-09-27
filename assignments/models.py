# assignments/models.py
#
# WHAT: Defines the MySQL database schema for the Assignment Module.
#
# WHY:  Stores assessments (Final & Subject-wise Exams), questions (MCQ & MSQ),
#       options, student attempts, student answers, and selected options.
#
# COLLEGE REQUIREMENT:
#       - Pure Django ORM + MySQL.
#       - Uses custom Student model (student.Student), NOT Django's built-in auth User.
#       - MSQ support (Multiple Select Questions) with clean normalized selection tables.
#       - Strict single-attempt policy enforced via database constraint (unique_together).

from django.db import models
from student.models import Student


class Assignment(models.Model):
    """
    Represents an assignment / exam created by the Admin.
    Can be a 'Final Exam' or a 'Subject-wise Exam'.
    """

    EXAM_TYPE_CHOICES = [
        ('FINAL', 'Final Exam'),
        ('SUBJECT', 'Subject-wise Exam'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('CLOSED', 'Closed'),
    ]

    title = models.CharField(
        max_length=200,
        help_text="Title of the assignment or exam (e.g. Data Structures Assessment 1)"
    )

    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPE_CHOICES,
        default='SUBJECT',
        help_text="Category: Final Exam or Subject-wise Exam"
    )

    subject = models.CharField(
        max_length=100,
        help_text="Subject name (e.g. Operating Systems, Data Structures, Aptitude)"
    )

    topic = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Specific topic (e.g. Paging, Arrays, Probability)"
    )

    description = models.TextField(
        blank=True,
        default='',
        help_text="Instructions or description for students before starting"
    )

    time_limit = models.PositiveIntegerField(
        default=30,
        help_text="Duration in minutes"
    )

    total_marks = models.PositiveIntegerField(
        default=0,
        help_text="Total marks available for this exam"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        help_text="Draft (admin only), Published (students can attempt), Closed (archived)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when assignment was created"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_exam_type_display()}) - {self.status}"

    @property
    def question_count(self):
        return self.questions.count()

    def recalculate_total_marks(self):
        """Sum up marks from all associated questions and update total_marks."""
        total = self.questions.aggregate(models.Sum('marks'))['marks__sum'] or 0
        self.total_marks = total
        self.save(update_fields=['total_marks'])
        return total


class Question(models.Model):
    """
    Represents an individual question inside an assignment.
    Can be Single Choice (MCQ) or Multiple Select (MSQ).
    """

    QUESTION_TYPE_CHOICES = [
        ('MCQ', 'Single Choice (MCQ)'),
        ('MSQ', 'Multiple Select (MSQ)'),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='questions',
        help_text="The assignment this question belongs to"
    )

    question_text = models.TextField(
        help_text="The question problem statement"
    )

    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        default='MCQ',
        help_text="MCQ (single correct) or MSQ (one or more correct)"
    )

    marks = models.PositiveIntegerField(
        default=1,
        help_text="Marks awarded if answered correctly"
    )

    solution = models.TextField(
        blank=True,
        default='',
        help_text="Explanation or step-by-step solution shown after submission"
    )

    order = models.PositiveIntegerField(
        default=1,
        help_text="Display order in test"
    )

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Q{self.order} ({self.question_type}) - {self.question_text[:50]}"

    def correct_options(self):
        """Returns queryset of correct options for this question."""
        return self.options.filter(is_correct=True)


class QuestionOption(models.Model):
    """
    Represents an option choice (A, B, C, D) for a question.
    """

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
        help_text="Question this option belongs to"
    )

    option_label = models.CharField(
        max_length=5,
        help_text="A, B, C, D, etc."
    )

    option_text = models.CharField(
        max_length=500,
        help_text="Content text of this option"
    )

    is_correct = models.BooleanField(
        default=False,
        help_text="True if this option is part of the correct answer"
    )

    class Meta:
        ordering = ['option_label', 'id']

    def __str__(self):
        return f"({self.option_label}) {self.option_text}"


class Attempt(models.Model):
    """
    Represents a student's attempt at an assignment.
    Enforces SINGLE ATTEMPT per student per assignment.
    """

    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attempts',
        help_text="Student who took the test"
    )

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='attempts',
        help_text="Assignment being attempted"
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When student clicked Start Test"
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When student submitted (or auto-submitted by timer)"
    )

    score = models.PositiveIntegerField(
        default=0,
        help_text="Total marks obtained by the student"
    )

    percentage = models.FloatField(
        default=0.0,
        help_text="Percentage scored (score / total_marks * 100)"
    )

    correct_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of fully correct questions"
    )

    wrong_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of incorrect questions"
    )

    unattempted_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of questions student left blank"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='IN_PROGRESS',
        help_text="In Progress while timer runs; Completed once submitted"
    )

    class Meta:
        # Strict college requirement: A student can attempt each assignment only ONCE!
        unique_together = ('student', 'assignment')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.name} - {self.assignment.title} ({self.status}: {self.score}/{self.assignment.total_marks})"


class StudentAnswer(models.Model):
    """
    Represents the student's evaluated response to a single question.
    """

    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name='answers',
        help_text="Parent attempt record"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='student_answers',
        help_text="Question answered"
    )

    is_correct = models.BooleanField(
        default=False,
        help_text="True if student scored full marks on this question"
    )

    marks_obtained = models.PositiveIntegerField(
        default=0,
        help_text="Marks awarded for this question (full marks or 0)"
    )

    class Meta:
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f"Attempt {self.attempt.id} - Q{self.question.id}: Correct={self.is_correct}"


class SelectedOptionRecord(models.Model):
    """
    Stores which options the student selected.
    Supports both Single (1 row for MCQ) and Multiple (>=1 rows for MSQ).
    """

    student_answer = models.ForeignKey(
        StudentAnswer,
        on_delete=models.CASCADE,
        related_name='selected_records',
        help_text="Parent student answer"
    )

    option = models.ForeignKey(
        QuestionOption,
        on_delete=models.CASCADE,
        help_text="Option chosen by the student"
    )

    def __str__(self):
        return f"Answer {self.student_answer.id} -> Option {self.option.option_label}"
