from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from supabase_client import supabase_client
from models import User, Institution
from app import db
from utils.validators import validate_email, validate_password, sanitize_input
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        
        if not validate_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('login.html')
        
        try:
            # Authenticate with Supabase
            response = supabase_client.sign_in(email, password)
            logging.info(f"Supabase login response: {response}")
            
            if 'error' in response:
                error_msg = response.get('error', {}).get('message', 'Invalid email or password.')
                flash(f'Login failed: {error_msg}', 'error')
                return render_template('login.html')
            
            # Store session data
            session['access_token'] = response.get('access_token')
            session['refresh_token'] = response.get('refresh_token')
            session['user_email'] = email
            
            # Get or create user in local database
            user = User.query.filter_by(email=email).first()
            if not user:
                # Create user if doesn't exist
                supabase_user_data = supabase_client.get_user(response['access_token'])
                user = User(
                    email=email,
                    name=email.split('@')[0],  # Default name from email
                    role='student',  # Default role
                    supabase_user_id=supabase_user_data.get('id', '')
                )
                db.session.add(user)
                db.session.commit()
            
            # Store user data in session
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_name'] = user.name
            session['institution_id'] = user.institution_id
            session['department_id'] = user.department_id
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logging.error(f"Login error: {e}")
            flash('Login failed. Please try again.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        name = sanitize_input(request.form.get('name', ''))
        
        # Validation
        errors = []
        
        if not validate_email(email):
            errors.append('Please enter a valid email address.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        password_validation = validate_password(password)
        if not password_validation['is_valid']:
            errors.extend(password_validation['errors'])
        
        if not name or len(name.strip()) < 2:
            errors.append('Name must be at least 2 characters long.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('signup.html')
        
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('An account with this email already exists.', 'error')
                return render_template('signup.html')
            
            # Sign up with Supabase
            response = supabase_client.sign_up(email, password)
            logging.info(f"Supabase signup response: {response}")
            
            if 'error' in response:
                error_msg = response.get('error', {}).get('message', 'Signup failed.')
                # Handle specific Supabase email validation issues
                if 'email_address_invalid' in error_msg:
                    flash('Please use a valid email address. Some email formats may not be supported.', 'error')
                else:
                    flash(f'Signup failed: {error_msg}', 'error')
                return render_template('signup.html')
            
            # Create user in local database
            user = User(
                email=email,
                name=name,
                role='student',  # Default role
                supabase_user_id=response.get('user', {}).get('id', '')
            )
            db.session.add(user)
            db.session.commit()
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logging.error(f"Signup error: {e}")
            flash('Signup failed. Please try again.', 'error')
    
    return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    try:
        if 'access_token' in session:
            supabase_client.sign_out(session['access_token'])
    except Exception as e:
        logging.error(f"Logout error: {e}")
    
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
def profile():
    from auth import login_required, get_current_user
    
    @login_required
    def _profile():
        user = get_current_user()
        institutions = Institution.query.all()
        return render_template('profile.html', user=user, institutions=institutions)
    
    return _profile()

@auth_bp.route('/profile/update', methods=['POST'])
def update_profile():
    from auth import login_required, get_current_user
    
    @login_required
    def _update_profile():
        user = get_current_user()
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.profile'))
        
        name = sanitize_input(request.form.get('name', ''))
        institution_id = request.form.get('institution_id')
        
        if not name or len(name.strip()) < 2:
            flash('Name must be at least 2 characters long.', 'error')
            return redirect(url_for('auth.profile'))
        
        try:
            user.name = name
            if institution_id and institution_id.isdigit():
                user.institution_id = int(institution_id)
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            logging.error(f"Profile update error: {e}")
            flash('Failed to update profile.', 'error')
        
        return redirect(url_for('auth.profile'))
    
    return _update_profile()
