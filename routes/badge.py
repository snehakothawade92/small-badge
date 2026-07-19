from flask import Blueprint, render_template, request
from config import mongo

badge = Blueprint('badge', __name__)

@badge.route('/issue-badge', methods=['GET', 'POST'])
def issue_badge():

    if request.method == 'POST':

        badge_data = {
            'student_name': request.form['student_name'],
            'course': request.form['course'],
            'organization': request.form['organization']
        }

        # Save into MongoDB
        mongo.db.badges.insert_one(badge_data)

        return 'Badge saved successfully!'

    return render_template('issue_badge.html')