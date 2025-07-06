from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from auth import login_required, role_required, get_current_user, get_user_institution_filter
from models import Institution, Department, Teacher, Course, Room, TimeSlot
from app import db
from utils.validators import (validate_required_fields, sanitize_input, 
                             validate_time_format, validate_course_code, validate_room_capacity)
from datetime import time
import logging

admin_bp = Blueprint('admin', __name__)

# Institutions
@admin_bp.route('/institutions')
@login_required
@role_required('admin')
def institutions():
    institutions = Institution.query.all()
    return render_template('admin/institutions.html', institutions=institutions)

@admin_bp.route('/institutions/add', methods=['POST'])
@login_required
@role_required('admin')
def add_institution():
    name = sanitize_input(request.form.get('name', ''))
    code = sanitize_input(request.form.get('code', ''))
    address = sanitize_input(request.form.get('address', ''))
    
    errors = validate_required_fields(request.form, ['name', 'code'])
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('admin.institutions'))
    
    try:
        institution = Institution(name=name, code=code.upper(), address=address)
        db.session.add(institution)
        db.session.commit()
        flash('Institution added successfully!', 'success')
    except Exception as e:
        logging.error(f"Add institution error: {e}")
        flash('Failed to add institution.', 'error')
    
    return redirect(url_for('admin.institutions'))

# Departments
@admin_bp.route('/departments')
@login_required
@role_required('admin', 'faculty')
def departments():
    user_filter = get_user_institution_filter()
    query = Department.query
    if user_filter:
        query = query.filter_by(**user_filter)
    departments = query.all()
    institutions = Institution.query.all()
    return render_template('admin/departments.html', departments=departments, institutions=institutions)

@admin_bp.route('/departments/add', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def add_department():
    name = sanitize_input(request.form.get('name', ''))
    code = sanitize_input(request.form.get('code', ''))
    institution_id = request.form.get('institution_id')
    
    errors = validate_required_fields(request.form, ['name', 'code', 'institution_id'])
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('admin.departments'))
    
    try:
        department = Department(
            name=name, 
            code=code.upper(), 
            institution_id=int(institution_id)
        )
        db.session.add(department)
        db.session.commit()
        flash('Department added successfully!', 'success')
    except Exception as e:
        logging.error(f"Add department error: {e}")
        flash('Failed to add department.', 'error')
    
    return redirect(url_for('admin.departments'))

# Teachers
@admin_bp.route('/teachers')
@login_required
@role_required('admin', 'faculty')
def teachers():
    user_filter = get_user_institution_filter()
    query = Teacher.query
    if user_filter:
        query = query.filter_by(**user_filter)
    teachers = query.all()
    
    departments_query = Department.query
    if user_filter:
        departments_query = departments_query.filter_by(**user_filter)
    departments = departments_query.all()
    
    return render_template('admin/teachers.html', teachers=teachers, departments=departments)

@admin_bp.route('/teachers/add', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def add_teacher():
    name = sanitize_input(request.form.get('name', ''))
    email = sanitize_input(request.form.get('email', ''))
    employee_id = sanitize_input(request.form.get('employee_id', ''))
    department_id = request.form.get('department_id')
    max_hours = request.form.get('max_hours_per_week', 40)
    
    errors = validate_required_fields(request.form, ['name', 'email', 'employee_id', 'department_id'])
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('admin.teachers'))
    
    try:
        # Get department to get institution_id
        department = Department.query.get(int(department_id))
        if not department:
            flash('Invalid department selected.', 'error')
            return redirect(url_for('admin.teachers'))
        
        teacher = Teacher(
            name=name,
            email=email,
            employee_id=employee_id,
            department_id=int(department_id),
            institution_id=department.institution_id,
            max_hours_per_week=int(max_hours)
        )
        db.session.add(teacher)
        db.session.commit()
        flash('Teacher added successfully!', 'success')
    except Exception as e:
        logging.error(f"Add teacher error: {e}")
        flash('Failed to add teacher.', 'error')
    
    return redirect(url_for('admin.teachers'))

# Courses
@admin_bp.route('/courses')
@login_required
@role_required('admin', 'faculty')
def courses():
    user_filter = get_user_institution_filter()
    query = Course.query
    if user_filter:
        query = query.filter_by(**user_filter)
    courses = query.all()
    
    departments_query = Department.query
    if user_filter:
        departments_query = departments_query.filter_by(**user_filter)
    departments = departments_query.all()
    
    return render_template('admin/courses.html', courses=courses, departments=departments)

