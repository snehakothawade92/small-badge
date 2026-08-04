from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from app.db import init_db, User
from app.email import init_mail

# Initialize Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    """Callback to load User object from database based on session ID."""
    return User.get_by_id(user_id)

def create_app():
    """
    Application Factory pattern to initialize Flask app with all blueprints and DB hooks.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize Database Connection
    init_db(app)
    
    # Initialize Mail Client
    init_mail(app)
    
    # Initialize Flask-Login session management
    login_manager.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.org import org_bp
    from app.routes.student import student_bp
    from app.routes.public import public_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(public_bp)
    
    # Error pages custom templates
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
        
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404
        
    return app
