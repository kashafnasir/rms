from flask import Flask
from extensions import db, login_manager, migrate
import os

def create_app():
    """Application factory to create and configure the Flask app"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_management.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    with app.app_context():
        # Import models
        from models import User
        
        # User loader for Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Import and register routes
        import routes
        
        # Create all database tables
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)