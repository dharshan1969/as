from app import db
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, faculty, student
    institution_id = db.Column(db.Integer, ForeignKey('institutions.id'), nullable=True)
    department_id = db.Column(db.Integer, ForeignKey('departments.id'), nullable=True)
    supabase_user_id = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, email=None, name=None, role='student', institution_id=None, 
                 department_id=None, supabase_user_id=None):
        self.email = email
        self.name = name
        self.role = role
        self.institution_id = institution_id
        self.department_id = department_id
        self.supabase_user_id = supabase_user_id
    
    # Relationships
    institution = relationship("Institution", back_populates="users")
    department = relationship("Department", back_populates="users", foreign_keys=[department_id])
    headed_department = relationship("Department", foreign_keys="Department.head_id", post_update=True)

class Institution(db.Model):
    __tablename__ = 'institutions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name=None, code=None, address=None):
        self.name = name
        self.code = code
        self.address = address
    
    # Relationships
    users = relationship("User", back_populates="institution")
    departments = relationship("Department", back_populates="institution")
    rooms = relationship("Room", back_populates="institution")
    timeslots = relationship("TimeSlot", back_populates="institution")
    institution_rules = relationship("InstitutionRule", back_populates="institution")

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    institution_id = db.Column(db.Integer, ForeignKey('institutions.id'), nullable=False)
    head_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name=None, code=None, institution_id=None, head_id=None):
        self.name = name
        self.code = code
        self.institution_id = institution_id
        self.head_id = head_id
    
    # Relationships
    institution = relationship("Institution", back_populates="departments")
    users = relationship("User", back_populates="department", foreign_keys="User.department_id")
    head = relationship("User", foreign_keys=[head_id], post_update=True, overlaps="headed_department")
    teachers = relationship("Teacher", back_populates="department")
    courses = relationship("Course", back_populates="department")

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    employee_id = db.Column(db.String(50), nullable=False)
    department_id = db.Column(db.Integer, ForeignKey('departments.id'), nullable=False)
    institution_id = db.Column(db.Integer, ForeignKey('institutions.id'), nullable=False)
    max_hours_per_week = db.Column(db.Integer, default=40)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = relationship("Department", back_populates="teachers")
    institution = relationship("Institution")
    availability = relationship("FacultyAvailability", back_populates="teacher")
    timetable_entries = relationship("TimetableEntry", back_populates="teacher")

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer, ForeignKey('departments.id'), nullable=False)
    institution_id = db.Column(db.Integer, ForeignKey('institutions.id'), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    student_count = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Integer, default=60)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = relationship("Department", back_populates="courses")
    institution = relationship("Institution")
    timetable_entries = relationship("TimetableEntry", back_populates="course")

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # lecture, lab, seminar
    building = db.Column(db.String(100))
    floor = db.Column(db.String(10))
    institution_id = db.Column(db.Integer, ForeignKey('institutions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    institution = relationship("Institution", back_populates="rooms")
    timetable_entries = relationship("TimetableEntry", back_populates="room")

class TimeSlot(db.Model):
    __tablename__ = 'timeslots'
    
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    period_name = db.Column(db.String(50))  # Period 1, Period 2, etc.
    institution_id = db.Column(db.Integer, ForeignKey('institutions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    institution = relationship("Institution", back_populates="timeslots")
    timetable_entries = relationship("TimetableEntry", back_populates="timeslot")
    faculty_availability = relationship("FacultyAvailability", back_populates="timeslot")

class TimetableEntry(db.Model):
    __tablename__ = 'timetable_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, ForeignKey('teachers.id'), nullable=False)
    room_id = db.Column(db.Integer, ForeignKey('rooms.id'), nullable=False)
    timeslot_id = db.Column(db.Integer, ForeignKey('timeslots.id'), nullable=False)
    institution_id = db.Column(db.Integer, ForeignKey('institutions.id'), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    is_manual = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="timetable_entries")
    teacher = relationship("Teacher", back_populates="timetable_entries")
    room = relationship("Room", back_populates="timetable_entries")
    timeslot = relationship("TimeSlot", back_populates="timetable_entries")
    institution = relationship("Institution")

class FacultyAvailability(db.Model):
    __tablename__ = 'faculty_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, ForeignKey('teachers.id'), nullable=False)
    timeslot_id = db.Column(db.Integer, ForeignKey('timeslots.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="availability")
    timeslot = relationship("TimeSlot", back_populates="faculty_availability")

class ElectiveGroup(db.Model):
    __tablename__ = 'elective_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, ForeignKey('departments.id'), nullable=False)
    institution_id = db.Column(db.Integer, ForeignKey('institutions.id'), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InstitutionRule(db.Model):
    __tablename__ = 'institution_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, ForeignKey('institutions.id'), nullable=False)
    rule_name = db.Column(db.String(100), nullable=False)
    rule_value = db.Column(db.String(200), nullable=False)
    rule_type = db.Column(db.String(50), nullable=False)  # time, capacity, constraint
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    institution = relationship("Institution", back_populates="institution_rules")
