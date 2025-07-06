from functools import wraps
from flask import session, redirect, url_for, flash, request, current_app
from supabase_client import supabase_client
from models import User
from app import db
import logging

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Validate token with Supabase
        try:
            user_data = supabase_client.get_user(session['access_token'])
            if 'error' in user_data:
                session.clear()
                flash('Session expired. Please log in again.', 'warning')
                return redirect(url_for('auth.login'))
            
            # Store user info in session for easy access
            session['user_email'] = user_data.get('email')
            session['user_id'] = user_data.get('id')
            
        except Exception as e:
            current_app.logger.error(f"Token validation error: {e}")
            session.clear()
            flash('Authentication error. Please log in again.', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_email' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            # Get user from database
            user = User.query.filter_by(email=session['user_email']).first()
            if not user or user.role not in allowed_roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard'))
            
            # Store user in session for easy access
            session['user_role'] = user.role
            session['user_institution_id'] = user.institution_id
            session['user_db_id'] = user.id
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get current user from database"""
    if 'user_email' not in session:
        return None
    return User.query.filter_by(email=session['user_email']).first()

def get_user_institution_filter():
    """Get institution filter for current user"""
    user = get_current_user()
    if not user or user.role == 'admin':
        return {}
    return {'institution_id': user.institution_id}
