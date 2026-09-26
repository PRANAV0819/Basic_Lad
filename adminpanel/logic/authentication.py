# adminpanel/logic/authentication.py
#
# WHAT: Handles authentication logic and session state management for Admin.
#
# COLLEGE REQUIREMENT:
# We do NOT use Django's auth module (django.contrib.auth, authenticate(), login(), logout()).
# We implement our own step-by-step verification and manage the logged-in state
# using Django's session dictionary (request.session).

from adminpanel.models import Admin
from .validation import validate_login_inputs
from .password import verify_password


def authenticate_admin(raw_username: str, raw_password: str):
    """
    Executes the manual Admin authentication algorithm.

    Algorithm:
    1. Check if username or password fields are empty (via validate_login_inputs).
    2. Search the MySQL database for an Admin record with the given username.
    3. If no record is found:
       -> Reject login with generic message: 'Invalid username or password'.
    4. If record is found:
       -> Read stored_salt and stored_password_hash from the Admin record.
       -> Run verify_password(cleaned_password, stored_salt, stored_password_hash).
    5. If the generated hash matches stored_password_hash:
       -> Return (True, None, admin_instance).
    6. If they do not match:
       -> Return (False, 'Invalid username or password', None).

    Security Note:
    We never reveal whether it was the username or the password that failed.
    This prevents username enumeration.
    """
    # Step 1: Input Validation
    is_valid, val_error, cleaned_username, cleaned_password = validate_login_inputs(
        raw_username, raw_password
    )

    if not is_valid:
        return False, "Invalid username or password", None

    # Step 2 & 3: Find username in Admin table
    try:
        admin_record = Admin.objects.filter(username=cleaned_username).first()
    except Exception:
        return False, "Database connection error. Please try again.", None

    if admin_record is None:
        # Admin record not found
        return False, "Invalid username or password", None

    # Step 4: Verify entered password using our custom algorithm
    is_password_correct = verify_password(
        cleaned_password,
        admin_record.salt,
        admin_record.password_hash
    )

    if not is_password_correct:
        # Hash mismatch
        return False, "Invalid username or password", None

    # Step 5: Authentication successful
    return True, None, admin_record


def login_admin(request, admin: Admin):
    """
    Establishes the logged-in state using Django's session dictionary.

    - Stores admin ID and username in request.session.
    - Sets 'is_admin_logged_in' flag to True.
    - Calls cycle_key() to prevent session fixation attacks.
    """
    request.session['admin_id'] = admin.id
    request.session['admin_username'] = admin.username
    request.session['is_admin_logged_in'] = True
    request.session.cycle_key()


def logout_admin(request):
    """
    Destroys the logged-in state completely.
    request.session.flush() deletes the session record from the database
    and clears the session cookie from the browser.
    """
    request.session.flush()


def is_admin_logged_in(request) -> bool:
    """
    Checks whether the current request is coming from an authenticated Admin.
    Returns True if 'is_admin_logged_in' is True and a valid 'admin_id' exists.
    """
    return bool(
        request.session.get('is_admin_logged_in') is True and
        request.session.get('admin_id') is not None
    )


def get_logged_in_admin_username(request) -> str:
    """Returns the logged-in admin's username from session, or 'Admin' as default."""
    return request.session.get('admin_username', 'Admin')
