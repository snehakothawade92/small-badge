from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """
    Decorator that restricts access to users with specific roles.
    Example usage: @role_required('super_admin', 'org_admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('auth.login'))
            
            # Check user role
            if current_user.role not in roles:
                flash("You do not have permission to view this resource.", "danger")
                abort(403) # Return HTTP 403 Forbidden
                
            # If org_admin, check if approved
            if current_user.role == 'org_admin' and current_user.status != 'active':
                flash("Your organization account is pending approval by the Super Admin.", "info")
                return redirect(url_for('auth.pending_approval'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Specific helper decorators for cleaner code
def admin_required(f):
    return role_required('super_admin')(f)

def org_required(f):
    return role_required('org_admin')(f)

def student_required(f):
    return role_required('student')(f)
