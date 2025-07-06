import json
import os
from typing import Dict, List, Any
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_timetable_conflicts(timetable_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze timetable for potential conflicts and suggest improvements"""
    try:
        prompt = f"""
        Analyze this academic timetable data for conflicts and optimization opportunities:
        {json.dumps(timetable_data, indent=2)}
        
        Please identify:
        1. Room capacity vs student enrollment conflicts
        2. Teacher workload distribution issues
        3. Time slot utilization patterns
        4. Suggestions for better scheduling
        
        Respond with JSON in this format:
        {{
            "conflicts": [list of conflict descriptions],
            "suggestions": [list of improvement suggestions],
            "utilization_score": number between 0-100,
            "teacher_workload_analysis": {{teacher_name: hours_per_week}}
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content or ""
        result = json.loads(content)
        return result
    except Exception as e:
        return {
            "error": f"Failed to analyze timetable: {str(e)}",
            "conflicts": [],
            "suggestions": ["Unable to analyze at this time"],
            "utilization_score": 0,
            "teacher_workload_analysis": {}
        }

def suggest_room_allocation(courses: List[Dict], rooms: List[Dict]) -> Dict[str, Any]:
    """Get AI suggestions for optimal room allocation"""
    try:
        prompt = f"""
        Given these courses and available rooms, suggest optimal room allocations:
        
        Courses: {json.dumps(courses, indent=2)}
        Rooms: {json.dumps(rooms, indent=2)}
        
        Consider:
        - Room capacity vs student count
        - Room type suitability (lecture/lab/seminar)
        - Building proximity for back-to-back classes
        
        Respond with JSON:
        {{
            "allocations": [{{
                "course_id": number,
                "recommended_room_id": number,
                "reason": "explanation for recommendation"
            }}],
            "warnings": [list of capacity or suitability warnings]
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content or "{}"
        return json.loads(content)
    except Exception as e:
        return {
            "error": f"Failed to suggest room allocation: {str(e)}",
            "allocations": [],
            "warnings": []
        }

def optimize_teacher_schedule(teachers: List[Dict], courses: List[Dict]) -> Dict[str, Any]:
    """Analyze and optimize teacher workload distribution"""
    try:
        prompt = f"""
        Analyze teacher workload and suggest optimizations:
        
        Teachers: {json.dumps(teachers, indent=2)}
        Courses: {json.dumps(courses, indent=2)}
        
        Consider:
        - Even distribution of teaching hours
        - Teacher expertise alignment with courses
        - Maximum weekly hour limits
        
        Respond with JSON:
        {{
            "workload_analysis": [{{
                "teacher_id": number,
                "current_hours": number,
                "recommended_hours": number,
                "status": "overloaded/balanced/underutilized"
            }}],
            "redistribution_suggestions": [list of specific recommendations]
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content or "{}"
        return json.loads(content)
    except Exception as e:
        return {
            "error": f"Failed to optimize teacher schedule: {str(e)}",
            "workload_analysis": [],
            "redistribution_suggestions": []
        }

def generate_schedule_summary(timetable_entries: List[Dict]) -> str:
    """Generate a natural language summary of the timetable"""
    try:
        prompt = f"""
        Create a concise summary of this academic timetable:
        {json.dumps(timetable_entries, indent=2)}
        
        Include:
        - Total number of scheduled classes
        - Peak utilization times
        - Department distribution
        - Any notable patterns or insights
        
        Write in clear, professional language suitable for academic administrators.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content or "Unable to generate summary."
    except Exception as e:
        return f"Unable to generate summary: {str(e)}"