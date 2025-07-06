from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from auth import login_required, role_required, get_current_user, get_user_institution_filter
from models import TimetableEntry, Course, Teacher, Room, TimeSlot, Department
from scheduler import generate_timetable_for_institution
from app import db
import logging

timetable_bp = Blueprint('timetable', __name__)

@timetable_bp.route('/')
@login_required
def view_timetable():
    user = get_current_user()
    user_filter = get_user_institution_filter()
    
    # Get timetable entries
    query = TimetableEntry.query
    if user_filter:
        query = query.filter_by(**user_filter)
    
    # Filter by department for faculty
    if user.role == 'faculty' and user.department_id:
        query = query.join(Course).filter(Course.department_id == user.department_id)
    
    timetable_entries = query.all()
    
    # Get time slots for display
    timeslots_query = TimeSlot.query
    if user_filter:
        timeslots_query = timeslots_query.filter_by(**user_filter)
    timeslots = timeslots_query.order_by(TimeSlot.day_of_week, TimeSlot.start_time).all()
    
    # Organize timetable data for display
    timetable_grid = {}
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for entry in timetable_entries:
        day = days_of_week[entry.timeslot.day_of_week]
        time_key = f"{entry.timeslot.start_time.strftime('%H:%M')}-{entry.timeslot.end_time.strftime('%H:%M')}"
        
        if day not in timetable_grid:
            timetable_grid[day] = {}
        
        timetable_grid[day][time_key] = {
            'entry': entry,
            'course': entry.course,
            'teacher': entry.teacher,
            'room': entry.room
        }
    
    # Get departments for admin/faculty
    departments = []
    if user.role in ['admin', 'faculty']:
        departments_query = Department.query
        if user_filter:
            departments_query = departments_query.filter_by(**user_filter)
        departments = departments_query.all()
    
    return render_template('timetable.html', 
                         timetable_grid=timetable_grid,
                         timeslots=timeslots,
                         days_of_week=days_of_week,
                         departments=departments,
                         user=user)

@timetable_bp.route('/generate', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def generate_timetable():
    user = get_current_user()
    department_id = request.form.get('department_id')
    
    if not user.institution_id:
        flash('You must be associated with an institution to generate timetables.', 'error')
        return redirect(url_for('timetable.view_timetable'))
    
    # Faculty can only generate for their department
    if user.role == 'faculty':
        department_id = user.department_id
    
    try:
        result = generate_timetable_for_institution(
            user.institution_id, 
            int(department_id) if department_id else None
        )
        
        if result['success']:
            flash(result['message'], 'success')
            if result['conflicts']:
                for conflict in result['conflicts']:
                    flash(f"Warning: {conflict}", 'warning')
        else:
            flash(result['message'], 'error')
            for conflict in result.get('conflicts', []):
                flash(f"Conflict: {conflict}", 'warning')
                
    except Exception as e:
        logging.error(f"Timetable generation error: {e}")
        flash('Failed to generate timetable. Please try again.', 'error')
    
    return redirect(url_for('timetable.view_timetable'))

@timetable_bp.route('/clear', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def clear_timetable():
    user = get_current_user()
    department_id = request.form.get('department_id')
    
    if not user.institution_id:
        flash('You must be associated with an institution.', 'error')
        return redirect(url_for('timetable.view_timetable'))
    
    try:
        query = TimetableEntry.query.filter_by(institution_id=user.institution_id)
        
        # Faculty can only clear their department
        if user.role == 'faculty' or department_id:
            dept_id = user.department_id if user.role == 'faculty' else int(department_id)
            query = query.join(Course).filter(Course.department_id == dept_id)
        
        deleted_count = query.delete(synchronize_session=False)
        db.session.commit()
        
        flash(f'Cleared {deleted_count} timetable entries.', 'success')
        
    except Exception as e:
        logging.error(f"Clear timetable error: {e}")
        flash('Failed to clear timetable.', 'error')
    
    return redirect(url_for('timetable.view_timetable'))

@timetable_bp.route('/analytics')
@login_required
@role_required('admin', 'faculty')
def analytics():
    user = get_current_user()
    user_filter = get_user_institution_filter()
    
    if not user.institution_id:
        flash('You must be associated with an institution.', 'error')
        return redirect(url_for('timetable.view_timetable'))
    
    # Get timetable entries for analytics
    query = TimetableEntry.query.filter_by(institution_id=user.institution_id)
    if user.role == 'faculty' and user.department_id:
        query = query.join(Course).filter(Course.department_id == user.department_id)
    
    entries = query.all()
    
    # Calculate analytics
    room_utilization = {}
    teacher_workload = {}
    
    for entry in entries:
        # Room utilization
        room_name = entry.room.name
        if room_name not in room_utilization:
            room_utilization[room_name] = 0
        room_utilization[room_name] += 1
        
        # Teacher workload
        teacher_name = entry.teacher.name
        if teacher_name not in teacher_workload:
            teacher_workload[teacher_name] = 0
        teacher_workload[teacher_name] += 1
    
    # Get total available slots for utilization calculation
    total_timeslots = TimeSlot.query.filter_by(institution_id=user.institution_id).count()
    
    analytics_data = {
        'total_classes': len(entries),
        'room_utilization': room_utilization,
        'teacher_workload': teacher_workload,
        'total_timeslots': total_timeslots
    }
    
    return render_template('analytics.html', analytics=analytics_data)

@timetable_bp.route('/edit/<int:entry_id>', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def edit_entry(entry_id):
    user = get_current_user()
    
    try:
        entry = TimetableEntry.query.get_or_404(entry_id)
        
        # Check permissions
        if user.role == 'faculty' and entry.course.department_id != user.department_id:
            flash('You can only edit entries for your department.', 'error')
            return redirect(url_for('timetable.view_timetable'))
        
        new_room_id = request.form.get('room_id')
        new_timeslot_id = request.form.get('timeslot_id')
        new_teacher_id = request.form.get('teacher_id')
        
        # Check for conflicts before updating
        conflicts = []
        
        if new_room_id and int(new_room_id) != entry.room_id:
            existing = TimetableEntry.query.filter_by(
                room_id=int(new_room_id),
                timeslot_id=entry.timeslot_id
            ).first()
            if existing and existing.id != entry.id:
                conflicts.append("Room is already occupied at this time")
        
        if new_teacher_id and int(new_teacher_id) != entry.teacher_id:
            existing = TimetableEntry.query.filter_by(
                teacher_id=int(new_teacher_id),
                timeslot_id=entry.timeslot_id
            ).first()
            if existing and existing.id != entry.id:
                conflicts.append("Teacher is already assigned at this time")
        
        if conflicts:
            for conflict in conflicts:
                flash(f"Conflict: {conflict}", 'error')
            return redirect(url_for('timetable.view_timetable'))
        
        # Update entry
        if new_room_id:
            entry.room_id = int(new_room_id)
        if new_timeslot_id:
            entry.timeslot_id = int(new_timeslot_id)
        if new_teacher_id:
            entry.teacher_id = int(new_teacher_id)
        
        entry.is_manual = True
        db.session.commit()
        
        flash('Timetable entry updated successfully!', 'success')
        
    except Exception as e:
        logging.error(f"Edit entry error: {e}")
        flash('Failed to update timetable entry.', 'error')
    
    return redirect(url_for('timetable.view_timetable'))
