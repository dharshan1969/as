from .auth_routes import auth_bp
from .admin_routes import admin_bp
from .timetable_routes import timetable_bp
from .export_routes import export_bp

__all__ = ['auth_bp', 'admin_bp', 'timetable_bp', 'export_bp']
