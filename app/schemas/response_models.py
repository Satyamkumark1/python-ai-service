from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RecommendationScore(BaseModel):
    """Individual recommendation score"""
    internship_id: int
    score: float
    reason: str
    title: str
    organization: str
    location: str

class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    recommendations: List[RecommendationScore]
    model_version: str = "v1.0"
    generated_at: str
    total_recommendations: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    model_loaded: bool
    internships_count: int
    timestamp: str

class ModelInfoResponse(BaseModel):
    """Model information response"""
    internships_count: int
    feature_dimension: int
    model_version: str
    last_trained: Optional[str] = None

class TrainingResponse(BaseModel):
    """Training response"""
    success: bool
    message: str
    internships_count: int
    training_time_seconds: float

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: str

class FeedbackResponse(BaseModel):
    """Feedback success response"""
    message: str