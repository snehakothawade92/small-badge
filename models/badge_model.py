import uuid
from datetime import datetime

class Badge:
    def __init__(self, student_name, course, organization):
        self.badge_id = str(uuid.uuid4())[:8]
        self.student_name = student_name
        self.course = course
        self.organization = organization
        self.issue_date = datetime.now().strftime('%d-%m-%Y')

    def to_dict(self):
        return {
            'badge_id': self.badge_id,
            'student_name': self.student_name,
            'course': self.course,
            'organization': self.organization,
            'issue_date': self.issue_date
        }