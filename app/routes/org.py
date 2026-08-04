from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.db import get_db
from app.decorators import org_required
from bson.objectid import ObjectId
import pandas as pd
import os
import hashlib
import qrcode
import bcrypt
from datetime import datetime
from app.email import send_badge_email
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

org_bp = Blueprint('org', __name__, url_prefix='/org')

@org_bp.route('/dashboard')
@org_required
def dashboard():
    db = get_db()
    org_id = current_user.org_id
    
    courses_count = db.courses.count_documents({"org_id": org_id})
    students_count = db.students.count_documents({"org_id": org_id})
    templates_count = db.badge_templates.count_documents({"org_id": org_id})
    badges_issued = db.issued_badges.count_documents({"org_id": org_id})
    
    recent_badges = list(db.issued_badges.aggregate([
        {"$match": {"org_id": org_id}},
        {"$sort": {"issued_date": -1}},
        {"$limit": 5},
        {
            "$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "_id",
                "as": "student"
            }
        },
        {
            "$lookup": {
                "from": "courses",
                "localField": "course_id",
                "foreignField": "_id",
                "as": "course"
            }
        }
    ]))
    
    return render_template('org/dashboard.html',
                           courses_count=courses_count,
                           students_count=students_count,
                           templates_count=templates_count,
                           badges_issued=badges_issued,
                           recent_badges=recent_badges)

# --- COURSE MANAGEMENT ---
@org_bp.route('/courses', methods=['GET', 'POST'])
@org_required
def courses():
    db = get_db()
    org_id = current_user.org_id
    
    if request.method == 'POST':
        code = request.form.get('course_code', '').strip().upper()
        name = request.form.get('course_name', '').strip()
        desc = request.form.get('description', '').strip()
        
        if not code or not name:
            flash("Course Code and Course Name are required.", "danger")
        else:
            # Check for existing course in this org
            existing = db.courses.find_one({"org_id": org_id, "course_code": code})
            if existing:
                flash(f"Course code {code} already exists.", "warning")
            else:
                db.courses.insert_one({
                    "org_id": org_id,
                    "course_code": code,
                    "course_name": name,
                    "description": desc,
                    "created_at": datetime.utcnow()
                })
                flash("Course added successfully!", "success")
                return redirect(url_for('org.courses'))
                
    all_courses = list(db.courses.find({"org_id": org_id}))
    return render_template('org/courses.html', courses=all_courses)

# --- STUDENT MANAGEMENT & CSV BATCH IMPORT ---
@org_bp.route('/students', methods=['GET', 'POST'])
@org_required
def students():
    db = get_db()
    org_id = current_user.org_id
    
    if request.method == 'POST':
        # Single Student Import
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        roll = request.form.get('roll_number', '').strip()
        
        if not name or not email or not roll:
            flash("All student fields are required.", "danger")
        else:
            existing = db.students.find_one({"org_id": org_id, "email": email})
            if existing:
                flash(f"Student with email {email} is already registered.", "warning")
            else:
                db.students.insert_one({
                    "org_id": org_id,
                    "name": name,
                    "email": email,
                    "roll_number": roll,
                    "created_at": datetime.utcnow()
                })
                flash("Student added successfully!", "success")
                return redirect(url_for('org.students'))
                
    all_students = list(db.students.find({"org_id": org_id}))
    return render_template('org/students.html', students=all_students)

@org_bp.route('/students/import-csv', methods=['POST'])
@org_required
def import_students_csv():
    if 'csv_file' not in request.files:
        flash("No file part selected.", "danger")
        return redirect(url_for('org.students'))
        
    file = request.files['csv_file']
    if file.filename == '':
        flash("No file selected.", "danger")
        return redirect(url_for('org.students'))
        
    if not file.filename.endswith('.csv'):
        flash("Please upload a valid CSV file.", "danger")
        return redirect(url_for('org.students'))
        
    try:
        # Load CSV using pandas
        df = pd.read_csv(file)
        
        # Verify required columns exist
        required_cols = {'name', 'email', 'roll_number'}
        if not required_cols.issubset(set(df.columns)):
            flash("CSV must contain columns: 'name', 'email', 'roll_number'", "danger")
            return redirect(url_for('org.students'))
            
        db = get_db()
        org_id = current_user.org_id
        import_count = 0
        duplicate_count = 0
        
        for _, row in df.iterrows():
            name = str(row['name']).strip()
            email = str(row['email']).strip().lower()
            roll = str(row['roll_number']).strip()
            
            # Skip empty lines
            if not name or not email or not roll:
                continue
                
            # Check duplicate in this organization
            existing = db.students.find_one({"org_id": org_id, "email": email})
            if existing:
                duplicate_count += 1
                continue
                
            db.students.insert_one({
                "org_id": org_id,
                "name": name,
                "email": email,
                "roll_number": roll,
                "created_at": datetime.utcnow()
            })
            import_count += 1
            
        flash(f"Import completed! Successfully added {import_count} students. (Ignored {duplicate_count} duplicates)", "success")
    except Exception as e:
        flash(f"Error processing CSV file: {str(e)}", "danger")
        
    return redirect(url_for('org.students'))

