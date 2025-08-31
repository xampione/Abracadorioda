import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the SQLite database
database_url = os.environ.get("DATABASE_URL", "sqlite:///frantoio.db")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Per accedere a questa pagina devi effettuare il login.'
login_manager.login_message_category = 'warning'

with app.app_context():
    # Import models to ensure tables are created
    import models
    
    # Create all tables
    db.create_all()
    
    # Create default admin user if not exists
    from models import User
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin = User(username='admin', ruolo='completo')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create limited user for sezioni 1-2
        limited_user = User(username='operatore', ruolo='limitato')
        limited_user.set_password('operatore123')
        db.session.add(limited_user)
        
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Import routes after app context setup to avoid circular imports
import routes

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
