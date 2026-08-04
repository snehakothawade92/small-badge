from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.db import get_db, User
from bson.objectid import ObjectId
import bcrypt
from datetime import datetime

# Define auth blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_dashboard(current_user.role)
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        db = get_db()
        user_data = db.users.find_one({"email": email})
        
        if user_data:
            # Check password using bcrypt
            hashed_pw = user_data.get('password_hash')
            if bcrypt.checkpw(password.encode('utf-8'), hashed_pw.encode('utf-8') if isinstance(hashed_pw, str) else hashed_pw):
                user = User(user_data)
                
                # Check status
                if user.role == 'org_admin' and user.status == 'pending':
                    return redirect(url_for('auth.pending_approval'))
                elif user.status == 'suspended':
                    flash("Your account has been suspended. Please contact the administrator.", "danger")
                    return render_template('auth/login.html')
                    
                login_user(user)
                flash(f"Welcome back, {user.name}!", "success")
                return redirect_dashboard(user.role)
                
        flash("Invalid email or password.", "danger")
        
    return render_template('auth/login.html')

@auth_bp.route('/register-org', methods=['GET', 'POST'])
def register_org():
    if current_user.is_authenticated:
        return redirect_dashboard(current_user.role)
        
    if request.method == 'POST':
        org_name = request.form.get('org_name', '').strip()
        org_domain = request.form.get('org_domain', '').strip().lower()
        contact_phone = request.form.get('contact_phone', '').strip()
        address = request.form.get('address', '').strip()
        
        admin_name = request.form.get('admin_name', '').strip()
        admin_email = request.form.get('admin_email', '').strip().lower()
        password = request.form.get('password', '')
        
        db = get_db()
        
        # Check if email or org already exists
        if db.users.find_one({"email": admin_email}):
            flash("Email is already registered.", "danger")
            return render_template('auth/register_org.html')
            
        if db.organizations.find_one({"name": org_name}):
            flash("Organization name is already registered.", "danger")
            return render_template('auth/register_org.html')
            
        # Create organization document (starts as pending)
        org_doc = {
            "name": org_name,
            "domain": org_domain,
            "contact_phone": contact_phone,
            "address": address,
            "logo_url": None, # Will upload later
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        org_result = db.organizations.insert_one(org_doc)
        org_id = org_result.inserted_id
        
        # Hash password using bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        # Create user document
        user_doc = {
            "name": admin_name,
            "email": admin_email,
            "password_hash": hashed_password,
            "role": "org_admin",
            "org_id": org_id,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        db.users.insert_one(user_doc)
        
        flash("Registration submitted successfully! Please wait for Super Admin approval.", "info")
        return redirect(url_for('auth.pending_approval'))
        
    return render_template('auth/register_org.html')

@auth_bp.route('/pending-approval')
def pending_approval():
    return render_template('auth/pending_approval.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully.", "success")
    return redirect(url_for('public.index'))

def redirect_dashboard(role):
    """Helper to redirect authenticated users to their role-specific dashboard."""
    if role == 'super_admin':
        return redirect(url_for('admin.dashboard'))
    elif role == 'org_admin':
        return redirect(url_for('org.dashboard'))
    elif role == 'student':
        return redirect(url_for('student.dashboard'))
    return redirect(url_for('public.index'))