# --- BADGE TEMPLATE MANAGEMENT ---
@org_bp.route('/templates', methods=['GET', 'POST'])
@org_required
def templates():
    db = get_db()
    org_id = current_user.org_id
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        desc = request.form.get('badge_description', '').strip()
        font_color = request.form.get('font_color', '#1a252f')
        border_color = request.form.get('border_color', '#f1c40f')
        
        if not title:
            flash("Template Title is required.", "danger")
        else:
            db.badge_templates.insert_one({
                "org_id": org_id,
                "title": title,
                "badge_description": desc,
                "font_color": font_color,
                "border_color": border_color,
                "created_at": datetime.utcnow()
            })
            flash("Badge Template designed successfully!", "success")
            return redirect(url_for('org.templates'))
            
    all_templates = list(db.badge_templates.find({"org_id": org_id}))
    return render_template('org/templates.html', templates=all_templates)

# --- BADGE ISSUANCE ---
@org_bp.route('/issue-badge', methods=['GET', 'POST'])
@org_required
def issue_badge():
    db = get_db()
    org_id = current_user.org_id
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        template_id = request.form.get('template_id')
        
        if not student_id or not course_id or not template_id:
            flash("All fields are required to issue a badge.", "danger")
        else:
            # Check if this student already has this badge
            duplicate = db.issued_badges.find_one({
                "org_id": org_id,
                "student_id": ObjectId(student_id),
                "course_id": ObjectId(course_id)
            })
            
            if duplicate:
                flash("This badge has already been issued to the selected student for this course.", "warning")
            else:
                # Generate cryptographically secure Unique Badge ID
                raw_hash_string = f"{student_id}-{course_id}-{template_id}-{datetime.utcnow()}"
                badge_id = hashlib.sha256(raw_hash_string.encode('utf-8')).hexdigest()
                
                # Setup output folders for dynamic assets
                upload_dir = current_app.config['UPLOAD_FOLDER']
                qrcodes_dir = os.path.join(upload_dir, 'qrcodes')
                pdfs_dir = os.path.join(upload_dir, 'pdfs')
                os.makedirs(qrcodes_dir, exist_ok=True)
                os.makedirs(pdfs_dir, exist_ok=True)
                
                # 1. Generate QR Code containing public verification link
                verify_url = url_for('public.verify_badge', badge_id=badge_id, _external=True)
                qr = qrcode.QRCode(version=1, box_size=10, border=1)
                qr.add_data(verify_url)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                qr_filename = f"{badge_id}.png"
                qr_filepath = os.path.join(qrcodes_dir, qr_filename)
                qr_img.save(qr_filepath)
                
                # 2. Fetch templates & records to create PDF Certificate
                student_record = db.students.find_one({"_id": ObjectId(student_id)})
                course_record = db.courses.find_one({"_id": ObjectId(course_id)})
                template_record = db.badge_templates.find_one({"_id": ObjectId(template_id)})
                org_record = db.organizations.find_one({"_id": ObjectId(org_id)})
                
                pdf_filename = f"{badge_id}.pdf"
                pdf_filepath = os.path.join(pdfs_dir, pdf_filename)
                
                # Render PDF using ReportLab
                generate_certificate_pdf(
                    filepath=pdf_filepath,
                    student_name=student_record['name'],
                    course_name=course_record['course_name'],
                    org_name=org_record['name'],
                    date_str=datetime.utcnow().strftime("%B %d, %Y"),
                    badge_id=badge_id,
                    qr_image_path=qr_filepath,
                    border_color=template_record.get('border_color', '#f1c40f')
                )
                
                # 3. Create Student User if they don't already exist
                # This lets them login using their email to access their portfolio
                student_user = db.users.find_one({"email": student_record['email']})
                if not student_user:
                    # Generate a default password which is student roll number
                    default_pw = student_record['roll_number'].strip()
                    salt = bcrypt.gensalt()
                    hashed_pw = bcrypt.hashpw(default_pw.encode('utf-8'), salt).decode('utf-8')
                    
                    db.users.insert_one({
                        "name": student_record['name'],
                        "email": student_record['email'],
                        "password_hash": hashed_pw,
                        "role": "student",
                        "org_id": org_id,
                        "status": "active",
                        "created_at": datetime.utcnow()
                    })
                
                # 4. Insert Issued Badge details
                db.issued_badges.insert_one({
                    "badge_id": badge_id,
                    "org_id": org_id,
                    "student_id": ObjectId(student_id),
                    "course_id": ObjectId(course_id),
                    "template_id": ObjectId(template_id),
                    "issued_date": datetime.utcnow(),
                    "qr_code_path": f"/static/uploads/qrcodes/{qr_filename}",
                    "pdf_path": f"/static/uploads/pdfs/{pdf_filename}",
                    "status": "issued"
                })
                
                # 5. Insert audit log
                db.activity_logs.insert_one({
                    "timestamp": datetime.utcnow(),
                    "user_id": ObjectId(current_user.id),
                    "role": "org_admin",
                    "action": "ISSUE_BADGE",
                    "details": f"Issued badge to student: {student_record['name']}, course: {course_record['course_name']}",
                    "ip_address": request.remote_addr
                })
                
                # 6. Trigger Email Notification to the Student
                send_badge_email(
                    recipient_email=student_record['email'],
                    recipient_name=student_record['name'],
                    course_name=course_record['course_name'],
                    org_name=org_record['name'],
                    verify_url=verify_url,
                    pdf_path=pdf_filepath
                )
                
                flash("Badge issued successfully! A Student Login has been created using their roll number.", "success")
                return redirect(url_for('org.dashboard'))
                
    students_list = list(db.students.find({"org_id": org_id}))
    courses_list = list(db.courses.find({"org_id": org_id}))
    templates_list = list(db.badge_templates.find({"org_id": org_id}))
    return render_template('org/issue_badge.html', 
                           students=students_list, 
                           courses=courses_list, 
                           templates=templates_list)

