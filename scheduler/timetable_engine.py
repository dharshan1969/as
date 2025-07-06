from ortools.sat.python import cp_model
from typing import List, Dict, Any, Tuple
from models import Course, Teacher, Room, TimeSlot, TimetableEntry, FacultyAvailability
from app import db
import logging

class TimetableScheduler:
    def __init__(self, institution_id: int):
        self.institution_id = institution_id
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables = {}
        self.conflicts = []
        
    def generate_timetable(self, department_id: int = None) -> Dict[str, Any]:
        """Generate timetable using constraint satisfaction"""
        try:
            # Clear existing timetable entries for this institution/department
            query = TimetableEntry.query.filter_by(institution_id=self.institution_id)
            if department_id:
                query = query.join(Course).filter(Course.department_id == department_id)
            query.delete(synchronize_session=False)
            db.session.commit()
            
            # Get data
            courses = self._get_courses(department_id)
            teachers = self._get_teachers(department_id)
            rooms = self._get_rooms()
            timeslots = self._get_timeslots()
            
            if not courses or not teachers or not rooms or not timeslots:
                return {
                    'success': False,
                    'message': 'Insufficient data to generate timetable. Please ensure you have courses, teachers, rooms, and timeslots configured.',
                    'conflicts': []
                }
            
            # Create variables
            self._create_variables(courses, teachers, rooms, timeslots)
            
            # Add constraints
            self._add_basic_constraints(courses, teachers, rooms, timeslots)
            self._add_availability_constraints(teachers, timeslots)
            self._add_capacity_constraints(courses, rooms)
            
            # Solve
            status = self.solver.Solve(self.model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                # Extract solution
                timetable_entries = self._extract_solution(courses, teachers, rooms, timeslots)
                
                # Save to database
                for entry_data in timetable_entries:
                    entry = TimetableEntry(**entry_data)
                    db.session.add(entry)
                
                db.session.commit()
                
                return {
                    'success': True,
                    'message': f'Timetable generated successfully with {len(timetable_entries)} classes scheduled.',
                    'conflicts': self.conflicts,
                    'entries_count': len(timetable_entries)
                }
            else:
                return {
                    'success': False,
                    'message': 'Could not generate a feasible timetable with current constraints.',
                    'conflicts': self._detect_conflicts(courses, teachers, rooms, timeslots)
                }
                
        except Exception as e:
            db.session.rollback()
            logging.error(f"Timetable generation error: {e}")
            return {
                'success': False,
                'message': f'Error generating timetable: {str(e)}',
                'conflicts': []
            }
    
    def _get_courses(self, department_id: int = None) -> List[Course]:
        """Get courses for scheduling"""
        query = Course.query.filter_by(institution_id=self.institution_id)
        if department_id:
            query = query.filter_by(department_id=department_id)
        return query.all()
    
    def _get_teachers(self, department_id: int = None) -> List[Teacher]:
        """Get teachers for scheduling"""
        query = Teacher.query.filter_by(institution_id=self.institution_id)
        if department_id:
            query = query.filter_by(department_id=department_id)
        return query.all()
    
    def _get_rooms(self) -> List[Room]:
        """Get rooms for scheduling"""
        return Room.query.filter_by(institution_id=self.institution_id).all()
    
    def _get_timeslots(self) -> List[TimeSlot]:
        """Get timeslots for scheduling"""
        return TimeSlot.query.filter_by(institution_id=self.institution_id).order_by(
            TimeSlot.day_of_week, TimeSlot.start_time
        ).all()
    
    def _create_variables(self, courses: List[Course], teachers: List[Teacher], 
                         rooms: List[Room], timeslots: List[TimeSlot]):
        """Create decision variables"""
        for course in courses:
            for teacher in teachers:
                # Only allow teachers from same department
                if teacher.department_id != course.department_id:
                    continue
                    
                for room in rooms:
                    for timeslot in timeslots:
                        var_name = f"schedule_{course.id}_{teacher.id}_{room.id}_{timeslot.id}"
                        self.variables[var_name] = self.model.NewBoolVar(var_name)
    
    def _add_basic_constraints(self, courses: List[Course], teachers: List[Teacher],
                              rooms: List[Room], timeslots: List[TimeSlot]):
        """Add basic scheduling constraints"""
        
        # Each course must be assigned exactly once
        for course in courses:
            course_vars = []
            for teacher in teachers:
                if teacher.department_id != course.department_id:
                    continue
                for room in rooms:
                    for timeslot in timeslots:
                        var_name = f"schedule_{course.id}_{teacher.id}_{room.id}_{timeslot.id}"
                        if var_name in self.variables:
                            course_vars.append(self.variables[var_name])
            
            if course_vars:
                self.model.Add(sum(course_vars) == 1)
        
        # No room conflicts - only one class per room per timeslot
        for room in rooms:
            for timeslot in timeslots:
                room_timeslot_vars = []
                for course in courses:
                    for teacher in teachers:
                        if teacher.department_id != course.department_id:
                            continue
                        var_name = f"schedule_{course.id}_{teacher.id}_{room.id}_{timeslot.id}"
                        if var_name in self.variables:
                            room_timeslot_vars.append(self.variables[var_name])
                
                if room_timeslot_vars:
                    self.model.Add(sum(room_timeslot_vars) <= 1)
        
        # No teacher conflicts - only one class per teacher per timeslot
        for teacher in teachers:
            for timeslot in timeslots:
                teacher_timeslot_vars = []
                for course in courses:
                    if teacher.department_id != course.department_id:
                        continue
                    for room in rooms:
                        var_name = f"schedule_{course.id}_{teacher.id}_{room.id}_{timeslot.id}"
                        if var_name in self.variables:
                            teacher_timeslot_vars.append(self.variables[var_name])
                
                if teacher_timeslot_vars:
                    self.model.Add(sum(teacher_timeslot_vars) <= 1)
    
    def _add_availability_constraints(self, teachers: List[Teacher], timeslots: List[TimeSlot]):
        """Add teacher availability constraints"""
        for teacher in teachers:
            unavailable_slots = FacultyAvailability.query.filter_by(
                teacher_id=teacher.id, is_available=False
            ).all()
            
            for unavail in unavailable_slots:
                for course_id in [c.id for c in Course.query.filter_by(
                    department_id=teacher.department_id, institution_id=self.institution_id
                ).all()]:
                    for room_id in [r.id for r in Room.query.filter_by(
                        institution_id=self.institution_id
                    ).all()]:
                        var_name = f"schedule_{course_id}_{teacher.id}_{room_id}_{unavail.timeslot_id}"
                        if var_name in self.variables:
                            self.model.Add(self.variables[var_name] == 0)
    
    def _add_capacity_constraints(self, courses: List[Course], rooms: List[Room]):
        """Add room capacity constraints"""
        for course in courses:
            if course.student_count > 0:
                for teacher_id in [t.id for t in Teacher.query.filter_by(
                    department_id=course.department_id, institution_id=self.institution_id
                ).all()]:
                    for room in rooms:
                        if room.capacity < course.student_count:
                            for timeslot_id in [ts.id for ts in TimeSlot.query.filter_by(
                                institution_id=self.institution_id
                            ).all()]:
                                var_name = f"schedule_{course.id}_{teacher_id}_{room.id}_{timeslot_id}"
                                if var_name in self.variables:
                                    self.model.Add(self.variables[var_name] == 0)
    
    def _extract_solution(self, courses: List[Course], teachers: List[Teacher],
                         rooms: List[Room], timeslots: List[TimeSlot]) -> List[Dict]:
        """Extract solution from solver"""
        timetable_entries = []
        
        for var_name, var in self.variables.items():
            if self.solver.Value(var) == 1:
                # Parse variable name
                parts = var_name.split('_')
                course_id = int(parts[1])
                teacher_id = int(parts[2])
                room_id = int(parts[3])
                timeslot_id = int(parts[4])
                
                timetable_entries.append({
                    'course_id': course_id,
                    'teacher_id': teacher_id,
                    'room_id': room_id,
                    'timeslot_id': timeslot_id,
                    'institution_id': self.institution_id,
                    'section': 'A',  # Default section
                    'is_manual': False
                })
        
        return timetable_entries
    
    def _detect_conflicts(self, courses: List[Course], teachers: List[Teacher],
                         rooms: List[Room], timeslots: List[TimeSlot]) -> List[str]:
        """Detect conflicts when no solution found"""
        conflicts = []
        
        # Check if there are enough rooms
        total_classes = len(courses)
        total_slots = len(timeslots) * len(rooms)
        if total_classes > total_slots:
            conflicts.append(f"Not enough time slots: {total_classes} classes need {total_slots} slots")
        
        # Check teacher availability
        for teacher in teachers:
            teacher_courses = [c for c in courses if c.department_id == teacher.department_id]
            unavailable_count = FacultyAvailability.query.filter_by(
                teacher_id=teacher.id, is_available=False
            ).count()
            available_slots = len(timeslots) - unavailable_count
            
            if len(teacher_courses) > available_slots:
                conflicts.append(f"Teacher {teacher.name} has {len(teacher_courses)} courses but only {available_slots} available slots")
        
        # Check room capacity
        for course in courses:
            suitable_rooms = [r for r in rooms if r.capacity >= course.student_count]
            if not suitable_rooms:
                conflicts.append(f"Course {course.name} has {course.student_count} students but no room has sufficient capacity")
        
        return conflicts

def generate_timetable_for_institution(institution_id: int, department_id: int = None) -> Dict[str, Any]:
    """Generate timetable for an institution"""
    scheduler = TimetableScheduler(institution_id)
    return scheduler.generate_timetable(department_id)
