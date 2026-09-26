# student/logic/authentication.py
#
# WHAT: Handles authentication logic and session state management for Students.
#
# COLLEGE REQUIREMENT:
# We do NOT use Django's auth module (django.contrib.auth, authenticate(), login(), logout()).
# We implement our own step-by-step verification and manage the logged-in state
# using Django's session dictionary (request.session).
#
# REUSING PASSWORD ALGORITHM:
# We reuse `adminpanel.logic.password` functions (hash_password, verify_password, generate_salt)
# so the same custom teaching algorithm is used across the entire platform without duplication.

from student.models import Student
from adminpanel.logic.password import verify_password
from .validation import validate_student_login


def authenticate_student(raw_email: str, raw_password: str):
    """
    Executes the manual Student authentication algorithm.

    Algorithm:
    1. Validate input cleanliness (no blank fields).
    2. Search the MySQL database for a Student record matching the email.
    3. If no record is found -> return generic error: 'Invalid email or password'.
    4. If record is found:
       - Read stored_salt and stored_password_hash.
       - Run verify_password(entered_password, stored_salt, stored_password_hash).
    5. If hashes match -> return (True, None, student_instance).
    6. If hash mismatch -> return (False, 'Invalid email or password', None).

    Security:
    The generic error 'Invalid email or password' prevents email enumeration attacks.
    """
    is_valid, error_msg, cleaned_email, cleaned_password = validate_student_login(
        raw_email, raw_password
    )

    if not is_valid:
        return False, "Invalid email or password", None

    try:
        student_record = Student.objects.filter(email=cleaned_email).first()
    except Exception:
        return False, "Database connection error. Please try again.", None

    if student_record is None:
        return False, "Invalid email or password", None

    # Verify password using our reused custom teaching algorithm
    is_password_correct = verify_password(
        cleaned_password,
        student_record.salt,
        student_record.password_hash
    )

    if not is_password_correct:
        return False, "Invalid email or password", None

    return True, None, student_record


def login_student(request, student: Student):
    """
    Establishes the student logged-in state in Django's session dictionary.

    Stores:
    - student_id: int
    - student_name: str
    - student_email: str
    - is_student_logged_in: True
    """
    request.session['student_id'] = student.id
    request.session['student_name'] = student.name
    request.session['student_email'] = student.email
    request.session['is_student_logged_in'] = True
    request.session.cycle_key()


def logout_student(request):
    """
    Destroys the student logged-in state.
    Clears all student session keys and flushes the session.
    """
    request.session.flush()


def is_student_logged_in(request) -> bool:
    """
    Checks whether the current request is from an authenticated Student.
    """
    return bool(
        request.session.get('is_student_logged_in') is True and
        request.session.get('student_id') is not None
    )


def get_logged_in_student(request):
    """
    Fetches the fresh Student database model instance for the active session.
    Returns None if session is missing or invalid.
    """
    if not is_student_logged_in(request):
        return None

    student_id = request.session.get('student_id')
    try:
        return Student.objects.filter(id=student_id).first()
    except Exception:
        return None
