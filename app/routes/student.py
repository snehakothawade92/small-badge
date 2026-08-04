from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.db import get_db
from app.decorators import student_required
from bson.objectid import ObjectId

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@student_required
def dashboard():
    db = get_db()
    student_email = current_user.email
    
    # 1. Load student document
    student_record = db.students.find_one({"email": student_email})
    if not student_record:
        return render_template('student/dashboard.html', badges=[])
        
    # 2. Get all badges issued to this student ID
    badges = list(db.issued_badges.aggregate([
        {"$match": {"student_id": student_record['_id'], "status": "issued"}},
        {"$sort": {"issued_date": -1}},
        {
            "$lookup": {
                "from": "courses",
                "localField": "course_id",
                "foreignField": "_id",
                "as": "course"
            }
        },
        {
            "$lookup": {
                "from": "organizations",
                "localField": "org_id",
                "foreignField": "_id",
                "as": "organization"
            }
        },
        {
            "$lookup": {
                "from": "badge_templates",
                "localField": "template_id",
                "foreignField": "_id",
                "as": "template"
            }
        }
    ]))
    
    # Flatten aggregates for template context convenience
    for b in badges:
        b['course_name'] = b['course'][0]['course_name'] if b['course'] else 'N/A'
        b['course_code'] = b['course'][0]['course_code'] if b['course'] else 'N/A'
        b['org_name'] = b['organization'][0]['name'] if b['organization'] else 'N/A'
        b['template_title'] = b['template'][0]['title'] if b['template'] else 'N/A'
        b['border_color'] = b['template'][0].get('border_color', '#f1c40f') if b['template'] else '#f1c40f'
        
    return render_template('student/dashboard.html', 
                           student=student_record,
                           badges=badges)
