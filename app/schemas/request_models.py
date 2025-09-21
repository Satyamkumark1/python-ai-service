from pydantic import BaseModel, Field
from typing import List, Optional

class StudentRequest(BaseModel):
    """Request model for student data"""
    student_id: int = Field(..., description="Unique student identifier")
    education_level: str = Field(..., description="Student's education level", example="B.Tech")
    skills: List[str] = Field(..., description="List of student skills", example=["Java", "Python"])
    interests: List[str] = Field(..., description="List of student interests", example=["Software Development", "AI"])
    preferred_location: Optional[str] = Field(None, description="Preferred internship location", example="Bhubaneswar")
    preferred_state: Optional[str] = Field(None, description="Preferred internship state", example="Odisha")
    is_first_gen_learner: bool = Field(False, description="First-generation learner status")
    request_id: Optional[str] = Field(None, description="Optional request ID for tracking")
    send_callback: bool = Field(True, description="Whether to send callback to Spring Boot")

class FeedbackRequest(BaseModel):
    """Request model for recommendation feedback"""
    student_id: int = Field(..., description="Student identifier")
    internship_id: int = Field(..., description="Internship identifier")
    feedback: str = Field(..., description="Feedback type", example="LIKE/DISLIKE")
    comments: Optional[str] = Field(None, description="Additional comments")
    request_id: Optional[str] = Field(None, description="Optional request ID for tracking")
    send_callback: bool = Field(True, description="Whether to send callback to Spring Boot")

class RetrainRequest(BaseModel):
    """Request model for model retraining"""
    force_retrain: bool = Field(False, description="Force retrain even if model exists")
    request_id: Optional[str] = Field(None, description="Optional request ID for tracking")
    send_callback: bool = Field(True, description="Whether to send callback to Spring Boot")

class ResumeAnalyzeRequest(BaseModel):
    """Request model for resume analysis"""
    resume_text: str = Field(..., description="Full resume text content to analyze")
    skills: Optional[List[str]] = Field(None, description="Detected or provided skills list")
    interests: Optional[List[str]] = Field(None, description="Detected or provided interests list")
    education_level: Optional[str] = Field(None, description="Education level string")
    college_name: Optional[str] = Field(None, description="College or university name")
    target_role: Optional[str] = Field(None, description="Optional target role to tailor suggestions")