from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import Any, List, Optional
from datetime import datetime, timezone
import uuid
from supabase import Client

from app.schemas.schemas import (
    User, Module, ModuleBlock, Question, Answer, Progress, UserAnswer,
    CourseProgress, QuizSubmission, QuizResult, Certificate, CertificateCreate,
    ApiResponse, ProgressCreate, ProgressUpdate
)
from app.api.deps import get_db
from app.api.endpoints.auth import get_current_user
from app.core.utils import get_current_time
from app.services.quiz import evaluate_quiz_answer, generate_quiz_feedback, extract_answer_data
from app.services.certificates import generate_certificate_content, prepare_certificate_response
from app.services.progress import (
    calculate_highest_score, get_last_activity, create_course_progress_summary,
    determine_module_status
)

router = APIRouter()


@router.get("/progress", response_model=ApiResponse)
async def get_course_progress(
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get user's course progress.
    """
    try:
        # Use the current user's ID
        user_id = current_user.id
        
        # Get user's progress data
        progress_response = db.table("progress").select("*").eq("user_id", user_id).execute()
        
        # Get total modules count
        modules_response = db.table("modules").select("id").execute()
        total_modules = len(modules_response.data) if modules_response.data else 0
        
        # Create course progress summary
        course_progress = create_course_progress_summary(
            user_id, 
            progress_response.data if progress_response.data else [],
            total_modules
        )
        
        return ApiResponse(success=True, data=course_progress.dict())
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course progress: {str(e)}"
        )


@router.get("/modules", response_model=ApiResponse)
async def get_course_modules(
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get all course modules with user's progress.
    """
    try:
        user_id = current_user.id
        
        modules_response = db.table("modules").select("*").order("order").execute()
        
        if not modules_response.data:
            return ApiResponse(success=True, data=[])
        
        progress_response = db.table("progress").select("*").eq("user_id", user_id).execute()
        progress_dict = {p["module_id"]: p for p in progress_response.data} if progress_response.data else {}
        
        modules_with_progress = []
        
        for i, module_data in enumerate(modules_response.data):
            module_id = module_data["id"]
            
            blocks_response = db.table("module_blocks").select("*").eq("module_id", module_id).order("order").execute()
            
            questions_response = db.table("questions").select("*").eq("module_id", module_id).execute()
            questions_with_answers = []
            
            if questions_response.data:
                for question in questions_response.data:
                    answers_response = db.table("answers").select("*").eq("question_id", question["id"]).execute()
                    question["answers"] = answers_response.data if answers_response.data else []
                    questions_with_answers.append(question)
            
            status, score, completion_date = determine_module_status(
                i, 
                module_id, 
                progress_dict, 
                modules_response.data
            )
            
            module_dict = {
                **module_data,
                "status": status,
                "score": score,
                "quiz_passed": progress_dict.get(module_id, {}).get("passed") if module_id in progress_dict else None,
                "completion_date": completion_date,
                "blocks": blocks_response.data if blocks_response.data else [],
                "questions": questions_with_answers
            }
            
            modules_with_progress.append(module_dict)
        
        return ApiResponse(success=True, data=modules_with_progress)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course modules: {str(e)}"
        )


