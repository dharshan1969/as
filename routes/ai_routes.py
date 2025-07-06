from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from auth import login_required, role_required, get_current_user, get_user_institution_filter
from models import Course, Room, Teacher, TimetableEntry
from ai_integration import (
    analyze_timetable_conflicts, 
    suggest_room_allocation, 
    optimize_teacher_schedule,
    generate_schedule_summary
)
import logging

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/analyze-timetable')
@login_required
@role_required('admin', 'faculty')
def analyze_timetable():
    """Analyze current timetable using AI"""
    try:
        institution_filter = get_user_institution_filter()
        
        # Get timetable data
        entries = TimetableEntry.query.filter_by(**institution_filter).all()
        
        # Convert to dict format for AI analysis
        timetable_data = {
            "entries": [{
                "course_name": entry.course.name,
                "teacher_name": entry.teacher.name,
                "room_name": entry.room.name,
                "capacity": entry.room.capacity,
                "student_count": entry.course.student_count,
                "day": entry.timeslot.day_of_week,
                "start_time": entry.timeslot.start_time.strftime("%H:%M"),
                "end_time": entry.timeslot.end_time.strftime("%H:%M")
            } for entry in entries]
        }
        
        # Get AI analysis
        analysis = analyze_timetable_conflicts(timetable_data)
        
        return render_template('ai/timetable_analysis.html', analysis=analysis)
        
    except Exception as e:
        logging.error(f"AI analysis error: {e}")
        flash('Unable to analyze timetable at this time.', 'error')
        return redirect(url_for('timetable.view_timetable'))

@ai_bp.route('/suggest-rooms')
@login_required
@role_required('admin', 'faculty')
def suggest_rooms():
    """Get AI suggestions for room allocation"""
    try:
        institution_filter = get_user_institution_filter()
        
        # Get courses and rooms
        courses = Course.query.filter_by(**institution_filter).all()
        rooms = Room.query.filter_by(**institution_filter).all()
        
        # Convert to dict format
        courses_data = [{
            "id": course.id,
            "name": course.name,
            "student_count": course.student_count,
            "duration_minutes": course.duration_minutes
        } for course in courses]
        
        rooms_data = [{
            "id": room.id,
            "name": room.name,
            "capacity": room.capacity,
            "type": room.room_type,
            "building": room.building
        } for room in rooms]
        
        # Get AI suggestions
        suggestions = suggest_room_allocation(courses_data, rooms_data)
        
        return render_template('ai/room_suggestions.html', 
                             suggestions=suggestions, 
                             courses=courses, 
                             rooms=rooms)
        
    except Exception as e:
        logging.error(f"Room suggestion error: {e}")
        flash('Unable to generate room suggestions at this time.', 'error')
        return redirect(url_for('admin.rooms'))

@ai_bp.route('/optimize-workload')
@login_required
@role_required('admin', 'faculty')
def optimize_workload():
    """Optimize teacher workload distribution using AI"""
    try:
        institution_filter = get_user_institution_filter()
        
        # Get teachers and courses
        teachers = Teacher.query.filter_by(**institution_filter).all()
        courses = Course.query.filter_by(**institution_filter).all()
        
        # Convert to dict format
        teachers_data = [{
            "id": teacher.id,
            "name": teacher.name,
            "max_hours_per_week": teacher.max_hours_per_week,
            "current_assignments": len(teacher.timetable_entries)
        } for teacher in teachers]
        
        courses_data = [{
            "id": course.id,
            "name": course.name,
            "credits": course.credits,
            "duration_minutes": course.duration_minutes
        } for course in courses]
        
        # Get AI optimization
        optimization = optimize_teacher_schedule(teachers_data, courses_data)
        
        return render_template('ai/workload_optimization.html', 
                             optimization=optimization,
                             teachers=teachers)
        
    except Exception as e:
        logging.error(f"Workload optimization error: {e}")
        flash('Unable to optimize workload at this time.', 'error')
        return redirect(url_for('admin.teachers'))

@ai_bp.route('/generate-summary')
@login_required
@role_required('admin', 'faculty')
def generate_summary():
    """Generate AI-powered timetable summary"""
    try:
        institution_filter = get_user_institution_filter()
        
        # Get timetable entries
        entries = TimetableEntry.query.filter_by(**institution_filter).all()
        
        # Convert to dict format
        entries_data = [{
            "course": entry.course.name,
            "teacher": entry.teacher.name,
            "room": entry.room.name,
            "day": entry.timeslot.day_of_week,
            "time": f"{entry.timeslot.start_time.strftime('%H:%M')}-{entry.timeslot.end_time.strftime('%H:%M')}",
            "department": entry.course.department.name
        } for entry in entries]
        
        # Generate AI summary
        summary = generate_schedule_summary(entries_data)
        
        return render_template('ai/schedule_summary.html', 
                             summary=summary,
                             total_entries=len(entries))
        
    except Exception as e:
        logging.error(f"Summary generation error: {e}")
        flash('Unable to generate summary at this time.', 'error')
        return redirect(url_for('timetable.view_timetable'))

@ai_bp.route('/api/quick-analysis', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def quick_analysis():
    """Quick AI analysis endpoint for AJAX requests"""
    try:
        data = request.get_json()
        analysis_type = data.get('type', 'conflicts')
        
        institution_filter = get_user_institution_filter()
        
        if analysis_type == 'conflicts':
            entries = TimetableEntry.query.filter_by(**institution_filter).all()
            timetable_data = {
                "entries": [{
                    "course_name": entry.course.name,
                    "teacher_name": entry.teacher.name,
                    "room_capacity": entry.room.capacity,
                    "student_count": entry.course.student_count
                } for entry in entries]
            }
            result = analyze_timetable_conflicts(timetable_data)
            
        elif analysis_type == 'utilization':
            rooms = Room.query.filter_by(**institution_filter).all()
            result = {
                "room_utilization": [
                    {
                        "room": room.name,
                        "capacity": room.capacity,
                        "bookings": len(room.timetable_entries)
                    } for room in rooms
                ]
            }
        
        else:
            result = {"error": "Unknown analysis type"}
            
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Quick analysis error: {e}")
        return jsonify({"error": "Analysis failed"}), 500