@org_bp.route('/revoke-badge/<badge_id>')
@org_required
def revoke_badge(badge_id):
    db = get_db()
    org_id = current_user.org_id
    
    # Confirm badge exists in this organization
    badge = db.issued_badges.find_one({"badge_id": badge_id, "org_id": org_id})
    if not badge:
        flash("Badge not found.", "danger")
        return redirect(url_for('org.dashboard'))
        
    db.issued_badges.update_one(
        {"badge_id": badge_id},
        {"$set": {"status": "revoked"}}
    )
    
    # Log the action
    db.activity_logs.insert_one({
        "timestamp": datetime.utcnow(),
        "user_id": ObjectId(current_user.id),
        "role": "org_admin",
        "action": "REVOKE_BADGE",
        "details": f"Revoked badge: {badge_id}",
        "ip_address": request.remote_addr
    })
    
    flash("Badge has been successfully revoked.", "warning")
    return redirect(url_for('org.dashboard'))

# --- HELPER FUNCTIONS FOR REPORTLAB PDF GENERATION ---
def hex_to_rgb(hex_str):
    """Converts hex color (e.g. #f1c40f) to reportlab-friendly fraction RGB tuple."""
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def generate_certificate_pdf(filepath, student_name, course_name, org_name, date_str, badge_id, qr_image_path, border_color):
    """
    Generates a landscape certificate PDF containing verified metadata and verification QR.
    """
    # Create landscape letter size canvas
    c = canvas.Canvas(filepath, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Background Border
    c.setStrokeColorRGB(*hex_to_rgb(border_color))
    c.setLineWidth(15)
    c.rect(15, 15, width - 30, height - 30)
    
    # Inner thin border
    c.setLineWidth(2)
    c.rect(25, 25, width - 50, height - 50)
    
    # Typography
    c.setFont("Helvetica-Bold", 34)
    c.setFillColorRGB(0.12, 0.16, 0.24) # #1e293b
    c.drawCentredString(width / 2.0, height - 100, "DIGITAL ACHIEVEMENT BADGE")
    
    c.setFont("Helvetica", 14)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width / 2.0, height - 140, "This is to verify that the following student is awarded the digital credential")
    
    # Student Name
    c.setFont("Helvetica-Bold", 28)
    c.setFillColorRGB(0.85, 0.47, 0.02) # gold-ish orange
    c.drawCentredString(width / 2.0, height - 200, student_name.upper())
    
    # Achievement Description
    c.setFont("Helvetica", 14)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.drawCentredString(width / 2.0, height - 240, f"for successful completion of the certification course")
    
    # Course Name
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0.12, 0.16, 0.24)
    c.drawCentredString(width / 2.0, height - 285, course_name)
    
    # Issuer Organization
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2.0, height - 330, f"Issued by: {org_name}")
    
    # Issuance Date
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawCentredString(width / 2.0, height - 365, f"Date: {date_str}")
    
    # Badge ID text
    c.setFont("Courier", 9)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width / 2.0, 50, f"Credential Verification Link ID: {badge_id}")
    
    # Draw QR code image on the bottom right
    c.drawImage(qr_image_path, width - 150, 45, width=100, height=100)
    
    # Save the canvas
    c.showPage()
    c.save()