@router.post("/modules/{module_id}/quiz", response_model=ApiResponse)
async def submit_quiz(
    module_id: int,
    quiz_data: QuizSubmission,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Submit quiz answers and get results with detailed feedback.
    """
    try:       
        user_response = db.table("users").select("*").eq("id", current_user.id).execute()
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in the database"
            )
        
        module_response = db.table("modules").select("*").eq("id", module_id).execute()
        if not module_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        questions_response = db.table("questions").select("*").eq("module_id", module_id).execute()
        if not questions_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No questions found for this module"
            )
        
        total_questions = len(questions_response.data)
        correct_answers = 0
        answer_results = []
        
        for answer_data in quiz_data.answers:            
            extracted_data = extract_answer_data(answer_data)
            question_id = extracted_data["question_id"]
            answer_text = extracted_data["answer_text"]
                        
            if not question_id:
                print(f"Missing question_id for answer: {answer_data}")
                continue
                
            question = next((q for q in questions_response.data if q["id"] == question_id), None)
            if not question:
                print(f"Question not found for ID: {question_id}")
                continue
                
            correct_answers_response = db.table("answers").select("*").eq("question_id", question_id).eq("is_correct", True).execute()
            
            evaluation = evaluate_quiz_answer(
                question, 
                answer_text, 
                correct_answers_response.data if correct_answers_response.data else []
            )
            
            is_correct = evaluation["is_correct"]
            correct_answer_text = evaluation["correct_answer_text"]
            feedback = evaluation["feedback"]
            
            if is_correct:
                correct_answers += 1
            
            user_answer = {
                "user_id": current_user.id,
                "question_id": question_id,
                "answer_text": answer_text,
                "is_correct": is_correct,
                "submitted_at": get_current_time()
            }
            
            try:
                insert_response = db.table("user_answers").insert(user_answer).execute()
            except Exception as insert_error:
                print(f"Warning: Could not save user answer: {str(insert_error)}")
                # Continue processing without failing the whole quiz submission
            
            answer_results.append({
                "question_id": question_id,
                "answer_text": answer_text,
                "is_correct": is_correct,
                "correct_answer": correct_answer_text,
                "feedback": feedback
            })
        
        score = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        passed = score >= 70  # 70% passing grade
        
        overall_feedback = generate_quiz_feedback(score)
        
        try:
            progress_response = db.table("progress").select("*").eq("user_id", current_user.id).eq("module_id", module_id).execute()
            
            if progress_response.data:
                update_data = {
                    "score": score,
                    "passed": passed,
                    "completed_at": get_current_time() if passed else None  # Only set completion time if passed
                }
                db.table("progress").update(update_data).eq("user_id", current_user.id).eq("module_id", module_id).execute()
            else:
                progress_data = {
                    "user_id": current_user.id,
                    "module_id": module_id,
                    "score": score,
                    "passed": passed,
                    "completed_at": get_current_time() if passed else None  # Only set completion time if passed
                }
                db.table("progress").insert(progress_data).execute()
        except Exception as progress_error:
            print(f"Warning: Could not update progress: {str(progress_error)}")
        
        quiz_result = QuizResult(
            module_id=module_id,
            score=score,
            passed=passed,
            completion_date=get_current_time() if passed else None,
            answers=answer_results,
            feedback=overall_feedback
        )
        
        return ApiResponse(success=True, data=quiz_result.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting quiz: {str(e)}")
        print(f"Quiz data: {quiz_data}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit quiz: {str(e)}"
        )


@router.get("/certificate", response_model=ApiResponse)
async def get_certificate(
    user_id: str,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get user's certificate if course is completed.
    """
    try:
        modules_response = db.table("modules").select("id").execute()
        total_modules = len(modules_response.data) if modules_response.data else 0
        
        progress_response = db.table("progress").select("*").eq("user_id", user_id).eq("passed", True).execute()
        completed_modules = len(progress_response.data) if progress_response.data else 0
        
        if completed_modules < total_modules:
            return ApiResponse(success=True, data=None, message="Course not completed yet")
        
        cert_response = db.table("certificates").select("*").eq("user_id", user_id).execute()
        
        if cert_response.data:
            certificate = cert_response.data[0]
        else:
            certificate_data = {
                "user_id": user_id,
                "certificate_url": f"/api/course/certificate/download?user_id={user_id}",
                "issued_at": get_current_time()
            }
            
            cert_insert_response = db.table("certificates").insert(certificate_data).execute()
            certificate = cert_insert_response.data[0] if cert_insert_response.data else certificate_data
        
        return ApiResponse(success=True, data=certificate)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get certificate: {str(e)}"
        )


@router.get("/certificate/download")
async def download_certificate(
    user_id: str,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Download certificate as PDF.
    """
    try:
        cert_response = db.table("certificates").select("*").eq("user_id", user_id).execute()
        
        if not cert_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found"
            )
        
        user_response = db.table("users").select("full_name, email").eq("id", user_id).execute()
        user_name = user_response.data[0]["full_name"] if user_response.data else "Student"
        
        certificate_content = generate_certificate_content(user_name, cert_response.data[0])
        
        return prepare_certificate_response(user_id, certificate_content)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download certificate: {str(e)}"
        )
