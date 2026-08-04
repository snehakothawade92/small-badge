from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.db import get_db
from app.decorators import admin_required
from bson.objectid import ObjectId

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    db = get_db()
    
    # Calculate stats for analytics counters
    orgs_count = db.organizations.count_documents({})
    badges_count = db.issued_badges.count_documents({})
    users_count = db.users.count_documents({})
    
    # Get pending approval requests
    pending_orgs = list(db.organizations.find({"status": "pending"}))
    
    # Get approved organizations
    approved_orgs = list(db.organizations.find({"status": "approved"}))
    
    return render_template('admin/dashboard.html', 
                           orgs_count=orgs_count, 
                           badges_count=badges_count, 
                           users_count=users_count, 
                           pending_orgs=pending_orgs,
                           approved_orgs=approved_orgs)

@admin_bp.route('/approve-org/<org_id>')
@admin_required
def approve_org(org_id):
    db = get_db()
    
    # Update organization status
    db.organizations.update_one(
        {"_id": ObjectId(org_id)},
        {"$set": {"status": "approved"}}
    )
    
    # Update organization admin user status to active
    db.users.update_one(
        {"org_id": ObjectId(org_id), "role": "org_admin"},
        {"$set": {"status": "active"}}
    )
    
    flash("Organization approved successfully!", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/suspend-org/<org_id>')
@admin_required
def suspend_org(org_id):
    db = get_db()
    
    # Suspend organization
    db.organizations.update_one(
        {"_id": ObjectId(org_id)},
        {"$set": {"status": "suspended"}}
    )
    
    # Suspend organization admin user
    db.users.update_one(
        {"org_id": ObjectId(org_id), "role": "org_admin"},
        {"$set": {"status": "suspended"}}
    )
    
    flash("Organization suspended successfully.", "warning")
    return redirect(url_for('admin.dashboard'))
