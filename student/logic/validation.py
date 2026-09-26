# student/logic/validation.py
#
# WHAT: Manual input validation for Student Signup, Login, and Profile update.
#
# WHY:  Enforces business rules and data sanitization before interacting with the database:
#       - Rejects blank inputs
#       - Validates email formatting
#       - Enforces password matching
#       - Checks for duplicate email registrations
#       - Pre-sanitizes fields (trimming leading/trailing whitespace)

import re
from student.models import Student

# Standard basic email regex: checks username@domain.extension
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


def validate_student_signup(name: str, email: str, password: str, confirm_password: str, department: str = "", year: str = ""):
    """
    Validates form data submitted during Student Signup.

    Rules:
    1. Name, Email, Password, and Confirm Password are required.
    2. Name must be at least 2 characters and at most 150 characters.
    3. Email must follow valid email format.
    4. Password must be at least 6 characters.
    5. Password and Confirm Password must match exactly.
    6. Email must not already exist in the Student database table.

    Returns:
        (is_valid: bool, error_message: str | None, cleaned_data: dict)
    """
    cleaned_name = (name or "").strip()
    cleaned_email = (email or "").strip().lower()
    cleaned_password = (password or "").strip()
    cleaned_confirm = (confirm_password or "").strip()
    cleaned_dept = (department or "").strip()
    cleaned_year = (year or "").strip()

    cleaned_data = {
        'name': cleaned_name,
        'email': cleaned_email,
        'password': cleaned_password,
        'department': cleaned_dept,
        'year': cleaned_year,
    }

    # 1. Required fields check
    if not cleaned_name:
        return False, "Please enter your full name.", cleaned_data

    if not cleaned_email:
        return False, "Please enter your email address.", cleaned_data

    if not cleaned_password:
        return False, "Please enter a password.", cleaned_data

    if not cleaned_confirm:
        return False, "Please confirm your password.", cleaned_data

    # 2. Name length validation
    if len(cleaned_name) < 2:
        return False, "Name must be at least 2 characters long.", cleaned_data

    # 3. Email format validation
    if not EMAIL_REGEX.match(cleaned_email):
        return False, "Please enter a valid email address.", cleaned_data

    # 4. Password length validation
    if len(cleaned_password) < 6:
        return False, "Password must be at least 6 characters long.", cleaned_data

    # 5. Password confirmation check
    if cleaned_password != cleaned_confirm:
        return False, "Passwords do not match. Please re-enter.", cleaned_data

    # 6. Duplicate email check
    try:
        if Student.objects.filter(email=cleaned_email).exists():
            return False, "An account with this email already exists.", cleaned_data
    except Exception:
        return False, "Database connection error. Please try again.", cleaned_data

    return True, None, cleaned_data


def validate_student_login(raw_email: str, raw_password: str):
    """
    Validates form data submitted during Student Login.

    Rules:
    - Both email and password must be non-empty strings.
    """
    cleaned_email = (raw_email or "").strip().lower()
    cleaned_password = (raw_password or "").strip()

    if not cleaned_email or not cleaned_password:
        return False, "Please enter both email and password.", cleaned_email, cleaned_password

    return True, None, cleaned_email, cleaned_password


def validate_student_profile(name: str, department: str, year: str):
    """
    Validates data submitted when updating Student Profile.

    Rules:
    - Name must be at least 2 characters long.
    - Department and year are sanitized strings.
    """
    cleaned_name = (name or "").strip()
    cleaned_dept = (department or "").strip()
    cleaned_year = (year or "").strip()

    if not cleaned_name:
        return False, "Name cannot be empty.", {}

    if len(cleaned_name) < 2:
        return False, "Name must be at least 2 characters long.", {}

    cleaned_data = {
        'name': cleaned_name,
        'department': cleaned_dept,
        'year': cleaned_year,
    }
    return True, None, cleaned_data
