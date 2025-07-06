from flask import Blueprint, request, flash, redirect, url_for, make_response, send_file
from auth import login_required, role_required, get_current_user
from models import TimetableEntry, Course, Teacher, Room, TimeSlot
import pandas as pd
import io
from datetime import datetime
import logging

export_bp = Blueprint('export', __name__)

@export_bp.route('/excel')
@login_required
@role_required('admin', 'faculty')
def export_excel():
    user = get_current_user()
    
    if not user.institution_id:
        flash('You must be associated with an institution.', 'error')
        return redirect(url_for('timetable.view_timetable'))
    
    try:
        # Get timetable entries
        query = TimetableEntry.query.filter_by(institution_id=user.institution_id)
        
        # Faculty can only export their department
        if user.role == 'faculty' and user.department_id:
            query = query.join(Course).filter(Course.department_id == user.department_id)
        
        entries = query.all()
        
        if not entries:
            flash('No timetable data to export.', 'warning')
            return redirect(url_for('timetable.view_timetable'))
        
        # Prepare data for Excel
        data = []
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for entry in entries:
            data.append({
                'Day': days_of_week[entry.timeslot.day_of_week],
                'Time': f"{entry.timeslot.start_time.strftime('%H:%M')}-{entry.timeslot.end_time.strftime('%H:%M')}",
                'Course Code': entry.course.code,
                'Course Name': entry.course.name,
                'Teacher': entry.teacher.name,
                'Room': entry.room.name,
                'Section': entry.section,
                'Credits': entry.course.credits,
                'Student Count': entry.course.student_count,
                'Department': entry.course.department.name,
                'Manual Entry': 'Yes' if entry.is_manual else 'No'
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Sort by day and time
        day_order = {day: i for i, day in enumerate(days_of_week)}
        df['day_order'] = df['Day'].map(day_order)
        df = df.sort_values(['day_order', 'Time']).drop('day_order', axis=1)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Timetable', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Timetable']
            
            # Add formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Write headers with formatting
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Auto-adjust column widths
            for i, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).str.len().max(), len(col))
                worksheet.set_column(i, i, min(max_length + 2, 50))
        
        output.seek(0)
        
        # Create response
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=timetable_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return response
        
    except Exception as e:
        logging.error(f"Excel export error: {e}")
        flash('Failed to export timetable to Excel.', 'error')
        return redirect(url_for('timetable.view_timetable'))

@export_bp.route('/csv')
@login_required
@role_required('admin', 'faculty')
def export_csv():
    user = get_current_user()
    
    if not user.institution_id:
        flash('You must be associated with an institution.', 'error')
        return redirect(url_for('timetable.view_timetable'))
    
    try:
        # Get timetable entries
        query = TimetableEntry.query.filter_by(institution_id=user.institution_id)
        
        # Faculty can only export their department
        if user.role == 'faculty' and user.department_id:
            query = query.join(Course).filter(Course.department_id == user.department_id)
        
        entries = query.all()
        
        if not entries:
            flash('No timetable data to export.', 'warning')
            return redirect(url_for('timetable.view_timetable'))
        
        # Prepare data for CSV
        data = []
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for entry in entries:
            data.append({
                'Day': days_of_week[entry.timeslot.day_of_week],
                'Time': f"{entry.timeslot.start_time.strftime('%H:%M')}-{entry.timeslot.end_time.strftime('%H:%M')}",
                'Course Code': entry.course.code,
                'Course Name': entry.course.name,
                'Teacher': entry.teacher.name,
                'Room': entry.room.name,
                'Section': entry.section,
                'Credits': entry.course.credits,
                'Student Count': entry.course.student_count,
                'Department': entry.course.department.name,
                'Manual Entry': 'Yes' if entry.is_manual else 'No'
            })
        
        # Create DataFrame and CSV
        df = pd.DataFrame(data)
        
        # Sort by day and time
        day_order = {day: i for i, day in enumerate(days_of_week)}
        df['day_order'] = df['Day'].map(day_order)
        df = df.sort_values(['day_order', 'Time']).drop('day_order', axis=1)
        
        # Create CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False)
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=timetable_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        logging.error(f"CSV export error: {e}")
        flash('Failed to export timetable to CSV.', 'error')
        return redirect(url_for('timetable.view_timetable'))

@export_bp.route('/summary')
@login_required
@role_required('admin', 'faculty')
def export_summary():
    user = get_current_user()
    
    if not user.institution_id:
        flash('You must be associated with an institution.', 'error')
        return redirect(url_for('timetable.view_timetable'))
    
    try:
        # Get timetable entries
        query = TimetableEntry.query.filter_by(institution_id=user.institution_id)
        
        # Faculty can only export their department
        if user.role == 'faculty' and user.department_id:
            query = query.join(Course).filter(Course.department_id == user.department_id)
        
        entries = query.all()
        
        if not entries:
            flash('No timetable data to export.', 'warning')
            return redirect(url_for('timetable.view_timetable'))
        
        # Create summary data
        summary_data = {
            'Total Classes': len(entries),
            'Manual Adjustments': len([e for e in entries if e.is_manual]),
            'Automatic Assignments': len([e for e in entries if not e.is_manual]),
        }
        
        # Room utilization
        room_usage = {}
        for entry in entries:
            room_name = entry.room.name
            room_usage[room_name] = room_usage.get(room_name, 0) + 1
        
        # Teacher workload
        teacher_workload = {}
        for entry in entries:
            teacher_name = entry.teacher.name
            teacher_workload[teacher_name] = teacher_workload.get(teacher_name, 0) + 1
        
        # Create summary DataFrame
        summary_df = pd.DataFrame(list(summary_data.items()), columns=['Metric', 'Value'])
        room_df = pd.DataFrame(list(room_usage.items()), columns=['Room', 'Classes Scheduled'])
        teacher_df = pd.DataFrame(list(teacher_workload.items()), columns=['Teacher', 'Classes Assigned'])
        
        # Create Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            room_df.to_excel(writer, sheet_name='Room Utilization', index=False)
            teacher_df.to_excel(writer, sheet_name='Teacher Workload', index=False)
            
            # Format sheets
            for sheet_name in ['Summary', 'Room Utilization', 'Teacher Workload']:
                worksheet = writer.sheets[sheet_name]
                workbook = writer.book
                
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Format headers
                for col_num in range(2):  # Both sheets have 2 columns
                    worksheet.write(0, col_num, worksheet.cell(0, col_num).value, header_format)
                
                # Auto-adjust column widths
                worksheet.set_column(0, 0, 20)
                worksheet.set_column(1, 1, 15)
        
        output.seek(0)
        
        # Create response
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=timetable_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return response
        
    except Exception as e:
        logging.error(f"Summary export error: {e}")
        flash('Failed to export timetable summary.', 'error')
        return redirect(url_for('timetable.view_timetable'))
