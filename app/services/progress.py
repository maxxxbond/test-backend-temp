from typing import Dict, List, Any, Tuple, Optional
from app.schemas.schemas import CourseProgress

def calculate_highest_score(progress_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate the highest score from user's progress data.
    """
    highest_score = {"module": 0, "score": 0}
    if progress_data:
        scores = [(p["module_id"], p["score"] or 0) for p in progress_data if p.get("score")]
        if scores:
            highest_score = {
                "module": max(scores, key=lambda x: x[1])[0], 
                "score": max(scores, key=lambda x: x[1])[1]
            }
    return highest_score

def get_last_activity(progress_data: List[Dict[str, Any]]) -> str:
    """
    Get the most recent activity timestamp from progress data.
    """
    last_activity = "Never"
    if progress_data:
        latest = max(progress_data, key=lambda x: x.get("completed_at", "1970-01-01"))
        if latest.get("completed_at"):
            last_activity = latest["completed_at"]
    return last_activity

def create_course_progress_summary(
    user_id: str,
    progress_data: List[Dict[str, Any]],
    total_modules: int
) -> CourseProgress:
    """
    Create a CourseProgress object with summary of user's course progress.
    """
    completed_modules = len([p for p in progress_data if p.get("passed")]) if progress_data else 0
    highest_score = calculate_highest_score(progress_data)
    last_activity = get_last_activity(progress_data)
    
    return CourseProgress(
        user_id=user_id,
        completed_modules=completed_modules,
        total_modules=total_modules,
        last_activity=last_activity,
        highest_score=highest_score,
        is_completed=completed_modules >= total_modules and total_modules > 0,
        has_started=completed_modules > 0
    )

def determine_module_status(
    module_index: int, 
    module_id: int, 
    progress_dict: Dict[int, Dict[str, Any]], 
    modules_data: List[Dict[str, Any]]
) -> Tuple[str, Optional[int], Optional[str]]:
    """
    Determine the status of a module based on user's progress.
    Returns a tuple of (status, score, completion_date)
    """
    user_progress = progress_dict.get(module_id)
    
    if user_progress and user_progress.get("passed"):
        return "completed", user_progress.get("score"), user_progress.get("completed_at")
    elif module_index == 0 or (module_index > 0 and 
                               modules_data[module_index-1]["id"] in progress_dict and 
                               progress_dict[modules_data[module_index-1]["id"]].get("passed")):
        # First module or previous module passed quiz
        return "available", None, None
    else:
        return "locked", None, None
