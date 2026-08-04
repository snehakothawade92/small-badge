from flask_mail import Mail, Message
from flask import current_app
import logging

# Global mail instance
mail = Mail()

def init_mail(app):
    """Initializes Flask-Mail extension."""
    mail.init_app(app)

def send_badge_email(recipient_email, recipient_name, course_name, org_name, verify_url, pdf_path=None):
    """
    Sends a secure digital badge notification email to the recipient.
    Catches all exceptions to prevent application crashes if SMTP is offline.
    """
    try:
        # Check if username config is set, otherwise skip actual sending in local dev mode
        if not current_app.config.get('MAIL_USERNAME'):
            current_app.logger.warning(
                f"SMTP username is not configured in .env. Skipping actual mail dispatch to {recipient_email}."
            )
            return False
            
        subject = f"Congratulations! Your Digital Badge for {course_name} is Ready"
        
        # HTML Message Body
        html_content = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px;">
            <h2 style="color: #d97706; border-bottom: 2px solid #f1c40f; padding-bottom: 10px;">Digital Credential Issued</h2>
            <p>Dear <strong>{recipient_name}</strong>,</p>
            <p>We are pleased to inform you that <strong>{org_name}</strong> has issued you a digital achievement badge for successfully completing the program:</p>
            
            <div style="background-color: #f8fafc; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #d97706; text-align: center;">
                <span style="font-size: 1.1rem; font-weight: bold; color: #1e293b;">{course_name}</span>
            </div>
            
            <p>You can instantly view, verify, and share this badge on your social profiles using the link below:</p>
            <div style="text-align: center; margin: 25px 0;">
                <a href="{verify_url}" style="background-color: #d97706; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Verify Badge Credential</a>
            </div>
            
            <p style="font-size: 0.9rem; color: #64748b;">
                <strong>Student Login Note:</strong> You can log into your Student Dashboard using your registered email and your Roll Number as the default password.
            </p>
            <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
            <p style="font-size: 0.8rem; color: #94a3b8; text-align: center;">Powered by SmallBadge Platform &copy; 2026</p>
        </div>
        """
        
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=html_content
        )
        
        # Attach PDF certificate if path is provided
        if pdf_path:
            with current_app.open_resource(pdf_path) as fp:
                msg.attach(
                    filename="Digital_Certificate.pdf",
                    content_type="application/pdf",
                    data=fp.read()
                )
                
        mail.send(msg)
        current_app.logger.info(f"Successfully dispatched badge notification email to: {recipient_email}")
        return True
        
    except Exception as e:
        # Logs the exception, but doesn't halt the flow
        current_app.logger.error(f"Failed to dispatch badge notification email to {recipient_email}. Reason: {str(e)}")
        return False
