# assignments/logic/security.py
#
# WHAT: Access control helpers and decorators for the Assignment Module.
#
# WHY:  Ensures admin routes are strictly guarded by admin session credentials,
#       and student routes are strictly guarded by student session credentials.
#
# COLLEGE REQUIREMENT:
#       We do NOT use Django's @login_required or User.is_authenticated.
#       Instead, we inspect request.session directly.

from functools import wraps
from django.shortcuts import redirect
from adminpanel.logic.authentication import is_admin_logged_in
from student.logic.authentication import is_student_logged_in, get_logged_in_student


def admin_required(view_func):
    """
    Decorator: Allows access ONLY if an Admin is currently logged in.
    Otherwise redirects to Admin login.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not is_admin_logged_in(request):
            return redirect('signin_admin')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def student_required(view_func):
    """
    Decorator: Allows access ONLY if an authenticated Student session exists.
    Passes the logged-in Student instance as request.student for convenience.
    Otherwise redirects to Student login.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not is_student_logged_in(request):
            return redirect('signin_student')
        
        student = get_logged_in_student(request)
        if not student:
            return redirect('signin_student')

        request.student = student
        return view_func(request, *args, **kwargs)
    return _wrapped_view
