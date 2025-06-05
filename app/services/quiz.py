from typing import List, Dict, Any

def evaluate_quiz_answer(
    question: Dict[str, Any], 
    answer_text: str, 
    correct_answers_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluate if a user's answer is correct based on question type.
    Returns a dictionary with evaluation results.
    """
    is_correct = False
    correct_answer_text = None
    feedback = None
    
    if question["type"] == "single":
        # For single choice, check if user answer matches any correct answer
        correct_answers_list = [a["answer_text"] for a in correct_answers_data] if correct_answers_data else []
        is_correct = answer_text in correct_answers_list
        correct_answer_text = correct_answers_list[0] if correct_answers_list else None
        
    elif question["type"] == "multi":
        # For multi-choice, check if user selections match all correct answers
        correct_answers_set = set(a["answer_text"] for a in correct_answers_data) if correct_answers_data else set()
        user_answers_set = set(answer_text.split(', ')) if isinstance(answer_text, str) and answer_text else set()
        is_correct = user_answers_set == correct_answers_set
        correct_answer_text = ", ".join(correct_answers_set) if correct_answers_set else None
        
    elif question["type"] == "text":
        # For text answers, check for exact match
        correct_answers_list = [a["answer_text"] for a in correct_answers_data] if correct_answers_data else []
        is_correct = any(a.lower().strip() == answer_text.lower().strip() for a in correct_answers_list)
        correct_answer_text = correct_answers_list[0] if correct_answers_list else None
        
    elif question["type"] == "number":
        # For number answers, check within tolerance if specified
        if correct_answers_data:
            correct_value = float(correct_answers_data[0]["answer_text"])
            tolerance = float(question.get("tolerance", 0))
            
            try:
                user_value = float(answer_text)
                is_correct = abs(user_value - correct_value) <= tolerance
                correct_answer_text = str(correct_value)
            except ValueError:
                is_correct = False
                correct_answer_text = str(correct_value)
                feedback = "Invalid number format"
    
    # Generate feedback based on answer correctness if not already set
    if not feedback:
        feedback = "Correct! Good job." if is_correct else "Incorrect answer."
    
    return {
        "is_correct": is_correct,
        "correct_answer_text": correct_answer_text,
        "feedback": feedback
    }

def generate_quiz_feedback(score: int) -> str:
    """Generate overall feedback for a quiz based on the score."""
    if score >= 70:
        if score >= 90:
            return "Excellent work! You've mastered this module."
        elif score >= 80:
            return "Great job! You have a solid understanding of the material."
        else:
            return "Good work! You've passed the quiz."
    else:
        return "You need to score at least 70% to pass. Review the material and try again."

def extract_answer_data(answer_data: Any) -> Dict[str, Any]:
    """
    Extract question_id and answer_text from various answer data formats.
    Returns a dict with extracted data or empty values if extraction fails.
    """
    question_id = None
    answer_text = ""
    
    if isinstance(answer_data, dict):
        question_id = answer_data.get("question_id")
        answer_text = answer_data.get("answer_text", "")
    else:
        # Try to handle other formats gracefully
        try:
            # If it's an object with attributes
            question_id = getattr(answer_data, "question_id", None)
            answer_text = getattr(answer_data, "answer_text", "")
        except:
            pass  # Will return default values
    
    return {
        "question_id": question_id,
        "answer_text": answer_text
    }
