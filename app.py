import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///timetable.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    db.create_all()

# Import and register blueprints
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.timetable_routes import timetable_bp
from routes.export_routes import export_bp
from routes.ai_routes import ai_bp
from routes.demo_routes import demo_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(timetable_bp, url_prefix='/timetable')
app.register_blueprint(export_bp, url_prefix='/export')
app.register_blueprint(ai_bp, url_prefix='/ai')
app.register_blueprint(demo_bp, url_prefix='/demo')

# Main route
from flask import render_template, redirect, url_for
from auth import login_required

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
