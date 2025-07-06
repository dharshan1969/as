from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from auth import login_required, role_required, get_current_user, get_user_institution_filter
from models import Institution, Department, Teacher, Course, Room, TimeSlot, User
from app import db
from datetime import time
import logging

demo_bp = Blueprint('demo', __name__, url_prefix='/demo')

@demo_bp.route('/generate-sample-data', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def generate_sample_data():
    """Generate sample academic data for demonstration"""
    try:
        current_user = get_current_user()
        
        # Create sample institution if none exists
        institution = Institution.query.first()
        if not institution:
            institution = Institution(
                name="Sample University",
                code="SU",
                address="123 Education Street, Knowledge City, KC 12345"
            )
            db.session.add(institution)
            db.session.flush()  # Get the ID
            
            # Update current user's institution
            current_user.institution_id = institution.id
        
        # Create sample departments
        departments_data = [
            {"name": "Computer Science", "code": "CS"},
            {"name": "Mathematics", "code": "MATH"},
            {"name": "Physics", "code": "PHY"},
            {"name": "English Literature", "code": "ENG"}
        ]
        
        departments = []
        for dept_data in departments_data:
            dept = Department.query.filter_by(code=dept_data["code"], institution_id=institution.id).first()
            if not dept:
                dept = Department(
                    name=dept_data["name"],
                    code=dept_data["code"],
                    institution_id=institution.id
                )
                db.session.add(dept)
                departments.append(dept)
            else:
                departments.append(dept)
        
        db.session.flush()
        
        # Set user's department to first department
        if not current_user.department_id and departments:
            current_user.department_id = departments[0].id
        
        # Create sample time slots
        time_slots_data = [
            {"day": 0, "start": "09:00", "end": "10:00", "name": "Period 1"},
            {"day": 0, "start": "10:00", "end": "11:00", "name": "Period 2"},
            {"day": 0, "start": "11:30", "end": "12:30", "name": "Period 3"},
            {"day": 0, "start": "13:30", "end": "14:30", "name": "Period 4"},
            {"day": 1, "start": "09:00", "end": "10:00", "name": "Period 1"},
            {"day": 1, "start": "10:00", "end": "11:00", "name": "Period 2"},
            {"day": 1, "start": "11:30", "end": "12:30", "name": "Period 3"},
            {"day": 1, "start": "13:30", "end": "14:30", "name": "Period 4"},
            {"day": 2, "start": "09:00", "end": "10:00", "name": "Period 1"},
            {"day": 2, "start": "10:00", "end": "11:00", "name": "Period 2"},
            {"day": 2, "start": "11:30", "end": "12:30", "name": "Period 3"},
            {"day": 3, "start": "09:00", "end": "10:00", "name": "Period 1"},
            {"day": 3, "start": "10:00", "end": "11:00", "name": "Period 2"},
            {"day": 4, "start": "09:00", "end": "10:00", "name": "Period 1"},
            {"day": 4, "start": "10:00", "end": "11:00", "name": "Period 2"}
        ]
        
        for slot_data in time_slots_data:
            existing_slot = TimeSlot.query.filter_by(
                day_of_week=slot_data["day"],
                start_time=time.fromisoformat(slot_data["start"]),
                institution_id=institution.id
            ).first()
            
            if not existing_slot:
                slot = TimeSlot(
                    day_of_week=slot_data["day"],
                    start_time=time.fromisoformat(slot_data["start"]),
                    end_time=time.fromisoformat(slot_data["end"]),
                    period_name=slot_data["name"],
                    institution_id=institution.id
                )
                db.session.add(slot)
        
        # Create sample rooms
        rooms_data = [
            {"name": "Room A101", "code": "A101", "capacity": 30, "type": "lecture", "building": "Academic Block A"},
            {"name": "Room A102", "code": "A102", "capacity": 25, "type": "lecture", "building": "Academic Block A"},
            {"name": "Lab B201", "code": "B201", "capacity": 20, "type": "lab", "building": "Lab Building B"},
            {"name": "Lab B202", "code": "B202", "capacity": 20, "type": "lab", "building": "Lab Building B"},
            {"name": "Seminar Room C301", "code": "C301", "capacity": 15, "type": "seminar", "building": "Conference Block C"},
            {"name": "Lecture Hall D401", "code": "D401", "capacity": 100, "type": "lecture", "building": "Main Auditorium D"}
        ]
        
        for room_data in rooms_data:
            existing_room = Room.query.filter_by(code=room_data["code"], institution_id=institution.id).first()
            if not existing_room:
                room = Room(
                    name=room_data["name"],
                    code=room_data["code"],
                    capacity=room_data["capacity"],
                    room_type=room_data["type"],
                    building=room_data["building"],
                    institution_id=institution.id
                )
                db.session.add(room)
        
        # Create sample teachers
        teachers_data = [
            {"name": "Dr. Sarah Johnson", "email": "s.johnson@sample.edu", "emp_id": "EMP001", "dept": 0},
            {"name": "Prof. Michael Chen", "email": "m.chen@sample.edu", "emp_id": "EMP002", "dept": 0},
            {"name": "Dr. Emily Davis", "email": "e.davis@sample.edu", "emp_id": "EMP003", "dept": 1},
            {"name": "Prof. Robert Wilson", "email": "r.wilson@sample.edu", "emp_id": "EMP004", "dept": 1},
            {"name": "Dr. Lisa Brown", "email": "l.brown@sample.edu", "emp_id": "EMP005", "dept": 2},
            {"name": "Prof. David Lee", "email": "d.lee@sample.edu", "emp_id": "EMP006", "dept": 3}
        ]
        
        for teacher_data in teachers_data:
            existing_teacher = Teacher.query.filter_by(employee_id=teacher_data["emp_id"], institution_id=institution.id).first()
            if not existing_teacher and teacher_data["dept"] < len(departments):
                teacher = Teacher(
                    name=teacher_data["name"],
                    email=teacher_data["email"],
                    employee_id=teacher_data["emp_id"],
                    department_id=departments[teacher_data["dept"]].id,
                    institution_id=institution.id,
                    max_hours_per_week=20
                )
                db.session.add(teacher)
        
        # Create sample courses
        courses_data = [
            {"name": "Introduction to Programming", "code": "CS101", "credits": 3, "dept": 0, "students": 25},
            {"name": "Data Structures", "code": "CS201", "credits": 4, "dept": 0, "students": 20},
            {"name": "Database Systems", "code": "CS301", "credits": 3, "dept": 0, "students": 18},
            {"name": "Calculus I", "code": "MATH101", "credits": 4, "dept": 1, "students": 30},
            {"name": "Linear Algebra", "code": "MATH201", "credits": 3, "dept": 1, "students": 22},
            {"name": "Physics I", "code": "PHY101", "credits": 4, "dept": 2, "students": 28},
            {"name": "Modern Physics", "code": "PHY301", "credits": 3, "dept": 2, "students": 15},
            {"name": "English Composition", "code": "ENG101", "credits": 3, "dept": 3, "students": 35}
        ]
        
        for course_data in courses_data:
            existing_course = Course.query.filter_by(code=course_data["code"], institution_id=institution.id).first()
            if not existing_course and course_data["dept"] < len(departments):
                course = Course(
                    name=course_data["name"],
                    code=course_data["code"],
                    credits=course_data["credits"],
                    department_id=departments[course_data["dept"]].id,
                    institution_id=institution.id,
                    semester="Fall 2025",
                    year=2025,
                    student_count=course_data["students"],
                    duration_minutes=60
                )
                db.session.add(course)
        
        # Update session data
        session['institution_id'] = institution.id
        if departments:
            session['department_id'] = departments[0].id
        
        db.session.commit()
        
        flash('Sample data generated successfully! You can now generate timetables.', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Sample data generation error: {e}")
        flash('Failed to generate sample data. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@demo_bp.route('/clear-all-data', methods=['POST'])
@login_required
@role_required('admin')
def clear_all_data():
    """Clear all academic data (admin only)"""
    try:
        # Clear in reverse dependency order
        from models import TimetableEntry, FacultyAvailability
        
        TimetableEntry.query.delete()
        FacultyAvailability.query.delete()
        Course.query.delete()
        Teacher.query.delete()
        Room.query.delete()
        TimeSlot.query.delete()
        Department.query.delete()
        Institution.query.delete()
        
        # Clear session data
        session.pop('institution_id', None)
        session.pop('department_id', None)
        
        db.session.commit()
        
        flash('All academic data cleared successfully.', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Data clearing error: {e}")
        flash('Failed to clear data. Please try again.', 'error')
        return redirect(url_for('dashboard'))