@admin_bp.route('/courses/add', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def add_course():
    name = sanitize_input(request.form.get('name', ''))
    code = sanitize_input(request.form.get('code', ''))
    credits = request.form.get('credits')
    department_id = request.form.get('department_id')
    semester = sanitize_input(request.form.get('semester', ''))
    year = request.form.get('year')
    student_count = request.form.get('student_count', 0)
    
    errors = validate_required_fields(request.form, ['name', 'code', 'credits', 'department_id', 'semester', 'year'])
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('admin.courses'))
    
    if not validate_course_code(code):
        flash('Invalid course code format.', 'error')
        return redirect(url_for('admin.courses'))
    
    try:
        # Get department to get institution_id
        department = Department.query.get(int(department_id))
        if not department:
            flash('Invalid department selected.', 'error')
            return redirect(url_for('admin.courses'))
        
        course = Course(
            name=name,
            code=code.upper(),
            credits=int(credits),
            department_id=int(department_id),
            institution_id=department.institution_id,
            semester=semester,
            year=int(year),
            student_count=int(student_count)
        )
        db.session.add(course)
        db.session.commit()
        flash('Course added successfully!', 'success')
    except Exception as e:
        logging.error(f"Add course error: {e}")
        flash('Failed to add course.', 'error')
    
    return redirect(url_for('admin.courses'))

# Rooms
@admin_bp.route('/rooms')
@login_required
@role_required('admin', 'faculty')
def rooms():
    user_filter = get_user_institution_filter()
    query = Room.query
    if user_filter:
        query = query.filter_by(**user_filter)
    rooms = query.all()
    
    institutions = Institution.query.all()
    return render_template('admin/rooms.html', rooms=rooms, institutions=institutions)

@admin_bp.route('/rooms/add', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def add_room():
    name = sanitize_input(request.form.get('name', ''))
    code = sanitize_input(request.form.get('code', ''))
    capacity = request.form.get('capacity')
    room_type = sanitize_input(request.form.get('room_type', ''))
    building = sanitize_input(request.form.get('building', ''))
    floor = sanitize_input(request.form.get('floor', ''))
    institution_id = request.form.get('institution_id')
    
    errors = validate_required_fields(request.form, ['name', 'code', 'capacity', 'room_type', 'institution_id'])
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('admin.rooms'))
    
    if not validate_room_capacity(capacity):
        flash('Invalid room capacity.', 'error')
        return redirect(url_for('admin.rooms'))
    
    try:
        room = Room(
            name=name,
            code=code.upper(),
            capacity=int(capacity),
            room_type=room_type,
            building=building,
            floor=floor,
            institution_id=int(institution_id)
        )
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')
    except Exception as e:
        logging.error(f"Add room error: {e}")
        flash('Failed to add room.', 'error')
    
    return redirect(url_for('admin.rooms'))

# Time Slots
@admin_bp.route('/timeslots')
@login_required
@role_required('admin', 'faculty')
def timeslots():
    user_filter = get_user_institution_filter()
    query = TimeSlot.query
    if user_filter:
        query = query.filter_by(**user_filter)
    timeslots = query.order_by(TimeSlot.day_of_week, TimeSlot.start_time).all()
    
    institutions = Institution.query.all()
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    return render_template('admin/timeslots.html', timeslots=timeslots, institutions=institutions, days_of_week=days_of_week)

@admin_bp.route('/timeslots/add', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def add_timeslot():
    day_of_week = request.form.get('day_of_week')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    period_name = sanitize_input(request.form.get('period_name', ''))
    institution_id = request.form.get('institution_id')
    
    errors = validate_required_fields(request.form, ['day_of_week', 'start_time', 'end_time', 'institution_id'])
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('admin.timeslots'))
    
    if not validate_time_format(start_time) or not validate_time_format(end_time):
        flash('Invalid time format. Use HH:MM format.', 'error')
        return redirect(url_for('admin.timeslots'))
    
    try:
        start_time_obj = time(*map(int, start_time.split(':')))
        end_time_obj = time(*map(int, end_time.split(':')))
        
        if start_time_obj >= end_time_obj:
            flash('End time must be after start time.', 'error')
            return redirect(url_for('admin.timeslots'))
        
        timeslot = TimeSlot(
            day_of_week=int(day_of_week),
            start_time=start_time_obj,
            end_time=end_time_obj,
            period_name=period_name,
            institution_id=int(institution_id)
        )
        db.session.add(timeslot)
        db.session.commit()
        flash('Time slot added successfully!', 'success')
    except Exception as e:
        logging.error(f"Add timeslot error: {e}")
        flash('Failed to add time slot.', 'error')
    
    return redirect(url_for('admin.timeslots'))

# Delete operations
@admin_bp.route('/delete/<model>/<int:item_id>', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def delete_item(model, item_id):
    try:
        model_map = {
            'institution': Institution,
            'department': Department,
            'teacher': Teacher,
            'course': Course,
            'room': Room,
            'timeslot': TimeSlot
        }
        
        if model not in model_map:
            flash('Invalid item type.', 'error')
            return redirect(url_for('admin.departments'))
        
        item = model_map[model].query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        flash(f'{model.title()} deleted successfully!', 'success')
        
    except Exception as e:
        logging.error(f"Delete {model} error: {e}")
        flash(f'Failed to delete {model}.', 'error')
    
    return redirect(url_for(f'admin.{model}s'))
