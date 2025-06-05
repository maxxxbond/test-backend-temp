from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Any, Union, Dict
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDB(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None


class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: Optional[str] = None


class VideoCreate(VideoBase):
    pass


class VideoUpdate(VideoBase):
    title: Optional[str] = None


class VideoInDB(VideoBase):
    id: str
    url: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: str
    
    class Config:
        from_attributes = True


class Video(VideoInDB):
    pass


# New schemas for course dashboard functionality

class ModuleBlockBase(BaseModel):
    module_id: int
    order: int
    type: str = Field(..., pattern="^(text|video|image|quiz_intro|code)$")
    content: Any  # JSONB content


class ModuleBlockCreate(ModuleBlockBase):
    pass


class ModuleBlockUpdate(ModuleBlockBase):
    module_id: Optional[int] = None
    order: Optional[int] = None
    type: Optional[str] = None
    content: Optional[Any] = None


class ModuleBlockInDB(ModuleBlockBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ModuleBlock(ModuleBlockInDB):
    pass


class AnswerBase(BaseModel):
    question_id: int
    answer_text: str
    is_correct: bool


class AnswerCreate(AnswerBase):
    pass


class AnswerInDB(AnswerBase):
    id: int
    
    class Config:
        from_attributes = True


class Answer(AnswerInDB):
    pass


class QuestionBase(BaseModel):
    module_id: int
    question_text: str
    type: str = Field(..., pattern="^(single|multi|text|number)$")
    tolerance: Optional[int] = None
    exact_match: Optional[bool] = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(QuestionBase):
    module_id: Optional[int] = None
    question_text: Optional[str] = None
    type: Optional[str] = None


class QuestionInDB(QuestionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Question(QuestionInDB):
    answers: Optional[List[Answer]] = []


class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int
    slug: str


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(ModuleBase):
    title: Optional[str] = None
    order: Optional[int] = None
    slug: Optional[str] = None


class ModuleInDB(ModuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Module(ModuleInDB):
    status: str = "locked"  # completed, available, locked
    score: Optional[int] = None
    quiz_passed: Optional[bool] = None
    completion_date: Optional[str] = None
    blocks: Optional[List[ModuleBlock]] = []
    questions: Optional[List[Question]] = []


class UserAnswerBase(BaseModel):
    user_id: str
    question_id: int
    answer_text: str
    is_correct: Optional[bool] = None


class UserAnswerCreate(UserAnswerBase):
    pass


class UserAnswerInDB(UserAnswerBase):
    id: int
    submitted_at: datetime
    
    class Config:
        from_attributes = True


class UserAnswer(UserAnswerInDB):
    pass


class ProgressBase(BaseModel):
    user_id: str
    module_id: int
    score: Optional[int] = None
    passed: bool = False


class ProgressCreate(ProgressBase):
    pass


class ProgressUpdate(ProgressBase):
    user_id: Optional[str] = None
    module_id: Optional[int] = None


class ProgressInDB(ProgressBase):
    id: int
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Progress(ProgressInDB):
    pass


class CourseProgress(BaseModel):
    user_id: str
    completed_modules: int
    total_modules: int
    last_activity: str
    highest_score: dict
    is_completed: bool
    has_started: bool


class AnswerSubmission(BaseModel):
    question_id: int
    answer_text: str

class QuizSubmission(BaseModel):
    answers: List[Union[Dict[str, Any], AnswerSubmission]]


class UserAnswerResult(BaseModel):
    question_id: int
    answer_text: str
    is_correct: bool
    correct_answer: Optional[str] = None
    feedback: Optional[str] = None


class QuizResult(BaseModel):
    module_id: int
    score: int
    passed: bool
    completion_date: Optional[str] = None
    answers: Optional[List[Dict[str, Any]]] = None
    feedback: Optional[str] = None


class CertificateBase(BaseModel):
    user_id: str
    certificate_url: Optional[str] = None


class CertificateCreate(CertificateBase):
    pass


class CertificateInDB(CertificateBase):
    id: int
    issued_at: datetime
    
    class Config:
        from_attributes = True


class Certificate(CertificateInDB):
    pass


# API Response wrapper
class ApiResponse(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None
    error: Optional[str] = None
