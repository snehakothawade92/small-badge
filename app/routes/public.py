from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.db import get_db
from bson.objectid import ObjectId

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Renders the main public landing page where badge lookups occur."""
    return render_template('public/index.html')

@public_bp.route('/verify', methods=['GET', 'POST'])
def verify_badge_post():
    """Handles Badge ID search submissions."""
    if request.method == 'POST':
        badge_id = request.form.get('badge_id', '').strip()
        if not badge_id:
            flash("Please enter a Badge ID.", "warning")
            return redirect(url_for('public.index'))
        return redirect(url_for('public.verify_badge', badge_id=badge_id))
    return redirect(url_for('public.index'))

@public_bp.route('/verify/<badge_id>')
def verify_badge(badge_id):
    """
    Looks up a specific Badge ID in the database and renders validation status.
    This handles both manual input and QR Code redirections.
    """
    db = get_db()
    badge = db.issued_badges.find_one({"badge_id": badge_id})
    
    if not badge:
        return render_template('public/verify_result.html', verified=False, badge_id=badge_id)
        
    # Fetch related documents from MongoDB
    student = db.students.find_one({"_id": ObjectId(badge['student_id'])})
    course = db.courses.find_one({"_id": ObjectId(badge['course_id'])})
    organization = db.organizations.find_one({"_id": ObjectId(badge['org_id'])})
    template = db.badge_templates.find_one({"_id": ObjectId(badge['template_id'])})
    
    return render_template('public/verify_result.html', 
                           verified=True, 
                           badge=badge, 
                           student=student, 
                           course=course, 
                           organization=organization,
                           template=template)
