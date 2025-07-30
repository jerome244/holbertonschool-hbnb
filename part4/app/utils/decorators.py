# utils/decorators.py

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """
    Decorator to ensure the user is an admin.
    If not an admin, it either redirects to login or returns a 403 error.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.login"))  # Redirect to login if not logged in
            # Alternatively, you could raise an abort here:
            # abort(403)  # To directly return a 403 error instead of redirecting
        return f(*args, **kwargs)

    return decorated_function
