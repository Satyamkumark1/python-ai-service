"""
Configuration settings for the PM Internship AI Recommendation API
"""
import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # Spring Boot API Configuration
    SPRING_BOOT_BASE_URL: str = os.getenv('SPRING_BOOT_BASE_URL', 'http://localhost:8080')
    INTERNSHIPS_ENDPOINT: str = os.getenv('INTERNSHIPS_ENDPOINT', '/api/internships')
    STUDENTS_ENDPOINT: str = os.getenv('STUDENTS_ENDPOINT', '/api/students')
    RECOMMENDATIONS_CALLBACK_ENDPOINT: str = os.getenv('RECOMMENDATIONS_CALLBACK_ENDPOINT', '/api/recommendations/callback')
    FEEDBACK_CALLBACK_ENDPOINT: str = os.getenv('FEEDBACK_CALLBACK_ENDPOINT', '/api/feedback/callback')
    API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', '30'))
    
    # Optional: API Authentication
    SPRING_BOOT_API_KEY: Optional[str] = os.getenv('SPRING_BOOT_API_KEY')
    
    # Application Configuration
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Model Configuration
    MODEL_PATH: str = os.getenv('MODEL_PATH', 'trained_models/recommendation_model.joblib')
    MODEL_VERSION: str = os.getenv('MODEL_VERSION', 'v1.0')
    
    @classmethod
    def get_api_url(cls, endpoint: str) -> str:
        """Get full API URL for an endpoint"""
        return f"{cls.SPRING_BOOT_BASE_URL}{endpoint}"
    
    @classmethod
    def get_internships_url(cls) -> str:
        """Get full URL for internships endpoint"""
        return cls.get_api_url(cls.INTERNSHIPS_ENDPOINT)
    
    @classmethod
    def get_students_url(cls) -> str:
        """Get full URL for students endpoint"""
        return cls.get_api_url(cls.STUDENTS_ENDPOINT)
    
    @classmethod
    def get_student_url(cls, student_id: int) -> str:
        """Get full URL for a specific student"""
        return f"{cls.get_students_url()}/{student_id}"
    
    @classmethod
    def get_internship_url(cls, internship_id: int) -> str:
        """Get full URL for a specific internship"""
        return f"{cls.get_internships_url()}/{internship_id}"
    
    @classmethod
    def get_recommendations_callback_url(cls) -> str:
        """Get full URL for recommendations callback endpoint"""
        return cls.get_api_url(cls.RECOMMENDATIONS_CALLBACK_ENDPOINT)
    
    @classmethod
    def get_feedback_callback_url(cls) -> str:
        """Get full URL for feedback callback endpoint"""
        return cls.get_api_url(cls.FEEDBACK_CALLBACK_ENDPOINT)
