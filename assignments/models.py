from django.db import models
from student.models import Student


class ReadinessModule(models.Model):
    """
    Represents one of the primary readiness modules (e.g. Core Subjects,
    Aptitude & Reasoning, Coding & DSA, Communication Skills, Academic / CGPA).
    Has a configured weight percentage totaling 100%.
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Machine-readable code (e.g. CORE_SUBJECTS, APTITUDE_REASONING)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Display title (e.g. Core Subjects)"
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="Short summary of this module's scope and placement importance"
    )
    weight_percentage = models.PositiveIntegerField(
        default=20,
        help_text="Configured weight contributing to the overall readiness index (e.g. 25%)"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default='book',
        help_text="Icon identifier for student dashboard rendering"
    )
    color_theme = models.CharField(
        max_length=30,
        blank=True,
        default='blue',
        help_text="Accent color token: blue, orange, green, purple, teal"
    )
    order = models.PositiveIntegerField(
        default=1,
        help_text="Display sequence in the accordion layout"
    )

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} ({self.weight_percentage}%)"


class SubjectCategory(models.Model):
    """
    Represents a specific subject under a Readiness Module
    (e.g. DBMS, DSA, Quantitative Aptitude, Linked Lists, Technical Interview).
    """
    module = models.ForeignKey(
        ReadinessModule,
        on_delete=models.CASCADE,
        related_name='subjects',
        help_text="Parent readiness module"
    )
    name = models.CharField(
        max_length=150,
        help_text="Subject title (e.g. Data Structures and Algorithms (DSA))"
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="Short subject description"
    )
    topics = models.TextField(
        blank=True,
        default='',
        help_text="Included curriculum topics for student guidance"
    )
    order = models.PositiveIntegerField(
        default=1,
        help_text="Display order within the parent module"
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = 'Subject Categories'

    def __str__(self):
        return f"{self.module.name} → {self.name}"


class Assignment(models.Model):
    """
    Represents an assignment / exam created by the Admin.
    Can be a 'Final Exam' or a 'Subject-wise Exam'.
    Organized into Readiness Modules and Subject Categories.
    """

    EXAM_TYPE_CHOICES = [
        ('FINAL', 'Final Exam'),
        ('SUBJECT', 'Subject-wise Exam'),
    ]

    ASSESSMENT_TYPE_CHOICES = [
        ('PRACTICE', 'Practice Test'),
        ('SUBJECT', 'Subject Test'),
        ('MOCK', 'Mock Test'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
        ('CLOSED', 'Closed'),
    ]

    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    ]

    title = models.CharField(
        max_length=200,
        help_text="Title of the assignment or exam (e.g. Data Structures Assessment 1)"
    )

    module = models.ForeignKey(
        ReadinessModule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments',
        help_text="The readiness module this assessment belongs to"
    )

    subject_category = models.ForeignKey(
        SubjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments',
        help_text="The specific subject inside the readiness module"
    )

    assessment_type = models.CharField(
        max_length=30,
        choices=ASSESSMENT_TYPE_CHOICES,
        default='SUBJECT',
        help_text="Practice Test, Subject Test, or Mock Test"
    )

    created_by = models.ForeignKey(
        'adminpanel.Admin',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_assignments',
        help_text="Admin or teacher who created this assessment"
    )

    created_by_name = models.CharField(
        max_length=100,
        default='Administrator',
        blank=True,
        help_text="Display author name"
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

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='MEDIUM',
        blank=True,
        help_text="Assessment difficulty level"
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

    passing_percentage = models.PositiveIntegerField(
        default=40,
        help_text="Minimum percentage required to pass"
    )

    negative_marking = models.FloatField(
        default=0.0,
        help_text="Negative marks per wrong answer (e.g. 0.25)"
    )

    shuffle_questions = models.BooleanField(
        default=False,
        help_text="Shuffle question order for each attempt"
    )

    show_solutions_after_submission = models.BooleanField(
        default=True,
        help_text="Show answers and explanations after test is submitted"
    )

    max_attempts = models.PositiveIntegerField(
        default=1,
        help_text="Maximum allowed attempts per student"
    )

    start_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Assessment availability start date/time"
    )

    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Assessment availability deadline"
    )

    tags = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="Comma-separated tags for filtering (e.g. campus, interview, mock)"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        help_text="Draft (admin only), Published (students can attempt), Archived"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when assignment was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when assignment was last modified"
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
    Can be Single Choice (MCQ), Multiple Select (MSQ), or Code Output/Tracing.
    """

    QUESTION_TYPE_CHOICES = [
        ('MCQ', 'Single Choice (MCQ)'),
        ('MSQ', 'Multiple Select (MSQ)'),
        ('CODE', 'Code Output / Tracing'),
        ('NUMERICAL', 'Numerical Question'),
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

    code_snippet = models.TextField(
        blank=True,
        default='',
        help_text="Optional code snippet or tracing block"
    )

    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        default='MCQ',
        help_text="MCQ (single correct), MSQ (one or more correct), or Code Output/Tracing"
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
    Supports attempt tracking, server-side deadline enforcement, and retakes.
    """

    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('SUBMITTED', 'Submitted'),
        ('AUTO_SUBMITTED', 'Auto-Submitted'),
        ('EXPIRED', 'Expired / Abandoned'),
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

    attempt_number = models.PositiveIntegerField(
        default=1,
        help_text="Sequence index of this attempt for this student"
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When student clicked Start Test"
    )

    deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Server-enforced deadline when attempt must conclude"
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When student submitted (or auto-submitted by timer)"
    )

    time_taken_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Actual duration taken in seconds"
    )

    score = models.FloatField(
        default=0.0,
        help_text="Total marks obtained by the student"
    )

    percentage = models.FloatField(
        default=0.0,
        help_text="Percentage scored (score / total_marks * 100)"
    )

    is_passed = models.BooleanField(
        default=False,
        help_text="True if score >= assignment.passing_percentage"
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
        help_text="In Progress, Submitted, Auto-Submitted, or Expired"
    )

    class Meta:
        unique_together = ('student', 'assignment', 'attempt_number')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.name} - {self.assignment.title} (Attempt #{self.attempt_number}: {self.score}/{self.assignment.total_marks})"

    @property
    def is_finished(self):
        return self.status in ['SUBMITTED', 'AUTO_SUBMITTED', 'COMPLETED', 'EXPIRED']

    @property
    def time_taken_formatted(self):
        if self.time_taken_seconds:
            m = self.time_taken_seconds // 60
            s = self.time_taken_seconds % 60
            return f"{m}m {s}s"
        if self.submitted_at and self.started_at:
            diff = int((self.submitted_at - self.started_at).total_seconds())
            m = max(0, diff // 60)
            s = max(0, diff % 60)
            return f"{m}m {s}s"
        return "N/A"


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

    marks_obtained = models.FloatField(
        default=0.0,
        help_text="Marks awarded for this question"
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
