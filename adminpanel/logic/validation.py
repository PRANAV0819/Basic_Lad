# adminpanel/logic/validation.py
#
# WHAT: Contains pure input validation logic for Admin Login.
#
# WHY:  Separating validation from the view and database access ensures "Single Responsibility":
#       - The view handles HTTP requests and responses.
#       - This file handles checking input cleanliness and rules.
#       - No database hits happen if basic validation fails, which saves server resources.
#
# WHERE: adminpanel/logic/validation.py
#
# HOW IT WORKS:
#       1. Accepts raw strings: username and password.
#       2. Strips whitespace from username.
#       3. Checks whether either field is empty.
#       4. Returns a tuple: (is_valid: bool, error_message: str | None, cleaned_username: str, cleaned_password: str)


def validate_login_inputs(raw_username: str, raw_password: str):
    """
    Validates the username and password inputs submitted from the login form.

    Rules:
    1. Both username and password must be non-empty strings.
    2. Username is trimmed of leading and trailing spaces.
    3. Password is trimmed of leading/trailing spaces as well for college project simplicity,
       or kept as is (we check if stripping makes it empty).

    Returns:
        (is_valid: bool, error_message: str | None, cleaned_username: str, cleaned_password: str)
    """
    # Safeguard against None values
    if raw_username is None:
        raw_username = ""
    if raw_password is None:
        raw_password = ""

    cleaned_username = raw_username.strip()
    cleaned_password = raw_password.strip()

    # Check for empty fields
    if not cleaned_username or not cleaned_password:
        return False, "Please enter both username and password.", cleaned_username, cleaned_password

    # Basic length checks (prevent extremely long or malicious inputs)
    if len(cleaned_username) > 20:
        return False, "Username must not exceed 20 characters.", cleaned_username, cleaned_password

    return True, None, cleaned_username, cleaned_password
